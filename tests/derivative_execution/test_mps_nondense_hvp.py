# Copyright 2026 QuantumBridge Contributors.
# Licensed under the Apache License, Version 2.0.
"""Actual 100-qubit Device derivative path with separate budget boundaries."""

from dataclasses import replace

import numpy as np
import pytest

from quantumbridge import Hamiltonian, PauliZ, StatevectorDevice, DensityMatrixDevice, MatrixProductStateDevice
from quantumbridge.execution import DerivativeExecutionRequest as Request, UnifiedExecutionLimits as Limits
from quantumbridge.information.matrix_product_state import MatrixProductState
from quantumbridge.qml import QNode
from quantumbridge.transforms import TransformProgram, merge_rotations, split_non_commuting


def test_100_qubit_device_hvp_has_no_dense_path_and_real_budget_boundaries(monkeypatch):
    def forbidden(*a, **k): pytest.fail("100-qubit derivative expanded a dense state")
    for cls, name in ((StatevectorDevice, "statevector"), (DensityMatrixDevice, "density_matrix"),
                      (MatrixProductState, "statevector"), (MatrixProductState, "reduced_density_matrix")):
        monkeypatch.setattr(cls, name, forbidden)
    def circuit(t, angle):
        t.h(0)
        for wire in range(99): t.cx(wire, wire+1)
        t.ry(angle, 99)
        return t.expval(Hamiltonian([(1., PauliZ(0).tensor(PauliZ(99))), (.2, PauliZ(0))]))
    device = MatrixProductStateDevice(max_bond_dim=4, max_memory_mb=2, cutoff=0)
    node = TransformProgram((merge_rotations, split_non_commuting))(QNode(circuit, 100, device=device, max_diff=2))
    request = Request(node, (.3,), derivative_order=2, derivative_kind="hvp", tangent=1.)
    result = device.execute_derivatives(request)
    assert result.code == 0
    np.testing.assert_allclose([result.value, result.derivative], [np.cos(.3), -np.cos(.3)], atol=1e-10)
    receipt = result.receipt
    assert receipt["live_memory_bytes"] == receipt["active_tapes"] == receipt["consumed_shots"] == 0
    assert receipt["consumed_tapes"] == result.metadata["second_order_work"]["tape_count"] == 8
    assert "mps_svd_allocator_peak" in receipt["unavailable"]
    assert "mps_svd_allocator_peak" not in receipt["observed_array_bytes"]
    evaluations = result.metadata["second_order_executions"][0]["second_order_evaluations"]
    for evaluation in evaluations:
        resources = evaluation["partitions"][0]["resources"]
        assert resources["max_bond_observed"] == 2
        assert resources["max_discarded_weight"] == resources["max_truncations"] == 0
        assert resources["max_tensor_bytes"] < receipt["peak_memory_bytes"]
    # A Device-local limit remains an independent constraint, not an addition
    # to the unified budget or a claim about observed allocator peak.
    small = MatrixProductStateDevice(max_bond_dim=4, max_memory_mb=.001, cutoff=0)
    failed = small.execute_derivatives(request, return_status=True)
    assert failed.code == 3 and failed.receipt["live_memory_bytes"] == 0
    # Preflight estimates and later retained-receipt high-water marks are
    # different: reject below the initial estimate before any child executes.
    boundary = receipt["estimated"]["memory_bytes"]-1
    monkeypatch.setattr(MatrixProductStateDevice, "_branches", forbidden)
    failed = device.execute_derivatives(replace(request, limits=Limits(max_total_memory_bytes=boundary)), return_status=True)
    assert failed.code == 3 and failed.receipt["consumed_tapes"] == 0
