# Copyright 2026 QuantumBridge Contributors.
# Licensed under the Apache License, Version 2.0.
"""Independent mixed-radix local linear maps, not upstream implementation tests."""

from itertools import product
from math import prod
import gc

import numpy as np
import pytest

from quantumbridge.execution import UnifiedResourceLedger as Ledger, UnifiedExecutionLimits as Limits
from quantumbridge.execution.resource_context import ResourceScope
from quantumbridge.information import DensityMatrix, Operator, Statevector


CASES = [((2, 4), (1,)), ((3, 2), (0,)), ((2, 3, 2), (0, 2)),
         ((2, 3, 2), (2, 0)), ((2, 3, 2), (1, 2)),
         ((2, 3, 2), (2, 1)), ((6,), (0,)), ((2, 2, 2), (2, 0))]


def vector(dims):
    values = np.arange(1, prod(dims) + 1) + 1j * np.arange(prod(dims), 0, -1)
    return values / np.linalg.norm(values)


def local_matrix(size, kind="fourier", rows=None):
    rows = size if rows is None else rows
    matrix = np.exp(2j * np.pi * np.outer(np.arange(rows), np.arange(size)) / max(rows, size)) / np.sqrt(size)
    if kind == "nonunitary":
        matrix[0] *= .2 + .3j
        matrix[-1] *= 1.3 - .4j
    return matrix


def reference_map(dims, selected, matrix, outgoing=None):
    incoming = tuple(dims[position] for position in selected)
    outgoing = incoming if outgoing is None else outgoing
    result_dims = list(dims)
    for position, size in zip(selected, outgoing):
        result_dims[position] = size
    result_dims = tuple(result_dims)
    embedded = np.zeros((prod(result_dims), prod(dims)), complex)
    for row, column in product(range(prod(result_dims)), range(prod(dims))):
        left = np.unravel_index(row, result_dims)
        right = np.unravel_index(column, dims)
        if any(left[position] != right[position] for position in range(len(dims)) if position not in selected):
            continue
        local_row = np.ravel_multi_index(tuple(left[position] for position in selected), outgoing)
        local_col = np.ravel_multi_index(tuple(right[position] for position in selected), incoming)
        embedded[row, column] = matrix[local_row, local_col]
    return embedded, result_dims


@pytest.mark.parametrize("cls", [Statevector, DensityMatrix])
@pytest.mark.parametrize("managed", [False, True])
@pytest.mark.parametrize("dims,selected", CASES)
@pytest.mark.parametrize("kind", ["fourier", "nonunitary"])
def test_native_local_numeric_map_matches_independent_complex_math(cls, managed, dims, selected, kind):
    values = vector(dims)
    data = values if cls is Statevector else .7 * np.outer(values, values.conj()) + .3 * np.diag(abs(values)**2)
    state = cls(data, dims=dims)
    matrix = local_matrix(prod(dims[position] for position in selected), kind)
    embedded, output_dims = reference_map(dims, selected, matrix)
    expected = embedded @ data if cls is Statevector else embedded @ data @ embedded.conj().T
    before = state.data.copy()
    ledger = Ledger()
    if managed:
        with ResourceScope(ledger):
            actual = state.evolve(matrix, qargs=selected)
    else:
        actual = state.evolve(matrix, qargs=selected)
    np.testing.assert_allclose(actual.data, expected, atol=3e-14, rtol=0)
    assert actual.dims() == output_dims
    np.testing.assert_array_equal(state.data, before)
    if managed:
        assert ledger.receipt()["live_memory_bytes"] == actual.data.nbytes
    if cls is DensityMatrix:
        np.testing.assert_allclose(actual.data, actual.data.conj().T, atol=2e-14)
        assert np.linalg.eigvalsh(actual.data).min() > -3e-14
        assert actual.trace() == pytest.approx(np.trace(expected))


@pytest.mark.parametrize("incoming,outgoing", [((4,), (4,)), ((3,), (3,)), ((3,), (4,)), ((2, 2), (3, 2)), ((), ())])
def test_native_operator_declares_actual_input_output_dimensions(incoming, outgoing):
    data = local_matrix(prod(incoming), rows=prod(outgoing))
    ledger = Ledger()
    with ResourceScope(ledger):
        operator = Operator(data, input_dims=incoming, output_dims=outgoing)
    np.testing.assert_array_equal(operator.data, data)
    assert operator.input_dims() == incoming and operator.output_dims() == outgoing
    assert operator.dim == (prod(incoming), prod(outgoing))
    assert operator.num_qubits == (len(incoming) if incoming == outgoing and all(size == 2 for size in incoming) else None)


