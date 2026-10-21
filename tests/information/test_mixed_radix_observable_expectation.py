# Copyright 2026 QuantumBridge Contributors.
# Licensed under the Apache License, Version 2.0.
"""Actual local complex expectations, with independent embedding/reduction math."""

from contextlib import nullcontext
import gc
from math import prod
import weakref

import numpy as np
import pytest

from quantumbridge.core.classical import UnsupportedFeature
from quantumbridge.execution import UnifiedExecutionLimits as Limits, UnifiedResourceLedger as Ledger
from quantumbridge.execution.resource_context import ResourceScope
from quantumbridge.information import DensityMatrix, Operator, Pauli, Statevector
from quantumbridge.operators import SparsePauliOperator


CASES = [((3,), (0,)), ((4,), (0,)), ((2, 3), (1,)), ((3, 2), (0,)),
         ((2, 3, 2), (0, 2)), ((2, 3, 2), (2, 0)),
         ((2, 3, 2), (1, 2)), ((2, 3, 2), (2, 1)),
         ((2, 3, 2), (1,)), ((2, 4), (1,)), ((6,), (0,)),
         ((2, 3), (1, 0))]


def vector(dims):
    size = prod(dims)
    values = np.arange(1, size + 1) + 1j * np.cos(np.arange(size) * .7 + .2)
    return values / np.linalg.norm(values)


def observable(size, hermitian=False):
    indices = np.arange(size * size).reshape(size, size)
    raw = (np.sin(indices + .3) + 1j * np.cos(indices * .7 + .2)) / size
    return raw + raw.conj().T if hermitian else raw + (.2 + .7j) * np.eye(size)


def state(cls, dims, *, mixed=True):
    values = vector(dims)
    data = values if cls is Statevector else np.outer(values, values.conj())
    if cls is DensityMatrix and mixed:
        data = .6 * data + .4 * np.diag(abs(values)**2)
    return cls(data, dims=dims)


def reference(dims, targets, matrix, data):
    selected = tuple(dims[position] for position in targets)
    size = prod(dims)
    embedded = np.zeros((size, size), complex)
    for row in range(size):
        left = np.unravel_index(row, dims)
        for column in range(size):
            right = np.unravel_index(column, dims)
            if any(left[position] != right[position] for position in range(len(dims)) if position not in targets):
                continue
            a = np.ravel_multi_index(tuple(left[position] for position in targets), selected) if selected else 0
            b = np.ravel_multi_index(tuple(right[position] for position in targets), selected) if selected else 0
            embedded[row, column] = matrix[a, b]
    pure = data.ndim == 1
    first = np.vdot(data, embedded @ data) if pure else np.trace(data @ embedded)
    # A separate tensor partial trace uses no production/basis-enumeration map.
    density = np.outer(data, data.conj()) if pure else data
    count = len(dims)
    order = targets + tuple(position for position in range(count) if position not in targets)
    tensor = density.reshape(dims + dims).transpose(order + tuple(count + position for position in order))
    local_size, rest = prod(selected), size // prod(selected)
    reduced = np.einsum("aibi->ab", tensor.reshape(local_size, rest, local_size, rest))
    second = np.einsum("ij,ji->", reduced, matrix)
    np.testing.assert_allclose(first, second, atol=3e-14, rtol=0)
    return first


@pytest.mark.parametrize("dims,targets", CASES)
@pytest.mark.parametrize("cls", [Statevector, DensityMatrix])
@pytest.mark.parametrize("hermitian", [False, True])
@pytest.mark.parametrize("managed", [False, True])
def test_mixed_local_expectation_matches_independent_embedding_and_reduction(cls, dims, targets, hermitian, managed):
    value = state(cls, dims)
    local_dims = tuple(dims[position] for position in targets)
    matrix = observable(prod(local_dims), hermitian)
    op = Operator(matrix, local_dims, local_dims)
    expected = reference(dims, targets, matrix, value.data)
    before = value.data.copy()
    ledger = Ledger()
    with ResourceScope(ledger) if managed else nullcontext():
        actual = value.expectation_value(op, qargs=targets)
    np.testing.assert_allclose(actual, expected, atol=3e-14, rtol=0)
    np.testing.assert_array_equal(value.data, before)
    np.testing.assert_array_equal(op.data, matrix)
    if hermitian:
        assert abs(complex(actual).imag) < 3e-14
    else:
        assert abs(complex(actual).imag) > .1
    if managed:
        assert ledger.receipt()["live_memory_bytes"] == 0


