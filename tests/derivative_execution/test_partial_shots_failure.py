# Copyright 2026 QuantumBridge Contributors.
# Licensed under the Apache License, Version 2.0.
"""Completed native samples cannot be lost when later processing/budgets fail."""

import numpy as np

from quantumbridge import Hamiltonian, PauliZ, StatevectorDevice
from quantumbridge.execution import DerivativeExecutionRequest as Request, UnifiedExecutionLimits as Limits, UnifiedResourceLedger as Ledger
from quantumbridge.qml import QNode
from quantumbridge.transforms import split_non_commuting


def test_peer_reservation_after_first_sampling_preserves_spent_shots_and_stops_children(monkeypatch):
    device = StatevectorDevice()
    def fn(t, x):
        t.ry(x, 0)
        return t.expval(PauliZ(0))
    node = QNode(fn, 1, shots=32, seed=17).with_transform(lambda tape:
        ((tape.copy(), tape.copy()), lambda values: (values[0]+values[1])/2))
    request = Request(node, (.3,), derivative_order=0, derivative_kind="value",
        limits=Limits(max_total_shots=64))
    parent, peer_reservations, samples = Ledger(Limits(max_total_shots=64)), [], []
    original = StatevectorDevice.sample
    def interleaved(self, circuit, *args, **kwargs):
        memory = original(self, circuit, *args, **kwargs)
        samples.append(len(memory))
        if len(samples) == 1:
            receipt = parent.receipt()
            available = 64-receipt["consumed_shots"]-receipt["reserved_shots"]
            peer_reservations.append(parent.reserve("independent_peer_request", shots=available))
        return memory
    monkeypatch.setattr(StatevectorDevice, "sample", interleaved)
    try:
        result = device.execute_derivatives(request, ledger=parent, return_status=True)
        assert result.code == 3 and result.value is None and result.derivative is None
        assert samples == [32], "a failed budget must stop later child Tapes"
        assert result.receipt["consumed_shots"] == parent.receipt()["consumed_shots"] == 32
        assert result.receipt["live_memory_bytes"] == result.receipt["reserved_shots"] == 0
    finally:
        for reservation in peer_reservations: reservation.release()
    assert parent.receipt()["reserved_shots"] == parent.receipt()["live_memory_bytes"] == 0
    recovered = device.execute_derivatives(request)
    assert recovered.code == 0 and recovered.receipt["consumed_shots"] == 64
    assert samples == [32, 32, 32] and np.isfinite(recovered.value)


def test_post_sample_statistics_failure_keeps_completed_shots_and_releases(monkeypatch):
    from quantumbridge.qml.pauli_group import PauliGroupResult
    def fn(t, x):
        t.ry(x, 0)
        return t.expval(Hamiltonian([(1., PauliZ(0)), (.2, PauliZ(1))]))
    node = split_non_commuting(QNode(fn, 2, shots=32, seed=17))
    request = Request(node, (.3,), derivative_order=0, derivative_kind="value")
    with monkeypatch.context() as context:
        def fail_after_sample(self): raise MemoryError("injected statistics allocation failure after sampling")
        context.setattr(PauliGroupResult, "metadata", fail_after_sample)
        result = node.device.execute_derivatives(request, return_status=True)
        assert result.code == 3 and result.value is None
        assert result.receipt["consumed_shots"] == 32
        assert result.receipt["live_memory_bytes"] == result.receipt["reserved_shots"] == 0
    recovered = node.device.execute_derivatives(request)
    assert recovered.code == 0 and recovered.receipt["consumed_shots"] == 32


def test_direct_native_sample_scope_preserves_zero_shots_and_rejects_before_dispatch(monkeypatch):
    from quantumbridge import Circuit, DensityMatrixDevice
    from quantumbridge.execution import ResourceLimitError
    from quantumbridge.execution.resource_context import ResourceScope
    import pytest
    device, circuit = DensityMatrixDevice(), Circuit(1).h(0)
    ledger = Ledger(Limits(max_total_shots=4))
    with ResourceScope(ledger):
        assert device.sample(circuit, shots=0) == []
        assert len(device.sample(circuit, shots=4, seed=2)) == 4
        def forbidden(*a, **k): pytest.fail("shot budget must reject before native state allocation")
        monkeypatch.setattr(DensityMatrixDevice, "_prepare", forbidden)
        with pytest.raises(ResourceLimitError): device.sample(circuit, shots=1)
    assert ledger.receipt()["consumed_shots"] == 4 and ledger.receipt()["reserved_shots"] == 0


def test_unknown_internal_failed_sampling_is_marked_unavailable_not_fabricated(monkeypatch):
    from quantumbridge import Circuit
    from quantumbridge.execution.resource_context import ResourceScope
    import pytest
    ledger = Ledger()
    def fail(*a, **k): raise RuntimeError("injected sampler failure before complete buffer")
    monkeypatch.setattr(StatevectorDevice, "statevector", fail)
    with ResourceScope(ledger):
        with pytest.raises(RuntimeError): StatevectorDevice().sample(Circuit(1), shots=4)
    receipt = ledger.receipt()
    assert receipt["consumed_shots"] == receipt["reserved_shots"] == 0
    assert "failed_native_sample_completion" in receipt["unavailable"]