@pytest.mark.parametrize("method", ["copy", "conjugate", "transpose", "adjoint", "scale", "tensor", "reverse"])
def test_existing_operator_operations_preserve_numbers_and_real_qudit_partition(method):
    data = local_matrix(4, "nonunitary")
    operator = Operator(data, input_dims=(4,), output_dims=(4,))
    if method == "scale":
        actual, expected, dims = operator * (.2 + .7j), data * (.2 + .7j), (4,)
    elif method == "tensor":
        actual = operator.tensor(Operator.from_label("X"))
        expected, dims = np.kron(data, np.array([[0, 1], [1, 0]])), (4, 2)
    elif method == "reverse":
        actual, expected, dims = operator.reverse_qargs(), data, (4,)
    else:
        actual = getattr(operator, method)()
        expected = data.conj() if method == "conjugate" else data.T if method == "transpose" else data.conj().T if method == "adjoint" else data
        dims = (4,)
    np.testing.assert_allclose(actual.data, expected, atol=1e-15)
    assert actual.input_dims() == actual.output_dims() == dims


@pytest.mark.parametrize("cls", [Statevector, DensityMatrix])
@pytest.mark.parametrize("selected", [[0, 0], [-1], [3], [True], [0.0]])
def test_native_invalid_local_targets_are_rejected_before_operator_factory(cls, selected, monkeypatch):
    values = vector((2, 3, 2))
    state = cls(values if cls is Statevector else np.outer(values, values.conj()), dims=(2, 3, 2))
    matrix = local_matrix(4 if len(selected) == 2 else 2)
    monkeypatch.setattr(np, "empty", lambda *a, **k: pytest.fail("Invalid qargs reached a numeric factory"))
    with ResourceScope(Ledger()), pytest.raises(ValueError):
        state.evolve(matrix, qargs=selected)


@pytest.mark.parametrize("name", ["Kraus", "SuperOp", "Choi", "PTM", "Chi", "Stinespring"])
@pytest.mark.parametrize("managed", [False, True])
@pytest.mark.parametrize("incoming,outgoing", [((4,), (4,)), ((2, 2), (3, 2))])
def test_new_typed_operator_does_not_silently_lose_partition_in_unextended_channel(name, managed, incoming, outgoing):
    import quantumbridge.information as info
    from quantumbridge.core.classical import UnsupportedFeature
    operator = Operator(local_matrix(prod(incoming), rows=prod(outgoing)), input_dims=incoming, output_dims=outgoing)
    if managed:
        with ResourceScope(Ledger()), pytest.raises(UnsupportedFeature):
            getattr(info, name)(operator)
    else:
        with pytest.raises(UnsupportedFeature):
            getattr(info, name)(operator)


@pytest.mark.parametrize("cls", [Statevector, DensityMatrix])
def test_managed_foreign_operator_subclass_does_not_dispatch_dimension_protocol(cls):
    from quantumbridge.core.classical import UnsupportedFeature
    class Foreign(Operator):
        def input_dims(self, *args):
            pytest.fail("Foreign dimension protocol was dispatched")
    foreign = object.__new__(Foreign)
    state = cls.from_int(0, (3, 2))
    with ResourceScope(Ledger()), pytest.raises(UnsupportedFeature):
        state.evolve(foreign)


@pytest.mark.parametrize("name", ["Kraus", "SuperOp", "Choi", "PTM", "Chi", "Stinespring"])
def test_managed_channel_guard_does_not_read_foreign_operator_metadata(name):
    import quantumbridge.information as info
    from quantumbridge.core.classical import UnsupportedFeature
    class Foreign(Operator):
        @property
        def num_qubits(self):
            pytest.fail("Foreign channel metadata protocol was dispatched")
    foreign = object.__new__(Foreign)
    with ResourceScope(Ledger()), pytest.raises(UnsupportedFeature):
        getattr(info, name)(foreign)


