# Copyright 2026 QuantumBridge Contributors.
# Licensed under the Apache License, Version 2.0.
"""Independent native operator products with actual ordered subsystem maps."""

import gc
from math import prod

import numpy as np
import pytest

from quantumbridge.core.classical import UnsupportedFeature
from quantumbridge.execution import UnifiedResourceLedger as Ledger, UnifiedExecutionLimits as Limits
from quantumbridge.execution.resource_context import ResourceScope
from quantumbridge.information import DensityMatrix, Operator, Statevector


CASES = [
    ((2, 3), (2, 3), (0,), (4,)),
    ((2, 3), (2, 3), (1,), (2,)),
    ((3, 2), (3, 2), (0,), (4,)),
    ((2, 3, 2), (2, 3, 2), (0, 2), (2, 2)),
    ((2, 3, 2), (2, 3, 2), (2, 0), (2, 2)),
    ((2, 3, 2), (2, 3, 2), (1, 2), (2, 3)),
    ((2, 3, 2), (2, 3, 2), (2, 1), (3, 2)),
    ((4, 2), (3, 2, 2), (0,), (5,)),
    ((2, 4), (4, 2), (1,), (3,)),
    ((2, 3, 2), (3, 2), (1,), (4,)),
    ((3, 2), (2, 3, 2), (0,), (2,)),
    ((2, 3, 2), (2, 3, 2), (0, 1, 2), (3, 2, 2)),
]


def matrix(rows, columns, seed=0):
    values = np.arange(rows * columns).reshape(rows, columns) + seed
    return np.exp(.17j * seed) * (np.sin(values + .3) + 1j * np.cos(values * .7 + .2)) / max(rows, columns)


def make_case(case, front):
    incoming, outgoing, selected, new_local = case
    side = outgoing if front else incoming
    old_local = tuple(side[position] for position in selected)
    local_input, local_output = (old_local, new_local) if front else (new_local, old_local)
    host = Operator(matrix(prod(outgoing), prod(incoming), 2), incoming, outgoing)
    local = Operator(matrix(prod(local_output), prod(local_input), 7), local_input, local_output)
    changed = list(side)
    for position, size in zip(selected, new_local):
        changed[position] = size
    expected_input = incoming if front else tuple(changed)
    expected_output = tuple(changed) if front else outgoing
    return host, local, selected, expected_input, expected_output


def enumerate_embedding(incoming, outgoing, selected, local):
    result = np.zeros((prod(outgoing), prod(incoming)), complex)
    for row in range(prod(outgoing)):
        left = np.unravel_index(row, outgoing)
        for column in range(prod(incoming)):
            right = np.unravel_index(column, incoming)
            if any(left[position] != right[position] for position in range(len(incoming)) if position not in selected):
                continue
            i = np.ravel_multi_index(tuple(left[position] for position in selected), local.output_dims())
            j = np.ravel_multi_index(tuple(right[position] for position in selected), local.input_dims())
            result[row, column] = local.data[i, j]
    return result


def references(host, local, selected, result_input, result_output, front):
    before = host.output_dims() if front else result_input
    after = result_output if front else host.input_dims()
    embedded = enumerate_embedding(before, after, selected, local)
    explicit = embedded @ host.data if front else host.data @ embedded
    # This oracle contracts the selected tensor axes directly, without using
    # the basis enumeration or the production stride/index implementation.
    incoming, outgoing = host.input_dims(), host.output_dims()
    row_count, count = len(outgoing), len(selected)
    tensor = host.data.reshape(outgoing + incoming)
    local_tensor = local.data.reshape(local.output_dims() + local.input_dims())
    if front:
        contracted = np.tensordot(local_tensor, tensor, axes=(tuple(range(count, 2 * count)), selected))
        labels = selected + tuple(position for position in range(row_count) if position not in selected) + tuple(range(row_count, row_count + len(incoming)))
    else:
        axes = tuple(row_count + position for position in selected)
        contracted = np.tensordot(tensor, local_tensor, axes=(axes, tuple(range(count))))
        labels = tuple(range(row_count)) + tuple(row_count + position for position in range(len(incoming)) if position not in selected) + axes
    independent = contracted.transpose(tuple(labels.index(position) for position in range(len(labels)))).reshape(prod(result_output), prod(result_input))
    np.testing.assert_allclose(explicit, independent, atol=3e-15, rtol=0)
    return explicit