@pytest.mark.parametrize("cls", [Statevector, DensityMatrix])
@pytest.mark.parametrize("managed", [False, True])
def test_nonuniform_qutrit_diagonal_expectation_has_hand_calculated_weights(cls, managed):
    values = np.array([1, 2j, -3], complex) / np.sqrt(14)
    value = cls(values if cls is Statevector else np.outer(values, values.conj()), dims=(3,))
    diagonal = np.diag([-2, .5, 1.3])
    with ResourceScope(Ledger()) if managed else nullcontext():
        actual = value.expectation_value(diagonal, qargs=(0,))
    np.testing.assert_allclose(actual, (-2 + .5 * 4 + 1.3 * 9) / 14, atol=1e-14, rtol=0)


@pytest.mark.parametrize("dims,targets", CASES[:6])
@pytest.mark.parametrize("hermitian", [False, True])
def test_pure_state_and_density_outer_product_have_the_same_complex_expectation(dims, targets, hermitian):
    pure = state(Statevector, dims)
    density = DensityMatrix.from_statevector(pure)
    local_dims = tuple(dims[position] for position in targets)
    op = Operator(observable(prod(local_dims), hermitian), local_dims, local_dims)
    with ResourceScope(Ledger()):
        a, b = pure.expectation_value(op, targets), density.expectation_value(op, targets)
    np.testing.assert_allclose(a, b, atol=3e-14, rtol=0)


@pytest.mark.parametrize("cls", [Statevector, DensityMatrix])
def test_reversed_targets_are_not_silently_sorted(cls):
    dims, targets = CASES[4]
    value = state(cls, dims)
    op = Operator(observable(4), (2, 2), (2, 2))
    a = value.expectation_value(op, (0, 2))
    b = value.expectation_value(op, (2, 0))
    assert abs(a-b) > 1e-4
    np.testing.assert_allclose(a, reference(dims, (0, 2), op.data, value.data), atol=3e-14, rtol=0)
    np.testing.assert_allclose(b, reference(dims, (2, 0), op.data, value.data), atol=3e-14, rtol=0)


@pytest.mark.parametrize("cls", [Statevector, DensityMatrix])
def test_local_strided_data_and_operator_do_not_build_global_matrices_or_flatten_copies(cls, monkeypatch):
    import quantumbridge.information.operator as operator_module
    dims, targets = CASES[7]
    value = state(cls, dims)
    matrix = observable(6)
    expected = reference(dims, targets, matrix, value.data)
    if cls is Statevector:
        backing = np.zeros(value.data.size * 3, complex)
        view = backing[::3]
    else:
        backing = np.zeros((value.data.shape[1] * 2, value.data.shape[0] * 3), complex)
        view = backing[::2, ::3].T
    view[:] = value.data
    value.data = view
    backing_op = np.zeros((12, 18), complex)
    op_view = backing_op[::2, ::3].T
    op_view[:] = matrix
    op = Operator(op_view, (2, 3), (2, 3))
    def forbidden(*args, **kwargs):
        pytest.fail("Local expectation attempted an embedded observable or hidden flatten")
    monkeypatch.setattr(operator_module, "_expand_subsystem_operator", forbidden)
    monkeypatch.setattr(Operator, "to_matrix", forbidden)
    for name in ("eye", "kron", "reshape", "vdot", "matmul"):
        monkeypatch.setattr(np, name, forbidden)
    with ResourceScope(Ledger()):
        actual = value.expectation_value(op, targets)
    np.testing.assert_allclose(actual, expected, atol=3e-14, rtol=0)