@pytest.mark.parametrize("cls", [Statevector, DensityMatrix])
@pytest.mark.parametrize("managed", [False, True])
@pytest.mark.parametrize("dims,selected", CASES[2:6])
def test_strided_native_state_and_typed_operator_do_not_expand_or_reshape(cls, managed, dims, selected, monkeypatch):
    import quantumbridge.information.operator as operator_module
    values = vector(dims)
    data = values if cls is Statevector else np.outer(values, values.conj())
    backing = np.zeros(tuple(2 * size for size in data.shape), complex)
    view = backing[::2] if cls is Statevector else backing[::2, ::2]
    view[...] = data
    state = cls(view, dims=dims)
    incoming = tuple(dims[position] for position in selected)
    matrix = local_matrix(prod(incoming), "nonunitary")[::-1, ::-1]
    operator = Operator(matrix, input_dims=incoming, output_dims=incoming)
    embedded, _ = reference_map(dims, selected, matrix)
    expected = embedded @ data if cls is Statevector else embedded @ data @ embedded.conj().T
    def forbidden(*args, **kwargs):
        pytest.fail("Local mixed-radix execution expanded or reshaped an unmetered array")
    monkeypatch.setattr(operator_module, "_expand_subsystem_operator", forbidden)
    for name in ("kron", "eye", "reshape"):
        monkeypatch.setattr(np, name, forbidden)
    ledger = Ledger()
    if managed:
        with ResourceScope(ledger):
            actual = state.evolve(operator, qargs=selected)
    else:
        actual = state.evolve(operator, qargs=selected)
    np.testing.assert_allclose(actual.data, expected, atol=3e-14, rtol=0)
    assert actual.dims() == dims
    np.testing.assert_array_equal(view, data)
    if managed:
        assert ledger.receipt()["live_memory_bytes"] == actual.data.nbytes


@pytest.mark.parametrize("dims,selected", CASES[:7])
def test_state_and_density_local_action_are_consistent_with_complex_pure_states(dims, selected):
    values = vector(dims)
    matrix = local_matrix(prod(dims[position] for position in selected), "nonunitary")
    with ResourceScope(Ledger()):
        state = Statevector(values, dims=dims).evolve(matrix, qargs=selected)
        density = DensityMatrix.from_statevector(Statevector(values, dims=dims)).evolve(matrix, qargs=selected)
    np.testing.assert_allclose(density.data, np.outer(state.data, state.data.conj()), atol=3e-14)
    assert state.dims() == density.dims() == dims
    assert density.trace() == pytest.approx(np.vdot(state.data, state.data))


@pytest.mark.parametrize("cls", [Statevector, DensityMatrix])
@pytest.mark.parametrize("kind", ["raw", "typed", "list"])
def test_mapped_outputs_and_known_group_are_denied_before_first_factory_or_core(cls, kind, monkeypatch):
    dims, selected = (2, 3, 2), (2, 0)
    values = vector(dims)
    state = cls(values if cls is Statevector else np.outer(values, values.conj()), dims=dims)
    matrix = local_matrix(4)
    operator = Operator(matrix, input_dims=(2, 2), output_dims=(2, 2)) if kind == "typed" else matrix.tolist() if kind == "list" else matrix
    amount = (12 if cls is Statevector else 12 * 12 * 2 + 12) * 16 + (0 if kind == "raw" else 4 * 4 * 16)
    def forbidden(*args, **kwargs):
        pytest.fail("Mapped output group preceded admission")
    for name in ("empty", "array", "multiply", "add", "matmul", "kron"):
        monkeypatch.setattr(np, name, forbidden)
    ledger = Ledger(Limits(max_total_memory_bytes=amount - 1))
    with ResourceScope(ledger), pytest.raises(MemoryError):
        state.evolve(operator, qargs=selected)
    assert ledger.receipt()["live_memory_bytes"] == 0


@pytest.mark.parametrize("cls", [Statevector, DensityMatrix])
def test_mapped_result_view_holds_lease_and_valid_overbudget_valid_recovers(cls):
    dims, selected = (2, 3, 2), (2, 0)
    values = vector(dims)
    state = cls(values if cls is Statevector else np.outer(values, values.conj()), dims=dims)
    matrix = local_matrix(4)
    amount = (12 if cls is Statevector else 12 * 12 * 2 + 12) * 16
    ledger = Ledger(Limits(max_total_memory_bytes=amount))
    with ResourceScope(ledger):
        first = state.evolve(matrix, qargs=selected)
        assert ledger.receipt()["peak_memory_bytes"] == amount
        expected = first.data.copy()
        view = first.data[::2]
        size = first.data.nbytes
        del first
        gc.collect()
        assert ledger.receipt()["live_memory_bytes"] == size
        with pytest.raises(MemoryError):
            state.evolve(matrix, qargs=selected)
        assert ledger.receipt()["live_memory_bytes"] == size
        del view
        gc.collect()
        assert ledger.receipt()["live_memory_bytes"] == 0
        recovered = state.evolve(matrix, qargs=selected)
        np.testing.assert_allclose(recovered.data, expected, atol=1e-15)
    del recovered
    gc.collect()
    assert ledger.receipt()["live_memory_bytes"] == 0


