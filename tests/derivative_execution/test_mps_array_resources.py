# Copyright 2026 QuantumBridge Contributors.
# Licensed under the Apache License, Version 2.0.
"""Known native MPS buffers reserve before contraction/decomposition."""

import gc
import weakref

import numpy as np
import pytest

from quantumbridge.execution import UnifiedExecutionLimits as Limits, UnifiedResourceLedger as Ledger
from quantumbridge.execution.array_ownership import native_storage_bytes
from quantumbridge.execution.resource_context import ResourceScope
from quantumbridge.execution import mps_arrays as arrays
from quantumbridge.information.matrix_product_state import MatrixProductState
from quantumbridge.utils.math import gate_matrix


def entangled_state():
    vector = np.zeros(16, complex)
    vector[0] = vector[-1] = 1/np.sqrt(2)
    state = MatrixProductState.from_statevector(vector, max_bond_dim=2, cutoff=0)
    state._move_center(1)
    return state


def test_two_site_contraction_rejects_before_numpy_allocation(monkeypatch):
    state, calls = entangled_state(), []
    left, right = state._tensors[1:3]
    output_bytes = left.shape[0]*4*right.shape[2]*np.dtype(complex).itemsize
    assert output_bytes > max(left.nbytes, right.nbytes)
    inputs = native_storage_bytes(state._tensors)
    ledger = Ledger(Limits(max_total_memory_bytes=inputs+output_bytes-1))
    def forbidden(*a, **k):
        calls.append("contraction")
        pytest.fail("MPS contraction executed before its output reservation")
    monkeypatch.setattr(np, "tensordot", forbidden)
    monkeypatch.setattr(np, "matmul", forbidden)
    monkeypatch.setattr(np, "einsum", forbidden)
    with ledger.reserve("existing_caller_mps_inputs", memory_bytes=inputs), ResourceScope(ledger):
        with pytest.raises(MemoryError):
            state._block_gate(gate_matrix("cx"), 1, 2)
        assert calls == []
        assert ledger.receipt()["live_memory_bytes"] == inputs
    assert ledger.receipt()["live_memory_bytes"] == 0


@pytest.mark.parametrize("kind", ["qr", "svd"])
@pytest.mark.parametrize("shape", [(6, 3), (3, 6)])
@pytest.mark.parametrize("dtype", [np.float32, np.float64, np.complex64, np.complex128])
def test_decomposition_outputs_have_separate_leases_retained_by_views(kind, shape, dtype):
    matrix = np.arange(np.prod(shape), dtype=float).reshape(shape)+np.eye(*shape)
    if np.dtype(dtype).kind == "c": matrix = matrix+1j*matrix[::-1]
    matrix = matrix.astype(dtype)
    ledger = Ledger()
    with ResourceScope(ledger):
        outputs = arrays.decomposed(matrix, kind)
    rebuilt = outputs[0] @ outputs[1] if kind == "qr" else (outputs[0]*outputs[1]) @ outputs[2]
    np.testing.assert_allclose(rebuilt, matrix, atol=2e-5 if matrix.dtype in (np.dtype("float32"), np.dtype("complex64")) else 1e-11)
    assert ledger.receipt()["live_memory_bytes"] == sum(native_storage_bytes(value) for value in outputs)
    assert "mps_lapack_allocator_workspace" in ledger.receipt()["unavailable"]
    assert "mps_lapack_allocator_workspace" not in ledger.receipt()["observed_array_bytes"]
    reference, view = weakref.ref(outputs[0]), outputs[0][:, :1]
    retained = native_storage_bytes(outputs[0])
    del outputs
    gc.collect()
    assert reference() is not None and ledger.receipt()["live_memory_bytes"] == retained
    del view
    gc.collect()
    assert reference() is None and ledger.receipt()["live_memory_bytes"] == 0
    receipt = ledger.receipt()
    assert receipt["total_reserved_memory_bytes"] == receipt["total_released_memory_bytes"]


def test_strided_contraction_preserves_dtype_order_and_releases_workspace():
    left = np.arange(24., dtype=np.float32).reshape(2, 3, 4)[:, :, ::-1]
    right = np.arange(40., dtype=np.float32).reshape(4, 2, 5)[::-1]
    expected, ledger = np.tensordot(left, right, axes=1), Ledger()
    with ResourceScope(ledger):
        result = arrays.contracted(left, right)
    np.testing.assert_array_equal(result, expected)
    assert result.dtype == np.dtype("float32")
    assert ledger.receipt()["live_memory_bytes"] == result.nbytes
    del result
    assert ledger.receipt()["live_memory_bytes"] == 0