@pytest.mark.parametrize("cls", [Statevector, DensityMatrix])
@pytest.mark.parametrize("kind", ["list", "real", "pauli"])
def test_known_conversions_and_state_work_are_admitted_before_the_first_factory(cls, kind, monkeypatch):
    dims = (2, 3) if kind != "pauli" else (2, 2)
    targets = (1,)
    value = state(cls, dims)
    width = dims[1]
    data = observable(width)
    if kind == "list":
        argument = data.tolist()
    elif kind == "real":
        argument = data.real
        data = data.real.astype(complex)
    else:
        argument = Pauli("iX")
        data = np.array([[0, 1j], [1j, 0]])
    expected = reference(dims, targets, data, value.data)
    known = data.size * 16 + (prod(dims) * 16 if cls is Statevector else 0)
    with monkeypatch.context() as patch:
        patch.setattr(np, "empty", lambda *a, **k: pytest.fail("Admission followed a matrix factory"))
        with ResourceScope(Ledger(Limits(max_total_memory_bytes=known-1))), pytest.raises(MemoryError):
            value.expectation_value(argument, targets)
    ledger = Ledger(Limits(max_total_memory_bytes=known))
    seen = []
    allocate = np.empty
    def observe(*args, **kwargs):
        result = allocate(*args, **kwargs)
        seen.append(weakref.ref(result))
        return result
    with monkeypatch.context() as patch:
        patch.setattr(np, "empty", observe)
        with ResourceScope(ledger):
            actual = value.expectation_value(argument, targets)
    np.testing.assert_allclose(actual, expected, atol=3e-14, rtol=0)
    gc.collect()
    assert ledger.receipt()["live_memory_bytes"] == 0
    assert seen and all(reference() is None for reference in seen)
    with ResourceScope(ledger):
        recovered = value.expectation_value(argument, targets)
    np.testing.assert_allclose(recovered, expected, atol=3e-14, rtol=0)


@pytest.mark.parametrize("cls", [Statevector, DensityMatrix])
def test_existing_user_view_holds_its_lease_and_release_allows_expectation_recovery(cls):
    value = state(cls, (2, 3))
    raw = observable(3).tolist()
    work = 3 * 3 * 16 + (6 * 16 if cls is Statevector else 0)
    ledger = Ledger(Limits(max_total_memory_bytes=work + 6 * 16 - 1))
    with ResourceScope(ledger):
        original = Statevector.from_int(0, (2, 3))
    escaped = original.data[::2]
    del original
    gc.collect()
    assert ledger.receipt()["live_memory_bytes"] == 6 * 16
    with ResourceScope(ledger), pytest.raises(MemoryError):
        value.expectation_value(raw, (1,))
    del escaped
    gc.collect()
    assert ledger.receipt()["live_memory_bytes"] == 0
    with ResourceScope(ledger):
        actual = value.expectation_value(raw, (1,))
    np.testing.assert_allclose(actual, reference((2, 3), (1,), np.asarray(raw), value.data), atol=3e-14, rtol=0)


def test_density_borrowed_numeric_operator_has_no_new_ndarray_even_at_zero_budget(monkeypatch):
    value = state(DensityMatrix, (2, 3, 2))
    op = Operator(observable(6), (2, 3), (2, 3))
    expected = reference((2, 3, 2), (2, 1), op.data, value.data)
    def forbidden(*a, **k):
        pytest.fail("Direct density expectation allocated an ndarray")
    for name in ("empty", "zeros", "eye", "kron", "matmul"):
        monkeypatch.setattr(np, name, forbidden)
    monkeypatch.setattr(Operator, "to_matrix", forbidden)
    with ResourceScope(Ledger(Limits(max_total_memory_bytes=0))):
        actual = value.expectation_value(op, (2, 1))
    np.testing.assert_allclose(actual, expected, atol=3e-14, rtol=0)


@pytest.mark.parametrize("cls", [Statevector, DensityMatrix])
@pytest.mark.parametrize("targets", [(0, 0), (-1,), (3,), (True,), (0.0,)])
def test_invalid_targets_reject_before_matrix_export_or_allocation(cls, targets, monkeypatch):
    value = state(cls, (2, 3, 2))
    op = Operator(np.eye(4), (2, 2), (2, 2))
    def forbidden(*a, **k):
        pytest.fail("Invalid targets reached a matrix export/factory")
    monkeypatch.setattr(Operator, "to_matrix", forbidden)
    monkeypatch.setattr(np, "empty", forbidden)
    with ResourceScope(Ledger()), pytest.raises(ValueError):
        value.expectation_value(op, targets)