@pytest.mark.parametrize("dims,selected,outgoing", [((2, 4), (1,), (5,)), ((3, 2), (0,), (2,)), ((3, 2), (0,), (4,)),
                                                    ((2, 3, 2), (0, 2), (3, 2)), ((2, 3, 2), (2, 0), (3, 2))])
def test_rectangular_local_density_evolution_changes_actual_selected_dimensions(dims, selected, outgoing):
    values = vector(dims)
    incoming = tuple(dims[position] for position in selected)
    matrix = local_matrix(prod(incoming), "nonunitary", rows=prod(outgoing))
    operator = Operator(matrix, input_dims=incoming, output_dims=outgoing)
    data = .7 * np.outer(values, values.conj()) + .3 * np.diag(abs(values)**2)
    embedded, result_dims = reference_map(dims, selected, matrix, outgoing)
    expected = embedded @ data @ embedded.conj().T
    ledger = Ledger()
    with ResourceScope(ledger):
        actual = DensityMatrix(data, dims=dims).evolve(operator, qargs=selected)
    np.testing.assert_allclose(actual.data, expected, atol=3e-14, rtol=0)
    assert actual.dims() == result_dims
    assert actual.num_qubits == (len(result_dims) if all(size == 2 for size in result_dims) else None)
    assert actual.trace() == pytest.approx(np.trace(expected))
    assert np.linalg.eigvalsh(actual.data).min() > -3e-14
    assert ledger.receipt()["live_memory_bytes"] == actual.data.nbytes


@pytest.mark.parametrize("cls", [Statevector, DensityMatrix])
@pytest.mark.parametrize("incoming,outgoing", [((3,), (4,)), ((2, 2), (3, 2)), ((3, 2), (3, 3)), ((3, 2), (9,)), ((2, 3, 2), (3, 2))])
def test_full_rectangular_typed_operator_updates_all_output_subsystems(cls, incoming, outgoing):
    values = vector(incoming)
    data = values if cls is Statevector else np.outer(values, values.conj())
    matrix = local_matrix(prod(incoming), "nonunitary", rows=prod(outgoing))
    operator = Operator(matrix, input_dims=incoming, output_dims=outgoing)
    expected = matrix @ data if cls is Statevector else matrix @ data @ matrix.conj().T
    with ResourceScope(Ledger()):
        actual = cls(data, dims=incoming).evolve(operator)
    np.testing.assert_allclose(actual.data, expected, atol=3e-14, rtol=0)
    assert actual.dims() == outgoing


def test_mapped_rectangular_statevector_and_output_subsystem_insertion_remain_explicitly_unsupported(monkeypatch):
    from quantumbridge.core.classical import UnsupportedFeature
    state = Statevector(vector((3, 2)), dims=(3, 2))
    rectangular = Operator(local_matrix(3, rows=4), input_dims=(3,), output_dims=(4,))
    insertion = Operator(np.eye(6), input_dims=(3, 2), output_dims=(6,))
    monkeypatch.setattr(np, "empty", lambda *a, **k: pytest.fail("Unsupported dimensions reached a factory"))
    with ResourceScope(Ledger()):
        with pytest.raises(UnsupportedFeature):
            state.evolve(rectangular, qargs=[0])
        with pytest.raises(UnsupportedFeature):
            state.evolve(insertion, qargs=[0, 1])