@pytest.mark.parametrize("case", CASES)
@pytest.mark.parametrize("front", [False, True])
@pytest.mark.parametrize("managed", [False, True])
def test_mixed_mapped_product_matches_two_independent_complex_oracles(case, front, managed):
    host, local, selected, incoming, outgoing = make_case(case, front)
    expected = references(host, local, selected, incoming, outgoing, front)
    old_host, old_local = host.data.copy(), local.data.copy()
    if managed:
        ledger = Ledger()
        with ResourceScope(ledger):
            actual = host.compose(local, qargs=selected, front=front)
        assert ledger.receipt()["live_memory_bytes"] == actual.data.nbytes
    else:
        actual = host.compose(local, qargs=selected, front=front)
    np.testing.assert_allclose(actual.data, expected, atol=3e-15, rtol=0)
    assert actual.input_dims() == incoming and actual.output_dims() == outgoing
    np.testing.assert_array_equal(host.data, old_host)
    np.testing.assert_array_equal(local.data, old_local)


@pytest.mark.parametrize("case", CASES[:6])
@pytest.mark.parametrize("front", [False, True])
@pytest.mark.parametrize("cls", [Statevector, DensityMatrix])
def test_composed_operator_has_the_same_actual_state_action_as_sequential_maps(case, front, cls):
    host, local, selected, incoming, outgoing = make_case(case, front)
    values = np.arange(1, prod(incoming) + 1) + 1j * np.arange(prod(incoming), 0, -1)
    values = values / np.linalg.norm(values)
    state = cls(values if cls is Statevector else np.outer(values, values.conj()), dims=incoming)
    composed = host.compose(local, qargs=selected, front=front)
    actual = state.evolve(composed)
    if front:
        intermediate = state.evolve(host)
        direction = host.output_dims(), outgoing
    else:
        intermediate = state
        direction = incoming, host.input_dims()
    # Full typed application also covers rectangular maps on pure states; the
    # P0.2 local Statevector rectangular limitation is not silently removed.
    embedded = Operator(enumerate_embedding(*direction, selected, local), *direction)
    sequential = intermediate.evolve(embedded)
    if not front:
        sequential = sequential.evolve(host)
    np.testing.assert_allclose(actual.data, sequential.data, atol=4e-15, rtol=0)
    assert actual.dims() == outgoing
    expected = references(host, local, selected, incoming, outgoing, front)
    native = expected @ values
    np.testing.assert_allclose(actual.data, native if cls is Statevector else np.outer(native, native.conj()), atol=4e-15, rtol=0)
    if cls is DensityMatrix:
        assert actual.trace() == pytest.approx(np.vdot(native, native).real)


@pytest.mark.parametrize("front", [False, True])
def test_noncontiguous_transposed_arrays_do_not_build_an_embedded_operator_or_hidden_reshape(front, monkeypatch):
    import quantumbridge.information.operator as operator_module
    incoming, outgoing, selected, new_dims = CASES[6]
    host, local, _, result_input, result_output = make_case(CASES[6], front)
    expected = references(host, local, selected, result_input, result_output, front)
    for op in (host, local):
        backing = np.zeros((op.data.shape[1] * 2, op.data.shape[0] * 3), complex)
        view = backing[::2, ::3].T
        view[:] = op.data
        op.data = view
        assert not view.flags.c_contiguous and not view.flags.f_contiguous
    def forbidden(*args, **kwargs):
        pytest.fail("Mapped composition attempted a full embedded matrix or packing reshape")
    monkeypatch.setattr(operator_module, "_expand_subsystem_operator", forbidden)
    monkeypatch.setattr(np, "kron", forbidden)
    monkeypatch.setattr(np, "eye", forbidden)
    monkeypatch.setattr(np, "reshape", forbidden)
    with ResourceScope(Ledger()):
        actual = host.compose(local, qargs=selected, front=front)
    np.testing.assert_allclose(actual.data, expected, atol=3e-15, rtol=0)


