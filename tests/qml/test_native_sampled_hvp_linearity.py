# Copyright 2026 QuantumBridge Contributors.
# Licensed under the Apache License, Version 2.0.
# Direction-independent signed-shift streams define a real sampled linear map.

import numpy as np
import pytest

from quantumbridge import Hamiltonian, PauliX, PauliZ
from quantumbridge.qml import QNode
from quantumbridge.transforms import split_non_commuting


@pytest.mark.parametrize("policy", [None, "uniform", "weighted"])
def test_sampled_hvp_is_linear_in_direction_with_fixed_shot_vector_streams(policy):
    def circuit(t, x):
        t.ry(x[0], 0); t.rx(x[1], 0); t.phase(.2, 0)
        return t.expval(Hamiltonian([(.7, PauliX(0)), (.2, PauliZ(0))]))
    node = split_non_commuting(QNode(circuit, 1, max_diff=2, shots=[4000, 6000], seed=71), shot_dist=policy)
    point = np.array([.37, .2])
    first = np.asarray(node.compute_hvp(np.array([1., 0.]), point))
    first_work = node.last_metadata["second_order_work"]
    other = np.asarray(node.compute_hvp(np.array([0., 1.]), point))
    np.testing.assert_allclose(node.compute_hvp(np.array([1., 1.]), point), first+other, atol=1e-12, rtol=0)
    np.testing.assert_allclose(node.compute_hvp(np.array([-.3, .4]), point), -.3*first+.4*other, atol=1e-12, rtol=0)
    np.testing.assert_array_equal(node.compute_hvp(np.zeros(2), point), np.zeros((2, 2)))
    assert node.last_metadata["second_order_work"] == first_work
    receipts = node.last_metadata["second_order_executions"]
    assert all(child["second_order_work"]["direction_independent_sampling_schedule"] for child in receipts)
    assert node.last_metadata["total_physical_shots"] > 0


def test_zero_weight_sampled_group_does_not_bypass_allocation_derivative_rejection(monkeypatch):
    from quantumbridge import UnsupportedFeature
    from quantumbridge.transforms.program import TransformError
    def circuit(t, x):
        t.h(0)
        return t.expval(Hamiltonian([(x, PauliX(0))]))
    node = split_non_commuting(QNode(circuit, 1, max_diff=2, shots=100, seed=7), shot_dist="weighted")
    monkeypatch.setattr(node.device, "sample", lambda *a, **k: pytest.fail("zero-group allocation derivative must reject before execution"))
    with pytest.raises(TransformError, match="zero-weight trainable") as caught:
        node.compute_hvp(1., 0.)
    assert isinstance(caught.value.__cause__, UnsupportedFeature)


def test_pure_classical_identity_sum_needs_no_sampled_quantum_group(monkeypatch):
    from quantumbridge import PauliString
    def circuit(t, x):
        return t.expval(Hamiltonian([(x*x, PauliString([(0, "I")]))]))
    node = split_non_commuting(QNode(circuit, 1, max_diff=2, shots=100, seed=7), shot_dist="weighted")
    monkeypatch.setattr(node.device, "sample", lambda *a, **k: pytest.fail("identity-only derivatives require no quantum shots"))
    np.testing.assert_allclose(node.compute_hvp(.4, .3), .8, atol=1e-12)
    assert node.last_metadata["executed_tape_count"] == node.last_metadata["total_physical_shots"] == 0


def test_fixed_sampling_schedule_tracks_dependencies_not_constant_angles(monkeypatch):
    from quantumbridge.diff.qnode_engine import ExecutionPlan
    original = ExecutionPlan.shift_recipe
    def recipe(self, operation, value):
        assert operation.name != "phase", "a fixed numerical angle must not acquire an irrelevant derivative recipe"
        return original(self, operation, value)
    monkeypatch.setattr(ExecutionPlan, "shift_recipe", recipe)
    def circuit(t, x):
        t.ry(x[0]**2, 0); t.rx(x[1], 0); t.phase(.2, 0)
        return t.expval(PauliZ(0))
    node = QNode(circuit, 1, max_diff=2, shots=10000, seed=18)
    point = np.array([0., .2])
    first = node.compute_hvp(np.array([1., 0.]), point)
    work = node.last_metadata["second_order_work"]
    other = node.compute_hvp(np.array([0., 1.]), point)
    np.testing.assert_allclose(node.compute_hvp(np.ones(2), point), first+other, atol=1e-12, rtol=0)
    node.compute_hvp(np.zeros(2), point)
    assert node.last_metadata["second_order_work"] == work