@pytest.mark.parametrize("dims", [(2, 4), (3, 2)])
def test_native_composition_runs_basis_tensor_mapped_evolve_density_trace_probabilities(dims):
    state = Statevector.from_int(1, dims).tensor(Statevector.from_label("+"))
    full_dims = dims + (2,)
    selected = (0, 2)
    incoming = (dims[0], 2)
    matrix = local_matrix(prod(incoming))
    embedded, _ = reference_map(full_dims, selected, matrix)
    evolved = embedded @ state.data
    expected = np.outer(evolved, evolved.conj()).reshape(full_dims + full_dims)
    expected = np.trace(expected, axis1=1, axis2=4).reshape(prod(incoming), prod(incoming))
    with ResourceScope(Ledger()):
        reduced = state.evolve(Operator(matrix, input_dims=incoming, output_dims=incoming), qargs=selected).to_density_matrix().partial_trace(selected)
    np.testing.assert_allclose(reduced.data, expected, atol=3e-14)
    assert reduced.dims() == incoming
    assert sum(reduced.probabilities().values()) == pytest.approx(1.)


@pytest.mark.parametrize("cls", [Statevector, DensityMatrix])
@pytest.mark.parametrize("dims,selected", CASES[:7])
def test_optional_public_square_local_oracle_uses_explicit_native_order_mapping(cls, dims, selected):
    info = pytest.importorskip("qiskit.quantum_info")
    values = vector(dims)
    data = values if cls is Statevector else np.outer(values, values.conj())
    incoming = tuple(dims[position] for position in selected)
    matrix = local_matrix(prod(incoming), "nonunitary")
    public_cls = info.Statevector if cls is Statevector else info.DensityMatrix
    reference = public_cls(data, dims=dims[::-1]).evolve(
        info.Operator(matrix, input_dims=incoming[::-1], output_dims=incoming[::-1]),
        qargs=[len(dims) - 1 - position for position in reversed(selected)])
    with ResourceScope(Ledger()):
        actual = cls(data, dims=dims).evolve(Operator(matrix, input_dims=incoming, output_dims=incoming), qargs=selected)
    np.testing.assert_allclose(actual.data, reference.data, atol=3e-14, rtol=0)
    assert actual.dims() == reference.dims()[::-1]


@pytest.mark.parametrize("dims,selected,outgoing", [((2, 4), (1,), (5,)), ((3, 2), (0,), (2,)), ((3, 2), (0,), (4,)),
                                                    ((2, 3, 2), (0, 2), (3, 2)), ((2, 3, 2), (2, 0), (3, 2))])
def test_optional_public_rectangular_density_local_oracle(dims, selected, outgoing):
    info = pytest.importorskip("qiskit.quantum_info")
    incoming = tuple(dims[position] for position in selected)
    values = vector(dims)
    data = np.outer(values, values.conj())
    matrix = local_matrix(prod(incoming), rows=prod(outgoing))
    reference = info.DensityMatrix(data, dims=dims[::-1]).evolve(
        info.Operator(matrix, input_dims=incoming[::-1], output_dims=outgoing[::-1]),
        qargs=[len(dims) - 1 - position for position in reversed(selected)])
    with ResourceScope(Ledger()):
        actual = DensityMatrix(data, dims=dims).evolve(Operator(matrix, input_dims=incoming, output_dims=outgoing), qargs=selected)
    np.testing.assert_allclose(actual.data, reference.data, atol=3e-14)
    assert actual.dims() == reference.dims()[::-1]


@pytest.mark.parametrize("cls", [Statevector, DensityMatrix])
@pytest.mark.parametrize("managed", [False, True])
@pytest.mark.parametrize("dims,selected,outgoing", [((2, 4), (0, 1), (4, 2)),
                                                    ((2, 3, 2), (1, 2), (2, 3)),
                                                    ((2, 3, 2), (2, 1), (3, 2))])
def test_square_local_map_with_repartitioned_output_dimensions_has_correct_actual_indices(cls, managed, dims, selected, outgoing):
    values = vector(dims)
    data = values if cls is Statevector else np.outer(values, values.conj())
    incoming = tuple(dims[position] for position in selected)
    matrix = local_matrix(prod(incoming), "nonunitary")
    embedded, result_dims = reference_map(dims, selected, matrix, outgoing)
    expected = embedded @ data if cls is Statevector else embedded @ data @ embedded.conj().T
    operator = Operator(matrix, input_dims=incoming, output_dims=outgoing)
    state = cls(data, dims=dims)
    if managed:
        with ResourceScope(Ledger()):
            actual = state.evolve(operator, qargs=selected)
    else:
        actual = state.evolve(operator, qargs=selected)
    np.testing.assert_allclose(actual.data, expected, atol=3e-14)
    assert actual.dims() == result_dims