@pytest.mark.parametrize("front", [False, True])
def test_rectangular_mapped_known_group_denial_escaped_view_and_valid_recovery(front, monkeypatch):
    from quantumbridge.execution import ResourceLimitError
    host, local, selected, incoming, outgoing = make_case(((3, 2), (2, 4), (1,), (5,)), front)
    expected = references(host, local, selected, incoming, outgoing, front)
    output_bytes = prod(incoming) * prod(outgoing) * 16
    scratch_bytes = (host.data.shape[1] if front else host.data.shape[0]) * 16
    known = output_bytes + scratch_bytes
    ledger = Ledger(Limits(max_total_memory_bytes=known-1))
    with monkeypatch.context() as patch:
        patch.setattr(np, "empty", lambda *a, **k: pytest.fail("Overbudget map reached a factory"))
        with ResourceScope(ledger), pytest.raises(ResourceLimitError):
            host.compose(local, qargs=selected, front=front)
    assert ledger.receipt()["live_memory_bytes"] == 0
    ledger = Ledger(Limits(max_total_memory_bytes=known))
    with ResourceScope(ledger):
        actual = host.compose(local, qargs=selected, front=front)
    np.testing.assert_allclose(actual.data, expected, atol=3e-15, rtol=0)
    view = actual.data[:, :1]
    del actual
    gc.collect()
    assert ledger.receipt()["live_memory_bytes"] == output_bytes
    with ResourceScope(ledger), pytest.raises(ResourceLimitError):
        host.compose(local, qargs=selected, front=front)
    del view
    gc.collect()
    assert ledger.receipt()["live_memory_bytes"] == 0
    with ResourceScope(ledger):
        recovered = host.compose(local, qargs=selected, front=front)
    np.testing.assert_allclose(recovered.data, expected, atol=3e-15, rtol=0)


@pytest.mark.parametrize("selected", [(0, 0), (-1,), (3,), (True,), (0.0,)])
@pytest.mark.parametrize("front", [False, True])
def test_invalid_mapped_targets_fail_before_any_factory(selected, front, monkeypatch):
    host = Operator(matrix(12, 12), (2, 3, 2), (2, 3, 2))
    local = Operator(matrix(4, 4), (2, 2), (2, 2))
    monkeypatch.setattr(np, "empty", lambda *a, **k: pytest.fail("Invalid target reached a factory"))
    with ResourceScope(Ledger()), pytest.raises(ValueError):
        host.compose(local, qargs=selected, front=front)


@pytest.mark.parametrize("front", [False, True])
def test_dimension_mismatch_and_local_subsystem_insertion_are_not_accepted(front, monkeypatch):
    host = Operator(matrix(12, 12), (2, 3, 2), (2, 3, 2))
    wrong = Operator(matrix(4, 4), (4,), (4,))
    inserted = Operator(matrix(4, 2), (2,), (2, 2))
    argument = inserted if front else inserted.adjoint()
    monkeypatch.setattr(np, "empty", lambda *a, **k: pytest.fail("Invalid dimensions reached a factory"))
    with ResourceScope(Ledger()), pytest.raises(ValueError):
        host.compose(wrong, qargs=(1,), front=front)
    with ResourceScope(Ledger()), pytest.raises(UnsupportedFeature):
        host.compose(argument, qargs=(0,), front=front)


def test_mapped_composition_keeps_strict_foreign_protocol_boundary():
    class Foreign:
        def __array__(self, *args, **kwargs):
            pytest.fail("Foreign array conversion dispatched")
    class ForeignOperator(Operator):
        def input_dims(self, *args):
            pytest.fail("Foreign dimension protocol dispatched")
    host = Operator(matrix(6, 6), (2, 3), (2, 3))
    for foreign in (Foreign(), object.__new__(ForeignOperator), np.array([[object()]], dtype=object)):
        with ResourceScope(Ledger()), pytest.raises(UnsupportedFeature):
            host.compose(foreign, qargs=(1,))


@pytest.mark.parametrize("front", [False, True])
def test_existing_full_typed_rectangle_and_partition_validation_remain_real_regressions(front):
    first = Operator(matrix(6, 4, 2), (2, 2), (3, 2))
    second = Operator(matrix(3, 6, 7), (3, 2), (3,))
    with ResourceScope(Ledger()):
        actual = first.compose(second, front=True) if front else second.compose(first)
    np.testing.assert_allclose(actual.data, second.data @ first.data, atol=2e-15, rtol=0)
    assert actual.input_dims() == (2, 2) and actual.output_dims() == (3,)
    with pytest.raises(ValueError):
        second.compose(Operator(first.data, (2, 2), (2, 3)))


@pytest.mark.parametrize("method", ["compose", "dot", "matmul", "reflected"])
def test_full_raw_rectangular_products_infer_only_the_uncontracted_side(method):
    host = Operator(matrix(3, 6, 2), (6,), (3,))
    right, left = matrix(6, 4, 7), matrix(5, 3, 9)
    with ResourceScope(Ledger()):
        actual = host.compose(right) if method == "compose" else host.dot(right) if method == "dot" else host @ right if method == "matmul" else left @ host
    np.testing.assert_allclose(actual.data, left @ host.data if method == "reflected" else host.data @ right, atol=2e-15, rtol=0)
    assert actual.input_dims() == ((6,) if method == "reflected" else (2, 2))
    assert actual.output_dims() == ((5,) if method == "reflected" else (3,))


