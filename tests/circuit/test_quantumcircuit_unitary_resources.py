# Copyright 2026 QuantumBridge Contributors. Apache-2.0.
"""Public wrappers retain existing native matrix leases and rejection rules."""

import gc
from concurrent.futures import ThreadPoolExecutor
from threading import Event

import numpy as np
import pytest

import quantumbridge as qb
from quantumbridge.core.gate_limits import GateCircuitLimits, gate_circuit_scope
from quantumbridge.core.standard_gates import UnitaryGate
from quantumbridge.execution.resource_context import ResourceScope
from quantumbridge.execution.resource_ledger import UnifiedResourceLedger
from quantumbridge.execution.resource_limits import UnifiedExecutionLimits


def test_public_unitary_owned_roots_copy_inverse_and_release():
    ledger = UnifiedResourceLedger()
    with ResourceScope(ledger):
        source = qb.QuantumCircuit(1)
        source.unitary(np.diag([1., 1j]), [0])
        assert ledger.receipt()["live_memory_bytes"] == 64
        copied = source.copy()
        assert ledger.receipt()["live_memory_bytes"] == 128
        inverse = source.inverse()
        assert ledger.receipt()["live_memory_bytes"] == 192
    np.testing.assert_allclose(qb.StatevectorDevice().statevector(inverse), [1., 0.], atol=2e-12, rtol=0)
    del source, copied, inverse
    gc.collect()
    assert ledger.receipt()["live_memory_bytes"] == 0


def test_public_unitary_rejects_local_size_before_numeric_copy(monkeypatch):
    from quantumbridge.execution import array_reservations

    source = qb.QuantumCircuit(2)
    before = source.to_ir().to_json()
    monkeypatch.setattr(array_reservations, "numeric_array",
        lambda *args, **kwargs: pytest.fail("Oversize public matrix allocated a numeric copy"))
    with gate_circuit_scope(GateCircuitLimits(max_matrix_dimension=2)), pytest.raises(MemoryError, match="max_matrix_dimension"):
        source.unitary(np.eye(4), [0, 1])
    assert source.to_ir().to_json() == before


def test_public_unitary_foreign_matrix_owner_hooks_do_not_execute():
    calls = []

    class Foreign(UnitaryGate):
        def to_matrix(self):
            calls.append("to_matrix")
            return np.eye(2)

    owner = object.__new__(Foreign)
    source = qb.QuantumCircuit(1)
    with pytest.raises(ValueError):
        source.unitary(owner, [0])
    assert not calls and len(source.data) == 0


def test_public_unitary_resource_failure_then_recovery_has_no_partial_store():
    source = qb.QuantumCircuit(2)
    before = source.to_ir().to_json()
    parent = UnifiedResourceLedger(UnifiedExecutionLimits(max_total_memory_bytes=255))
    child = UnifiedResourceLedger(parent=parent)
    with ResourceScope(child), pytest.raises(MemoryError):
        source.unitary(np.eye(4), [0, 1])
    assert source.to_ir().to_json() == before
    assert parent.receipt()["live_memory_bytes"] == child.receipt()["live_memory_bytes"] == 0
    source.unitary(np.eye(4), [0, 1])
    assert len(source.operations) == len(source.data) == 1


def test_independent_public_appends_compete_in_shared_parent_and_release():
    pilot = UnifiedResourceLedger()
    with ResourceScope(pilot):
        probe = qb.QuantumCircuit(1)
        probe.unitary(np.eye(2), [0])
    peak = pilot.receipt()["peak_memory_bytes"]
    del probe
    gc.collect()
    parent = UnifiedResourceLedger(UnifiedExecutionLimits(max_total_memory_bytes=peak + 32))
    first_child, second_child = UnifiedResourceLedger(parent=parent), UnifiedResourceLedger(parent=parent)
    entered, release = Event(), Event()

    def held():
        with ResourceScope(first_child):
            source = qb.QuantumCircuit(1)
            source.unitary(np.eye(2), [0])
            entered.set()
            assert release.wait(30)
            assert len(source.data) == 1

    def refused():
        source = qb.QuantumCircuit(1)
        with ResourceScope(second_child), pytest.raises(MemoryError):
            source.unitary(np.eye(2), [0])
        assert not source.operations

    with ThreadPoolExecutor(max_workers=2) as workers:
        first = workers.submit(held)
        try:
            assert entered.wait(30)
            workers.submit(refused).result(timeout=20)
        finally:
            release.set()
        first.result(timeout=30)
    gc.collect()
    assert parent.receipt()["live_memory_bytes"] == 0


def test_readonly_execution_of_one_public_matrix_snapshot_is_reentrant():
    source = qb.QuantumCircuit(2)
    source.h(0)
    source.unitary(np.diag([1., 1j, -1., -1j]), [1, 0])
    before = source.to_ir().to_json()
    expected = qb.StatevectorDevice().statevector(source)
    with ThreadPoolExecutor(max_workers=2) as workers:
        results = list(workers.map(lambda _: qb.StatevectorDevice().statevector(source), range(4)))
    for actual in results:
        np.testing.assert_allclose(actual, expected, atol=2e-12, rtol=0)
    assert source.to_ir().to_json() == before


@pytest.mark.parametrize("layout", ["c", "f", "strided", "subclass"])
def test_readonly_numeric_buffers_keep_existing_owned_copy_admission(layout):
    rng = np.random.default_rng(9595)
    matrix, _ = np.linalg.qr(rng.normal(size=(4, 4)) + 1j * rng.normal(size=(4, 4)))
    if layout == "strided":
        buffer = np.zeros((8, 8), complex)
        raw = buffer[::2, ::2]
        raw[:] = matrix
    elif layout == "subclass":
        class NumericBuffer(np.ndarray): pass
        raw = matrix.copy().view(NumericBuffer)
    else: raw = np.array(matrix, order=layout.upper(), copy=True)
    raw.flags.writeable = False
    ledger = UnifiedResourceLedger()
    with ResourceScope(ledger):
        source = qb.QuantumCircuit(2)
        source.unitary(raw, [1, 0])
    owner = source.data[0].operation
    assert ledger.receipt()["live_memory_bytes"] == 256
    assert not raw.flags.writeable and not np.shares_memory(owner.params[0], raw)
    if layout == "strided": buffer[:] = 0
    np.testing.assert_allclose(qb.StatevectorDevice().statevector(source), matrix[:, 0], atol=3e-12, rtol=0)
    np.testing.assert_array_equal(owner.to_matrix(), matrix)
    del source, owner
    gc.collect()
    assert ledger.receipt()["live_memory_bytes"] == 0