@pytest.mark.parametrize("cls", [Statevector, DensityMatrix])
@pytest.mark.parametrize("incoming,outgoing", [((3,), (4,)), ((2, 2), (3, 2)), ((3, 2), (3, 3)), ((3, 2), (9,)), ((2, 3, 2), (3, 2))])
def test_optional_public_full_rectangular_typed_oracle(cls, incoming, outgoing):
    info = pytest.importorskip("qiskit.quantum_info")
    values = vector(incoming)
    data = values if cls is Statevector else np.outer(values, values.conj())
    matrix = local_matrix(prod(incoming), "nonunitary", rows=prod(outgoing))
    public_cls = info.Statevector if cls is Statevector else info.DensityMatrix
    reference = public_cls(data, dims=incoming[::-1]).evolve(
        info.Operator(matrix, input_dims=incoming[::-1], output_dims=outgoing[::-1]))
    with ResourceScope(Ledger()):
        actual = cls(data, dims=incoming).evolve(Operator(matrix, input_dims=incoming, output_dims=outgoing))
    np.testing.assert_allclose(actual.data, reference.data, atol=3e-14)
    assert actual.dims() == reference.dims()[::-1]


@pytest.mark.parametrize("method", ["copy", "conjugate", "transpose", "adjoint", "tensor", "expand", "reverse", "reshape"])
def test_rectangular_operator_existing_operations_keep_both_sides_and_values(method):
    incoming, outgoing = (3, 2), (3, 3)
    data = local_matrix(6, rows=9)
    operator = Operator(data, input_dims=incoming, output_dims=outgoing)
    with ResourceScope(Ledger()):
        if method in {"tensor", "expand"}:
            actual = getattr(operator, method)(Operator.from_label("X"))
            expected = np.kron(data, [[0, 1], [1, 0]]) if method == "tensor" else np.kron([[0, 1], [1, 0]], data)
            left, right = (incoming + (2,), outgoing + (2,)) if method == "tensor" else ((2,) + incoming, (2,) + outgoing)
        elif method == "reverse":
            actual = operator.reverse_qargs()
            rows = [np.ravel_multi_index(np.unravel_index(index, outgoing)[::-1], outgoing[::-1]) for index in range(9)]
            columns = [np.ravel_multi_index(np.unravel_index(index, incoming)[::-1], incoming[::-1]) for index in range(6)]
            expected = np.empty_like(data)
            expected[np.ix_(rows, columns)] = data
            left, right = incoming[::-1], outgoing[::-1]
        elif method == "reshape":
            actual = operator.reshape(input_dims=(6,), output_dims=(9,))
            expected, left, right = data, (6,), (9,)
        else:
            actual = getattr(operator, method)()
            expected = data.conj() if method == "conjugate" else data.T if method == "transpose" else data.conj().T if method == "adjoint" else data
            left, right = (outgoing, incoming) if method in {"transpose", "adjoint"} else (incoming, outgoing)
    np.testing.assert_allclose(actual.data, expected, atol=1e-15)
    assert actual.input_dims() == left and actual.output_dims() == right


def test_reversed_local_targets_are_not_silently_sorted():
    state = Statevector(vector((2, 3, 2)), dims=(2, 3, 2))
    matrix = local_matrix(4, "nonunitary")
    first = state.evolve(matrix, qargs=[0, 2])
    second = state.evolve(matrix, qargs=[2, 0])
    assert not np.allclose(first.data, second.data)
    for selected, actual in (((0, 2), first), ((2, 0), second)):
        expected, _ = reference_map(state.dims(), selected, matrix)
        np.testing.assert_allclose(actual.data, expected @ state.data, atol=3e-14)