@pytest.mark.parametrize("cls", [Statevector, DensityMatrix])
@pytest.mark.parametrize("kind", ["partition", "output", "rectangle"])
def test_invalid_observable_dimensions_do_not_become_valid_merely_from_total_size(cls, kind, monkeypatch):
    value = state(cls, (2, 4))
    if kind == "partition":
        op = Operator(observable(4), (2, 2), (2, 2))
    elif kind == "output":
        op = Operator(observable(4), (4,), (2, 2))
    else:
        op = Operator(np.ones((3, 4)), (4,), (3,))
    def forbidden(*a, **k):
        pytest.fail("Invalid observable reached a matrix factory")
    monkeypatch.setattr(Operator, "to_matrix", forbidden)
    monkeypatch.setattr(np, "empty", forbidden)
    with ResourceScope(Ledger()), pytest.raises(ValueError):
        value.expectation_value(op, (1,))


@pytest.mark.parametrize("cls", [Statevector, DensityMatrix])
def test_foreign_factories_and_dimension_protocols_are_not_dispatched_in_a_scope(cls):
    class Foreign:
        def to_matrix(self):
            pytest.fail("Foreign matrix factory dispatched")
        def to_hamiltonian(self):
            pytest.fail("Foreign Hamiltonian protocol dispatched")
        def __array__(self, *a, **k):
            pytest.fail("Foreign array protocol dispatched")
    class ForeignOperator(Operator):
        def input_dims(self, *a):
            pytest.fail("Foreign dimension protocol dispatched")
    value = state(cls, (2, 3))
    for foreign in (Foreign(), object.__new__(ForeignOperator), np.array([[object()]], dtype=object)):
        with ResourceScope(Ledger()), pytest.raises(UnsupportedFeature):
            value.expectation_value(foreign, (1,))


@pytest.mark.parametrize("cls", [Statevector, DensityMatrix])
@pytest.mark.parametrize("dims,targets", [((), None), ((), ()), ((1,), (0,)), ((2, 3), ())])
def test_native_scalar_and_zero_register_boundaries_are_actual_linear_expectations(cls, dims, targets):
    value = state(cls, dims)
    local = () if not targets else (1,)
    op = Operator(np.array([[.2 + .7j]]), local, local)
    expected = (.2 + .7j) * (np.vdot(value.data, value.data) if cls is Statevector else np.trace(value.data))
    with ResourceScope(Ledger()):
        actual = value.expectation_value(op, targets)
    np.testing.assert_allclose(actual, expected, atol=3e-14, rtol=0)


@pytest.mark.parametrize("cls", [Statevector, DensityMatrix])
def test_expectation_is_linear_in_non_normalized_state_weights(cls):
    value = state(cls, (2, 3))
    matrix = observable(3)
    original = reference((2, 3), (1,), matrix, value.data)
    value.data *= 2 if cls is Statevector else 3
    with ResourceScope(Ledger()):
        actual = value.expectation_value(matrix, (1,))
    np.testing.assert_allclose(actual, original * (4 if cls is Statevector else 3), atol=3e-14, rtol=0)


@pytest.mark.parametrize("cls", [Statevector, DensityMatrix])
def test_existing_qubit_pauli_phase_and_sparse_complex_local_targets_remain_mathematical(cls):
    value = state(cls, (2, 2), mixed=False)
    arguments = [Pauli("iX"), SparsePauliOperator.from_list([("Z", .2 + .7j)])]
    matrices = [np.array([[0, 1j], [1j, 0]]), (.2 + .7j) * np.diag([1, -1])]
    for op, matrix in zip(arguments, matrices):
        with ResourceScope(Ledger()):
            actual = value.expectation_value(op, (1,))
        np.testing.assert_allclose(actual, reference((2, 2), (1,), matrix, value.data), atol=3e-14, rtol=0)


@pytest.mark.parametrize("cls", [Statevector, DensityMatrix])
@pytest.mark.parametrize("dims,targets", CASES[:6])
def test_optional_public_numeric_expectation_has_explicit_wire_and_dimension_conversion(cls, dims, targets):
    public = pytest.importorskip("qiskit.quantum_info")
    value = state(cls, dims)
    local = tuple(dims[position] for position in targets)
    matrix = observable(prod(local))
    expected_cls = public.Statevector if cls is Statevector else public.DensityMatrix
    expected = expected_cls(value.data, dims=dims[::-1]).expectation_value(
        public.Operator(matrix, local[::-1], local[::-1]),
        qargs=[len(dims)-1-position for position in reversed(targets)])
    actual = value.expectation_value(Operator(matrix, local, local), targets)
    np.testing.assert_allclose(actual, expected, atol=3e-14, rtol=0)