def test_two_mixed_local_products_are_not_silently_sorted():
    host, local, selected, incoming, outgoing = make_case(CASES[3], False)
    first = host.compose(local, qargs=(0, 2))
    second = host.compose(local, qargs=(2, 0))
    assert np.max(abs(first.data-second.data)) > .001
    np.testing.assert_allclose(first.data, references(host, local, (0, 2), incoming, outgoing, False), atol=3e-15, rtol=0)
    np.testing.assert_allclose(second.data, references(host, local, (2, 0), incoming, outgoing, False), atol=3e-15, rtol=0)


@pytest.mark.parametrize("case", CASES)
@pytest.mark.parametrize("front", [False, True])
def test_optional_public_composition_has_explicit_native_order_and_side_conversion(case, front):
    public = pytest.importorskip("qiskit.quantum_info")
    host, local, selected, incoming, outgoing = make_case(case, front)
    actual = host.compose(local, qargs=selected, front=front)
    reference = public.Operator(host.data, host.input_dims()[::-1], host.output_dims()[::-1]).compose(
        public.Operator(local.data, local.input_dims()[::-1], local.output_dims()[::-1]),
        qargs=[len(host.output_dims() if front else host.input_dims())-1-position for position in reversed(selected)],
        front=not front)
    np.testing.assert_allclose(actual.data, reference.data, atol=3e-15, rtol=0)
    assert actual.input_dims() == reference.input_dims()[::-1]
    assert actual.output_dims() == reference.output_dims()[::-1]


def test_end_to_end_composition_evolution_reduction_and_native_probability_contract():
    first = Operator(matrix(12, 12, 2), (2, 3, 2), (2, 3, 2))
    second = Operator(matrix(4, 4, 7), (2, 2), (2, 2))
    state = Statevector.from_int(5, (2, 3, 2))
    combined = first.compose(second, qargs=(2, 0))
    density = DensityMatrix.from_statevector(state.evolve(combined))
    reduced = density.partial_trace([1])
    values = references(first, second, (2, 0), first.input_dims(), first.output_dims(), False) @ state.data
    tensor = values.reshape(2, 3, 2)
    expected = np.einsum("aib,ajb->ij", tensor, tensor.conj())
    np.testing.assert_allclose(reduced.data, expected, atol=3e-15, rtol=0)
    assert reduced.dims() == (3,) and reduced.dim == (3, 3)
    probabilities = reduced.probabilities()
    assert isinstance(probabilities, dict)
    for index, value in enumerate(expected.diagonal().real):
        assert probabilities[str(index)] == pytest.approx(value)


@pytest.mark.parametrize("front", [False, True])
@pytest.mark.parametrize("raw", [False, True])
def test_raw_list_mapped_conversion_is_in_the_whole_known_group_before_a_factory(front, raw, monkeypatch):
    host, local, selected, incoming, outgoing = make_case(CASES[3], front)
    expected = references(host, local, selected, incoming, outgoing, front)
    argument = local.data.tolist() if raw else local
    known = expected.nbytes + (host.data.shape[1] if front else host.data.shape[0]) * 16
    if raw:
        known += local.data.nbytes
    with monkeypatch.context() as patch:
        patch.setattr(np, "empty", lambda *a, **k: pytest.fail("Known group was not checked before conversion"))
        with ResourceScope(Ledger(Limits(max_total_memory_bytes=known-1))), pytest.raises(MemoryError):
            host.compose(argument, qargs=selected, front=front)
    ledger = Ledger(Limits(max_total_memory_bytes=known))
    with ResourceScope(ledger):
        actual = host.compose(argument, qargs=selected, front=front)
    np.testing.assert_allclose(actual.data, expected, atol=3e-15, rtol=0)
    assert ledger.receipt()["live_memory_bytes"] == actual.data.nbytes


@pytest.mark.parametrize("raw", [False, True])
def test_full_rectangular_packing_and_conversion_are_admitted_together(raw, monkeypatch):
    host_data = matrix(6, 6, 2)[::2, :]
    other_data = matrix(12, 8, 7)[::2, ::2]
    assert not host_data.flags.c_contiguous and not host_data.flags.f_contiguous
    assert not other_data.flags.c_contiguous and not other_data.flags.f_contiguous
    host = Operator(host_data, (6,), (3,))
    argument = other_data.tolist() if raw else Operator(other_data, (2, 2), (6,))
    expected = host_data @ other_data
    known = expected.nbytes + host_data.nbytes + other_data.nbytes
    with monkeypatch.context() as patch:
        patch.setattr(np, "empty", lambda *a, **k: pytest.fail("Packing group preceded admission"))
        with ResourceScope(Ledger(Limits(max_total_memory_bytes=known-1))), pytest.raises(MemoryError):
            host.compose(argument)
    ledger = Ledger(Limits(max_total_memory_bytes=known))
    with ResourceScope(ledger):
        actual = host.compose(argument)
    np.testing.assert_allclose(actual.data, expected, atol=2e-15, rtol=0)
    assert actual.input_dims() == (2, 2) and actual.output_dims() == (3,)
    assert ledger.receipt()["live_memory_bytes"] == actual.data.nbytes