def test_noncontiguous_reshape_copy_denies_before_allocating(monkeypatch):
    source = np.arange(60.).reshape(5, 3, 4)[:, ::2]
    ledger = Ledger(Limits(max_total_memory_bytes=source.nbytes-1))
    monkeypatch.setattr(np, "empty", lambda *a, **k: pytest.fail("unreserved MPS reshape copy"))
    with ResourceScope(ledger), pytest.raises(MemoryError):
        arrays.reshaped(source, (5, 8))
    assert ledger.receipt()["live_memory_bytes"] == 0


def test_svd_failure_releases_output_tickets_without_changing_the_state(monkeypatch):
    state = entangled_state()
    expected = state.statevector()
    ledger = Ledger()
    def failed(*a, **k): raise np.linalg.LinAlgError("injected decomposition failure")
    monkeypatch.setattr(np.linalg, "svd", failed)
    with ResourceScope(ledger), pytest.raises(np.linalg.LinAlgError):
        state.apply(gate_matrix("cx"), [1, 2])
    gc.collect()
    assert ledger.receipt()["live_memory_bytes"] == 0
    np.testing.assert_array_equal(state.statevector(), expected)


def test_failed_second_swap_rolls_back_and_next_valid_operation_recovers(monkeypatch):
    state = entangled_state()
    expected = state.statevector()
    ledger, tickets, calls = Ledger(Limits(max_total_memory_bytes=100_000)), [], []
    original = MatrixProductState._block_gate
    def injected(self, matrix, start, width):
        calls.append((start, width))
        if len(calls) == 2:
            tickets.append(ledger.reserve("peer_pressure", memory_bytes=100_000-ledger.receipt()["live_memory_bytes"]))
        return original(self, matrix, start, width)
    with monkeypatch.context() as context:
        context.setattr(MatrixProductState, "_block_gate", injected)
        try:
            with ResourceScope(ledger), pytest.raises(MemoryError):
                state.apply(gate_matrix("cx"), [0, 3])
        finally:
            for ticket in tickets: ticket.release()
    gc.collect()
    assert len(calls) == 2 and ledger.receipt()["live_memory_bytes"] == 0
    np.testing.assert_array_equal(state.statevector(), expected)
    with ResourceScope(ledger):
        state.apply(gate_matrix("x"), [0])
    np.testing.assert_allclose(np.linalg.norm(state.statevector()), 1., atol=1e-12)
    assert ledger.receipt()["live_memory_bytes"] == native_storage_bytes(state._tensors)
    del state
    gc.collect()
    assert ledger.receipt()["live_memory_bytes"] == 0


def test_constructed_mps_and_exported_tensor_views_retain_real_storage():
    ledger = Ledger()
    with ResourceScope(ledger):
        state = MatrixProductState.from_statevector(np.array([1., 0., 0., 1.])/np.sqrt(2))
        exported = state.tensors
    assert ledger.receipt()["live_memory_bytes"] == native_storage_bytes((state._tensors, exported))
    view = exported[0][:, :, :1]
    retained = native_storage_bytes(exported[0])
    del exported, state
    gc.collect()
    assert ledger.receipt()["live_memory_bytes"] == retained
    del view
    gc.collect()
    assert ledger.receipt()["live_memory_bytes"] == 0


def test_output_shape_overflow_denies_before_numpy(monkeypatch):
    monkeypatch.setattr(np, "empty", lambda *a, **k: pytest.fail("overflow allocated an MPS array"))
    with ResourceScope(Ledger()), pytest.raises(MemoryError):
        arrays.owned("mps_overflow", (2**62, 4), complex)


def test_weak_root_metadata_does_not_keep_arrays_or_accounts_alive():
    ledger = Ledger()
    with ResourceScope(ledger):
        result = arrays.copied(np.ones(8, complex))
    key = id(result)
    result_reference, ledger_reference = weakref.ref(result), weakref.ref(ledger)
    assert arrays.owner_account(result) is ledger
    del ledger
    gc.collect()
    assert ledger_reference() is not None
    del result
    gc.collect()
    assert result_reference() is None and ledger_reference() is None
    assert key not in arrays._owners


def test_concurrent_requests_copy_shared_input_and_keep_only_returned_storage():
    from concurrent.futures import ThreadPoolExecutor
    source, parent = entangled_state(), Ledger()
    unchanged = source.statevector()
    def execute(angle):
        account = Ledger(parent=parent)
        with ResourceScope(account):
            state = source.copy()
            state.apply(gate_matrix("ry", (angle,)), [0])
            value = state.statevector()
        return value, account
    with ThreadPoolExecutor(max_workers=2) as executor:
        results = list(executor.map(execute, (.2, .7)))
    np.testing.assert_array_equal(source.statevector(), unchanged)
    assert not np.shares_memory(results[0][0], results[1][0])
    for value, account in results:
        assert np.linalg.norm(value) == pytest.approx(1.)
        assert account.receipt()["live_memory_bytes"] == value.nbytes
    del value, account
    assert parent.receipt()["live_memory_bytes"] == 2*unchanged.nbytes
    results.clear()
    gc.collect()
    assert parent.receipt()["live_memory_bytes"] == 0


