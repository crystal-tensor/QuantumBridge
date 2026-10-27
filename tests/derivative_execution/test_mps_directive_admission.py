# Copyright 2026 QuantumBridge Contributors. Apache-2.0.
"""Noiseless directives must not invent MPS Schmidt-rank growth."""

import json
from pathlib import Path
from types import SimpleNamespace

import numpy as np
import pytest

import quantumbridge as qb
from quantumbridge.diff.mps_derivatives import _bond_bound
from quantumbridge.execution import DerivativeExecutionRequest as Request, UnifiedExecutionLimits as Limits
from quantumbridge.execution.derivative_planning import device_working_bytes
from quantumbridge.information import MatrixProductState
from quantumbridge.qml import QNode

ORACLE = json.loads((Path(__file__).parents[1] / "information/data/native_mixed_power_oracles.json").read_text())


def source(directives):
    p, q = qb.Parameter("p"), qb.Parameter("q")
    circuit = qb.QuantumCircuit(100)
    circuit.append(qb.Circuit(1).rx(p, 0).rz(q, 0).to_gate().power(0.5, annotated=True), (99,))
    if directives:
        circuit.barrier()
        circuit.delay(3, 99)
        circuit.barrier(*reversed(range(100)))
    return circuit


@pytest.mark.parametrize("cap", [None, 4])
@pytest.mark.parametrize("external_only", [False, True])
def test_directives_leave_both_resource_bounds_equal_to_the_same_unitaries(cap, external_only):
    device = qb.MatrixProductStateDevice(max_bond_dim=cap, cutoff=0)
    # Admission sees the lowered native operation store. Public Instruction
    # handles are covered separately by the end-to-end QNode test below.
    plain = qb.Circuit(100).rx(0.3, 99)
    annotated = plain.copy().barrier().delay(3, 99).barrier(*reversed(range(100)))
    assert _bond_bound(device, annotated) == _bond_bound(device, plain)
    assert device_working_bytes(device, annotated, mps_external_only=external_only) == device_working_bytes(
        device, plain, mps_external_only=external_only)


def test_unknown_directive_is_not_assumed_to_be_a_noop():
    operation = SimpleNamespace(name="opaque", wires=tuple(range(100)), controls=(),
        targets=tuple(range(100)), metadata={"directive": True})
    circuit = SimpleNamespace(num_qubits=100, operations=[operation])
    device = qb.MatrixProductStateDevice(max_bond_dim=None, cutoff=0)
    assert _bond_bound(device, circuit)[0] > 1
    assert device_working_bytes(device, circuit) > 64*1024*1024


def test_public_hvp_with_wide_barriers_has_no_false_exponential_resource_refusal(monkeypatch):
    node = QNode.from_circuit(source(True), qb.PauliZ(99), max_diff=2,
        device=qb.MatrixProductStateDevice(max_bond_dim=None, cutoff=0))
    monkeypatch.setattr(MatrixProductState, "statevector", lambda *a, **k: pytest.fail("Dense MPS materialization"))
    point, direction = np.array(ORACLE["point"]), np.array([0.4, -0.3])
    actual = node.compute_hvp(direction, point)
    np.testing.assert_allclose(actual, np.array(ORACLE["su2"][0]["hessian"]) @ direction, atol=2e-9, rtol=0)
    assert node.last_metadata["mps_tangent_work"]["mps_bond_bound"] == 1


@pytest.mark.parametrize("field", ["max_derivative_work", "max_total_memory_bytes", "max_total_tapes"])
@pytest.mark.parametrize("kind,order", [("jacobian", 1), ("hvp", 2)])
def test_directive_bound_fix_does_not_bypass_shared_resource_admission(field, kind, order, monkeypatch):
    circuit = source(True)
    before = circuit.to_ir().to_json()
    node = QNode.from_circuit(circuit, qb.PauliZ(99), max_diff=2,
        device=qb.MatrixProductStateDevice(max_bond_dim=None, cutoff=0))
    node.device.last_execution_metadata = {"sentinel": "unchanged"}
    monkeypatch.setattr(MatrixProductState, "_apply", lambda *a, **k: pytest.fail("MPS update before admission"))
    result = node.device.execute_derivatives(Request(node, (np.array(ORACLE["point"]),),
        derivative_kind=kind, derivative_order=order, tangent=np.array([0.4, -0.3]),
        limits=Limits(**{field: 0})), return_status=True)
    assert result.code == 3
    assert result.receipt["consumed_tapes"] == result.receipt["consumed_shots"] == 0
    assert result.receipt["consumed_derivative_work"] == 0
    assert result.receipt["live_memory_bytes"] == 0
    assert node.device.last_execution_metadata == {"sentinel": "unchanged"}
    assert circuit.to_ir().to_json() == before


@pytest.mark.parametrize("direction", [np.ones(3), np.array([0.4+0.1j, -0.3])])
def test_wide_directive_malformed_direction_is_atomic_before_mps_update(direction, monkeypatch):
    circuit = source(True)
    before = circuit.to_ir().to_json()
    node = QNode.from_circuit(circuit, qb.PauliZ(99), max_diff=2,
        device=qb.MatrixProductStateDevice(max_bond_dim=None, cutoff=0))
    node.device.last_execution_metadata = {"sentinel": "unchanged"}
    monkeypatch.setattr(MatrixProductState, "_apply", lambda *a, **k: pytest.fail("Invalid direction followed simulation"))
    result = node.device.execute_derivatives(Request(node, (np.array(ORACLE["point"]),),
        derivative_kind="hvp", derivative_order=2, tangent=direction), return_status=True)
    assert result.code == 1
    assert result.receipt["consumed_tapes"] == result.receipt["consumed_shots"] == 0
    assert result.receipt["consumed_derivative_work"] == 0
    assert result.receipt["live_memory_bytes"] == 0
    assert node.device.last_execution_metadata == {"sentinel": "unchanged"}
    assert circuit.to_ir().to_json() == before