def test_mapped_evolution_density_reduction_and_local_expectation_are_one_native_workflow():
    dims = (2, 3, 2)
    initial = state(Statevector, dims)
    indices = np.arange(3)
    transform = np.exp(2j * np.pi * np.outer(indices, indices) / 3) / np.sqrt(3)
    evolved = initial.evolve(Operator(transform, (3,), (3,)), (1,))
    density = DensityMatrix.from_statevector(evolved)
    reduced = density.partial_trace((1,))
    op = Operator(observable(3), (3,), (3,))
    expected = reference(dims, (1,), op.data, evolved.data)
    with ResourceScope(Ledger()):
        actual = reduced.expectation_value(op, (0,))
        full_density_value = density.expectation_value(op, (1,))
    np.testing.assert_allclose(actual, expected, atol=3e-14, rtol=0)
    np.testing.assert_allclose(full_density_value, expected, atol=3e-14, rtol=0)
    assert reduced.dims() == (3,) and reduced.dim == (3, 3)


@pytest.mark.parametrize("cls", [Statevector, DensityMatrix])
def test_parameterized_qutrit_expectation_has_the_independent_finite_difference_objective(cls):
    matrix = np.array([[.3, -1j, 0], [1j, -.7, 0], [0, 0, 1.2]])
    op = Operator(matrix, (3,), (3,))
    def objective(theta):
        qutrit = np.array([np.cos(theta), 1j * np.sin(theta), 0])
        values = np.kron(np.array([.6, .8j]), qutrit)
        value = cls(values if cls is Statevector else np.outer(values, values.conj()), dims=(2, 3))
        return value.expectation_value(op, (1,))
    theta, step = .37, 1e-6
    with ResourceScope(Ledger()):
        mean = objective(theta)
        derivative = (objective(theta + step)-objective(theta-step)) / (2*step)
    expected = .3 * np.cos(theta)**2 - .7 * np.sin(theta)**2 + 2 * np.cos(theta) * np.sin(theta)
    np.testing.assert_allclose(mean, expected, atol=3e-14, rtol=0)
    np.testing.assert_allclose(derivative, -np.sin(2*theta) + 2*np.cos(2*theta), atol=2e-9, rtol=0)


@pytest.mark.parametrize("cls", [Statevector, DensityMatrix])
def test_explicit_numeric_ndarray_subclasses_are_borrowed_without_foreign_protocols(cls):
    class Trap(np.ndarray):
        def __array_function__(self, *a, **k):
            pytest.fail("Foreign ndarray function protocol dispatched")
        def __array_ufunc__(self, *a, **k):
            pytest.fail("Foreign ndarray ufunc protocol dispatched")
        def __getitem__(self, *a, **k):
            pytest.fail("Foreign ndarray item protocol dispatched")
    dims, targets = CASES[7]
    value = state(cls, dims)
    matrix = observable(6)
    expected = reference(dims, targets, matrix, value.data)
    value.data = value.data.view(Trap)
    op = Operator(matrix, (2, 3), (2, 3))
    op.data = op.data.view(Trap)
    with ResourceScope(Ledger()):
        actual = value.expectation_value(op, targets)
    np.testing.assert_allclose(actual, expected, atol=3e-14, rtol=0)


def test_pure_borrowed_operator_only_admits_one_state_action_vector(monkeypatch):
    value = state(Statevector, (2, 3, 2))
    op = Operator(observable(6), (2, 3), (2, 3))
    expected = reference((2, 3, 2), (2, 1), op.data, value.data)
    known = 12 * 16
    def forbidden(*a, **k):
        pytest.fail("Borrowed Operator was copied or action buffer allocated too early")
    monkeypatch.setattr(Operator, "to_matrix", forbidden)
    with monkeypatch.context() as patch:
        patch.setattr(np, "empty", forbidden)
        with ResourceScope(Ledger(Limits(max_total_memory_bytes=known-1))), pytest.raises(MemoryError):
            value.expectation_value(op, (2, 1))
    ledger = Ledger(Limits(max_total_memory_bytes=known))
    with ResourceScope(ledger):
        actual = value.expectation_value(op, (2, 1))
    np.testing.assert_allclose(actual, expected, atol=3e-14, rtol=0)
    assert ledger.receipt()["peak_memory_bytes"] == known
    assert ledger.receipt()["live_memory_bytes"] == 0