def test_native_result_and_exported_tensor_view_outlive_device_and_result():
    from quantumbridge import Circuit, MatrixProductStateDevice
    device, ledger = MatrixProductStateDevice(max_bond_dim=2), Ledger()
    with ResourceScope(ledger):
        result = device.run(Circuit(4).h(0).cx(0, 3))
    stored = native_storage_bytes(result.mps._tensors)
    assert ledger.receipt()["live_memory_bytes"] == stored
    # Defensive exports outside the callback inherit their actual source
    # account, not a new global ledger or an uncharged native copy.
    exported = result.matrix_product_state()
    tensor = exported.tensors[1]
    view = tensor[:, :, :1]
    retained = native_storage_bytes(tensor)
    assert ledger.receipt()["live_memory_bytes"] > stored
    del tensor, exported, result, device
    gc.collect()
    assert ledger.receipt()["live_memory_bytes"] == retained
    np.testing.assert_allclose(np.linalg.norm(view), 1., atol=1e-12)
    del view
    gc.collect()
    assert ledger.receipt()["live_memory_bytes"] == 0


def test_external_workspace_policy_does_not_reserve_known_tensors_twice():
    from quantumbridge import Circuit, MatrixProductStateDevice
    from quantumbridge.execution.derivative_planning import device_working_bytes
    circuit, device = Circuit(4).h(0).cx(0, 3), MatrixProductStateDevice(max_bond_dim=2)
    estimate = device_working_bytes(device, circuit)
    external = device_working_bytes(device, circuit, mps_external_only=True)
    assert estimate > external > 0
    assert external == 128*(2*2)**2


def test_managed_kraus_products_are_reserved_before_matmul(monkeypatch):
    from quantumbridge import MatrixProductStateDevice
    state = MatrixProductState.zero(1)
    density, operator = np.eye(2, dtype=complex)/2, np.eye(2, dtype=complex)
    monkeypatch.setattr(state, "reduced_density_matrix", lambda wires: density)
    calls = []
    def forbidden(*a, **k):
        calls.append("matmul")
        pytest.fail("Kraus product was not reserved")
    monkeypatch.setattr(np, "matmul", forbidden)
    ledger = Ledger(Limits(max_total_memory_bytes=63))
    with ResourceScope(ledger), pytest.raises(MemoryError):
        MatrixProductStateDevice._kraus_choices(state, [operator], [0])
    assert calls == [] and ledger.receipt()["live_memory_bytes"] == 0


def test_foreign_mps_conversion_rejects_before_running_user_protocols():
    from quantumbridge.core.classical import UnsupportedFeature
    calls = []
    class Foreign:
        def __getattribute__(self, key):
            calls.append(key)
            return object.__getattribute__(self, key)
        def __complex__(self):
            calls.append("complex")
            return 1j
    foreign = Foreign()
    objects = np.empty(2, object)
    objects.fill(foreign)
    ledger = Ledger()
    for source in (foreign, objects):
        with ResourceScope(ledger), pytest.raises(UnsupportedFeature):
            arrays.numeric(source)
    assert calls == [] and ledger.receipt()["live_memory_bytes"] == 0


def test_svd_input_and_all_outputs_must_fit_before_lapack_is_called(monkeypatch):
    state, calls = entangled_state(), []
    block = np.tensordot(*state._tensors[1:3], axes=1)
    matrix = block.reshape(block.shape[0]*2, -1)
    rows, columns = matrix.shape
    rank = min(rows, columns)
    expected = (rows*rank+rank*columns)*matrix.dtype.itemsize+rank*np.dtype(float).itemsize
    inputs = native_storage_bytes((state._tensors, block))
    ledger = Ledger(Limits(max_total_memory_bytes=inputs+expected-1))
    def forbidden(*a, **k):
        calls.append("svd")
        pytest.fail("SVD executed before its simultaneous output reservation")
    monkeypatch.setattr(np.linalg, "svd", forbidden)
    with ledger.reserve("existing_caller_mps_inputs", memory_bytes=inputs), ResourceScope(ledger):
        with pytest.raises(MemoryError):
            state._split(1, 2, block)
        assert calls == []
        assert ledger.receipt()["live_memory_bytes"] == inputs
    assert ledger.receipt()["live_memory_bytes"] == 0