@pytest.mark.parametrize("local", [False, True])
def test_rectangular_strided_density_group_quota_view_and_recovery(local, monkeypatch):
    dims = (2, 3, 2) if local else (2, 2)
    selected = (2, 0) if local else None
    incoming, outgoing = (2, 2), (3, 2)
    values = vector(dims)
    data = np.outer(values, values.conj())
    backing = np.zeros((2 * len(data), 2 * len(data)), complex)
    backing[::2, ::2] = data
    state = DensityMatrix(backing[::2, ::2], dims=dims)
    matrix = local_matrix(4, "nonunitary", rows=6)[::-1, ::-1]
    operator = Operator(matrix, input_dims=incoming, output_dims=outgoing)
    before, after = prod(dims), 18 if local else 6
    amount = 16 * (before * after + after * after + max(before, after) + matrix.size)
    embedded = reference_map(dims, selected, matrix, outgoing)[0] if local else matrix
    expected = embedded @ data @ embedded.conj().T
    denied = Ledger(Limits(max_total_memory_bytes=amount - 1))
    with monkeypatch.context() as patch:
        for name in ("empty", "array", "multiply", "add", "matmul"):
            patch.setattr(np, name, lambda *a, **k: pytest.fail("Rectangular output group preceded admission"))
        with ResourceScope(denied), pytest.raises(MemoryError):
            state.evolve(operator, qargs=selected)
    assert denied.receipt()["live_memory_bytes"] == 0
    ledger = Ledger(Limits(max_total_memory_bytes=amount))
    with ResourceScope(ledger):
        result = state.evolve(operator, qargs=selected)
        np.testing.assert_allclose(result.data, expected, atol=3e-14)
        assert ledger.receipt()["peak_memory_bytes"] == amount
        view = result.data[:, 0]
        retained = result.data.nbytes
        del result
        gc.collect()
        assert ledger.receipt()["live_memory_bytes"] == retained
        with pytest.raises(MemoryError):
            state.evolve(operator, qargs=selected)
        del view
        gc.collect()
        assert ledger.receipt()["live_memory_bytes"] == 0
        recovered = state.evolve(operator, qargs=selected)
        np.testing.assert_allclose(recovered.data, expected, atol=3e-14)
    del recovered
    gc.collect()
    assert ledger.receipt()["live_memory_bytes"] == 0


@pytest.mark.parametrize("trace_preserving", [False, True])
def test_unselected_density_reduction_follows_the_actual_local_map_not_a_blanket_invariance(trace_preserving):
    dims = (2, 4)
    values = vector(dims)
    data = .7 * np.outer(values, values.conj()) + .3 * np.diag(abs(values)**2)
    matrix = local_matrix(5)[:, :4]
    if not trace_preserving:
        matrix = matrix @ np.diag([.1 + .2j, .4 - .1j, .7 + .3j, 1.2 - .5j])
    embedded, _ = reference_map(dims, (1,), matrix, (5,))
    expected = embedded @ data @ embedded.conj().T
    reduced = np.array([[sum(expected[left * 5 + q, right * 5 + q] for q in range(5))
                         for right in range(2)] for left in range(2)])
    original = np.array([[sum(data[left * 4 + q, right * 4 + q] for q in range(4))
                          for right in range(2)] for left in range(2)])
    with ResourceScope(Ledger()):
        actual = DensityMatrix(data, dims=dims).evolve(Operator(matrix, input_dims=(4,), output_dims=(5,)), qargs=[1])
        actual_reduced = actual.partial_trace([0])
    np.testing.assert_allclose(actual_reduced.data, reduced, atol=3e-14)
    if trace_preserving:
        np.testing.assert_allclose(reduced, original, atol=3e-14)
    else:
        assert not np.allclose(reduced, original)
    assert actual.trace() == pytest.approx(np.trace(reduced))


@pytest.mark.parametrize("shape,incoming,outgoing", [((3, 3), (3,), (3,)), ((4, 3), (3,), (2, 2)),
                                                      ((3, 4), (2, 2), (3,)), ((9, 6), (6,), (9,)), ((1, 1), (), ())])
@pytest.mark.parametrize("managed", [False, True])
def test_raw_operator_infers_positive_rectangular_and_qudit_dimensions(shape, incoming, outgoing, managed):
    data = local_matrix(shape[1], rows=shape[0])
    if managed:
        with ResourceScope(Ledger()):
            actual = Operator(data)
    else:
        actual = Operator(data)
    np.testing.assert_array_equal(actual.data, data)
    assert actual.input_dims() == incoming and actual.output_dims() == outgoing
    assert actual.dim == (shape[1], shape[0])


def test_operator_dimension_arguments_accept_the_verified_public_positional_signature():
    data = local_matrix(4, rows=6)
    with ResourceScope(Ledger()):
        actual = Operator(data, (2, 2), (3, 2))
    np.testing.assert_array_equal(actual.data, data)
    assert actual.input_dims() == (2, 2) and actual.output_dims() == (3, 2)