@pytest.mark.parametrize("cls", [Statevector, DensityMatrix])
def test_actual_state_dtype_conversion_is_part_of_the_first_known_group(cls, monkeypatch):
    dims, targets = (2, 3), (1,)
    value = state(cls, dims)
    value.data = value.data.real.copy()
    op = Operator(observable(3), (3,), (3,))
    expected = reference(dims, targets, op.data, value.data)
    known = value.data.size * 16 + (6 * 16 if cls is Statevector else 0)
    with monkeypatch.context() as patch:
        patch.setattr(np, "empty", lambda *a, **k: pytest.fail("State conversion preceded whole-group admission"))
        with ResourceScope(Ledger(Limits(max_total_memory_bytes=known-1))), pytest.raises(MemoryError):
            value.expectation_value(op, targets)
    ledger = Ledger(Limits(max_total_memory_bytes=known))
    with ResourceScope(ledger):
        actual = value.expectation_value(op, targets)
    np.testing.assert_allclose(actual, expected, atol=3e-14, rtol=0)
    assert ledger.receipt()["live_memory_bytes"] == 0


@pytest.mark.parametrize("cls", [Statevector, DensityMatrix])
def test_full_numeric_legacy_partition_and_typed_observable_endomorphism_are_distinct(cls, monkeypatch):
    value = state(cls, (2, 3))
    matrix = observable(6)
    expected = reference((2, 3), (0, 1), matrix, value.data)
    legacy = Operator(matrix, (6,), (6,))
    with ResourceScope(Ledger()):
        np.testing.assert_allclose(value.expectation_value(legacy), expected, atol=3e-14, rtol=0)
        np.testing.assert_allclose(value.expectation_value(matrix), expected, atol=3e-14, rtol=0)
    invalid = Operator(matrix, (2, 3), (3, 2))
    monkeypatch.setattr(np, "empty", lambda *a, **k: pytest.fail("Non-endomorphism reached a factory"))
    with ResourceScope(Ledger()), pytest.raises(ValueError):
        value.expectation_value(invalid)


@pytest.mark.parametrize("cls", [Statevector, DensityMatrix])
def test_full_sparse_complex_coefficients_keep_even_a_small_nonzero_imaginary_part(cls):
    value = cls.from_int(0, (2, 2))
    op = SparsePauliOperator.from_list([("II", 1 + 5e-13j)])
    with ResourceScope(Ledger()):
        actual = value.expectation_value(op)
    assert complex(actual).imag == pytest.approx(5e-13, abs=1e-26, rel=1e-13)
    np.testing.assert_allclose(actual.real, 1, atol=3e-14, rtol=0)


@pytest.mark.parametrize("cls", [Statevector, DensityMatrix])
def test_pauli_objects_are_explicitly_qubit_only_but_numeric_operators_can_target_binary_subsystems(cls):
    value = state(cls, (2, 3, 2))
    for pauli in (Pauli("X"), SparsePauliOperator.from_list([("X", .2 + .7j)])):
        with ResourceScope(Ledger()), pytest.raises(UnsupportedFeature):
            value.expectation_value(pauli, (0,))
    op = Operator(Pauli("X").to_matrix(), (2,), (2,))
    expected = reference((2, 3, 2), (0,), op.data, value.data)
    with ResourceScope(Ledger()):
        actual = value.expectation_value(op, (0,))
    np.testing.assert_allclose(actual, expected, atol=3e-14, rtol=0)


@pytest.mark.parametrize("coefficient", [.3, .2 + .7j])
def test_full_sparse_matrix_free_state_path_does_not_dispatch_numeric_ndarray_protocols(coefficient):
    class Trap(np.ndarray):
        def __array_function__(self, *a, **k):
            pytest.fail("Matrix-free sparse expectation dispatched a foreign ndarray protocol")
        def __array_ufunc__(self, *a, **k):
            pytest.fail("Matrix-free sparse expectation dispatched a foreign ndarray protocol")
    value = state(Statevector, (2, 2))
    expected = coefficient * np.vdot(value.data, np.diag([1, 1, -1, -1]) @ value.data)
    value.data = value.data.view(Trap)
    op = SparsePauliOperator.from_list([("ZI", coefficient)])
    with ResourceScope(Ledger()):
        actual = value.expectation_value(op)
    np.testing.assert_allclose(actual, expected, atol=3e-14, rtol=0)
