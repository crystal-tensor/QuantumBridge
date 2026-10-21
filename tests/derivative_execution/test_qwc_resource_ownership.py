# Copyright 2026 QuantumBridge Contributors.
# Licensed under the Apache License, Version 2.0.
"""Owned QWC payload, temporary statistics and copied receipt lifetimes."""

import numpy as np
import pytest
import gc

from quantumbridge import Circuit, Hamiltonian, PauliX, PauliZ, StatevectorDevice
from quantumbridge.execution import DerivativeExecutionRequest as Request, ResourceLimitError, UnifiedExecutionLimits as Limits, UnifiedResourceLedger as Ledger
from quantumbridge.execution.resource_context import ResourceScope, copy_execution_payload
from quantumbridge.qml import QNode
from quantumbridge.qml.pauli_group import PauliGroup, measure_pauli_group
from quantumbridge.transforms import split_non_commuting


def group():
    return PauliGroup((((0, "Z"),), ((1, "Z"),)), ((0, "Z"), (1, "Z")), (0, 1), ((1., .2),))


def test_sample_arrays_are_retained_while_statistics_workspace_releases():
    ledger = Ledger()
    with ResourceScope(ledger):
        result = measure_pauli_group(StatevectorDevice(), Circuit(2).h(0), group(), 32, 7)
        assert result.eigenvalues.shape == (32, 2)
        before = ledger.receipt()
        assert before["observed_array_bytes"]["qwc_retained_arrays_and_bitstrings"] == 656
        assert before["live_memory_bytes"] == 656
        result.metadata()
        assert ledger.receipt()["live_memory_bytes"] > before["live_memory_bytes"]
        assert ledger.receipt()["consumed_shots"] == 32
    receipt = ledger.receipt()
    assert receipt["live_memory_bytes"] == 0
    assert receipt["total_reserved_memory_bytes"] == receipt["total_released_memory_bytes"]
    assert "python_container_allocator_memory" in receipt["unavailable"]


def test_joint_statistics_budget_rejects_before_native_sampling(monkeypatch):
    ledger = Ledger(Limits(max_total_memory_bytes=700))
    def forbidden(*a, **k): pytest.fail("statistics workspace must reserve before sampling")
    monkeypatch.setattr(StatevectorDevice, "sample", forbidden)
    with pytest.raises(ResourceLimitError), ResourceScope(ledger):
        measure_pauli_group(StatevectorDevice(), Circuit(2), group(), 32, 7)
    assert ledger.receipt()["consumed_shots"] == ledger.receipt()["live_memory_bytes"] == 0


def test_covariance_array_reservation_precedes_analytic_allocation(monkeypatch):
    ledger = Ledger(Limits(max_total_memory_bytes=47))
    def forbidden(*a, **k): pytest.fail("covariance allocated before its reservation")
    monkeypatch.setattr(np, "empty", forbidden)
    monkeypatch.setattr(StatevectorDevice, "expectation", forbidden)
    with pytest.raises(ResourceLimitError), ResourceScope(ledger):
        measure_pauli_group(StatevectorDevice(), Circuit(2), group(), None, None)
    assert ledger.receipt()["live_memory_bytes"] == 0


def test_analytic_joint_covariance_and_sample_one_have_distinct_observations():
    ledger = Ledger()
    with ResourceScope(ledger):
        analytic = measure_pauli_group(StatevectorDevice(), Circuit(2), group(), None, None)
        assert analytic.sample_covariance is None and analytic.eigenvalues is None
        assert ledger.receipt()["live_memory_bytes"] == 48
        sampled = measure_pauli_group(StatevectorDevice(), Circuit(2), group(), 1, 7)
        assert sampled.sample_covariance is None
        assert ledger.receipt()["live_memory_bytes"] == 48+66
        np.testing.assert_allclose(sampled.covariance, np.zeros((2, 2)))


def test_copied_metadata_reserves_before_copy_and_retains_each_distinct_payload():
    payload = {"array": np.ones(4), "seeds": [3, 7], "provenance": "native"}
    ledger = Ledger()
    with ResourceScope(ledger):
        first = copy_execution_payload(payload)
        one = ledger.receipt()["live_memory_bytes"]
        second = copy_execution_payload(payload)
        assert not np.shares_memory(first["array"], second["array"])
        assert ledger.receipt()["live_memory_bytes"] == 2*one
    tight = Ledger(Limits(max_total_memory_bytes=one-1))
    with pytest.raises(ResourceLimitError), ResourceScope(tight): copy_execution_payload(payload)
    assert tight.receipt()["live_memory_bytes"] == 0


@pytest.mark.parametrize("policy", [None, "uniform", "weighted"])
def test_seeded_shot_vector_hvp_records_actual_qwc_calls_and_retained_payload(policy, monkeypatch):
    samples = []
    original = StatevectorDevice.sample
    def sampled(self, *args, **kwargs):
        result = original(self, *args, **kwargs)
        samples.append((len(result), kwargs["seed"]))
        return result
    monkeypatch.setattr(StatevectorDevice, "sample", sampled)
    def circuit(t, x):
        t.ry(x, 0)
        return t.expval(Hamiltonian([(1., PauliX(0)), (.3, PauliZ(0))]))
    node = split_non_commuting(QNode(circuit, 1, max_diff=2, shots=[101, (151, 2)], seed=17), shot_dist=policy)
    ledger = Ledger()
    result = node.device.execute_derivatives(Request(node, (.3,), derivative_order=2,
        derivative_kind="hvp", method="parameter-shift", tangent=.4), ledger=ledger)
    assert result.code == 0 and len(result.derivative) == 3
    assert sum(n for n, _ in samples) == result.receipt["consumed_shots"] == result.metadata["total_physical_shots"]
    assert len({seed for _, seed in samples}) == len(samples)
    assert result.receipt["observed_array_bytes"]["qwc_retained_arrays_and_bitstrings"] > 0
    assert result.receipt["observed_array_bytes"]["retained_receipt_payload"] > 0
    assert result.receipt["live_memory_bytes"] > 0 and result.receipt["reserved_shots"] == 0
    shots = ledger.receipt()["consumed_shots"]
    del result
    gc.collect()
    assert ledger.receipt()["live_memory_bytes"] == 0
    assert ledger.receipt()["consumed_shots"] == shots