@pytest.mark.parametrize("front", [False, True])
def test_foreign_ndarray_protocols_are_not_called_for_explicit_numeric_buffers(front):
    class Trap(np.ndarray):
        def __array_ufunc__(self, *args, **kwargs):
            pytest.fail("Foreign ndarray ufunc protocol dispatched")
        def __array_function__(self, *args, **kwargs):
            pytest.fail("Foreign ndarray function protocol dispatched")
    host, local, selected, incoming, outgoing = make_case(CASES[5], front)
    expected = references(host, local, selected, incoming, outgoing, front)
    host.data = host.data.view(Trap)
    local.data = local.data.view(Trap)
    with ResourceScope(Ledger()):
        actual = host.compose(local, qargs=selected, front=front)
    np.testing.assert_allclose(actual.data, expected, atol=3e-15, rtol=0)


@pytest.mark.parametrize("front", [False, True])
@pytest.mark.parametrize("case", [CASES[5], CASES[7], CASES[10]])
def test_mapped_adjoint_reverses_the_product_and_swaps_the_actual_sides(case, front):
    host, local, selected, incoming, outgoing = make_case(case, front)
    combined = host.compose(local, qargs=selected, front=front)
    reversed_product = host.adjoint().compose(local.adjoint(), qargs=selected, front=not front)
    np.testing.assert_allclose(combined.adjoint().data, reversed_product.data, atol=3e-15, rtol=0)
    assert reversed_product.input_dims() == outgoing and reversed_product.output_dims() == incoming


@pytest.mark.parametrize("front", [False, True])
def test_empty_native_targets_remain_a_scalar_map_not_a_fake_qudit(front):
    host = Operator(matrix(6, 6), (2, 3), (2, 3))
    local = Operator(np.array([[.2 + .7j]]), (), ())
    with ResourceScope(Ledger()):
        actual = host.compose(local, qargs=(), front=front)
    np.testing.assert_allclose(actual.data, host.data * (.2 + .7j), atol=1e-15, rtol=0)
    assert actual.input_dims() == actual.output_dims() == (2, 3)


def test_minimal_repartitioned_basis_has_hand_calculated_native_state_and_operator_action():
    # q0-first (3,2), basis 1 -> selected digits (1,0) -> local index 3.
    # Identity as (2,3)->(3,2) means output digits (1,1), full index 4.
    state = Statevector.from_int(1, (3, 2))
    state.data *= 1j
    local = Operator(np.eye(6, dtype=complex), (2, 3), (3, 2))
    expected = np.zeros(6, complex)
    expected[4] = 1j
    direct = state.evolve(local, qargs=(1, 0))
    full = Operator(np.eye(6, dtype=complex), (3, 2), (3, 2)).compose(local, qargs=(1, 0), front=True)
    np.testing.assert_array_equal(direct.data, expected)
    np.testing.assert_array_equal(state.evolve(full).data, expected)
    density = DensityMatrix.from_statevector(state).evolve(local, qargs=(1, 0))
    np.testing.assert_array_equal(density.data, np.outer(expected, expected.conj()))
    assert direct.dims() == full.output_dims() == density.dims() == (2, 3)


@pytest.mark.parametrize("front", [False, True])
def test_optional_public_full_raw_rectangle_matches_the_explicit_native_multiplication_side(front):
    public = pytest.importorskip("qiskit.quantum_info")
    host = Operator(matrix(3, 6, 2), (6,), (3,))
    raw = matrix(5, 3, 7) if front else matrix(6, 4, 7)
    actual = host.compose(raw, front=front)
    reference = public.Operator(host.data, host.input_dims()[::-1], host.output_dims()[::-1]).compose(raw, front=not front)
    np.testing.assert_allclose(actual.data, reference.data, atol=2e-15, rtol=0)
    assert actual.input_dims() == reference.input_dims()[::-1]
    assert actual.output_dims() == reference.output_dims()[::-1]
