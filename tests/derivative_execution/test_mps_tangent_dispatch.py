# Copyright 2026 QuantumBridge Contributors. Apache-2.0.
"""Direct Device admission uses the same native MPS method/work planning."""

import gc
import json
from pathlib import Path

import numpy as np
import pytest

import quantumbridge as qb
from quantumbridge.execution import DerivativeExecutionRequest as Request, UnifiedExecutionLimits as Limits, UnifiedResourceLedger as Ledger
from quantumbridge.information import MatrixProductState
from quantumbridge.qml import QNode

ORACLE = json.loads((Path(__file__).parents[1] / "information/data/native_mixed_power_oracles.json").read_text())


def node_for(**options):
    p, q = qb.Parameter("p"), qb.Parameter("q")
    source = qb.QuantumCircuit(100)
    source.append(qb.Circuit(1).rx(p, 0).rz(q, 0).to_gate().power(0.5, annotated=True), (99,))
    node = QNode.from_circuit(source, qb.PauliZ(99), max_diff=2,
        device=qb.MatrixProductStateDevice(max_bond_dim=4, cutoff=0), **options)
    return source, node


@pytest.mark.parametrize("kind,order", [("jacobian", 1), ("hessian", 2), ("hvp", 2)])
@pytest.mark.parametrize("method", ["best", "mps-tangent"])
def test_device_protocol_selects_same_actual_mps_algorithm_and_consumes_its_work(kind, order, method):
    _, node = node_for()
    point, direction, ledger = np.array(ORACLE["point"]), np.array([0.4, -0.3]), Ledger()
    result = node.device.execute_derivatives(Request(node, (point,), derivative_kind=kind,
        derivative_order=order, tangent=direction, method=method), ledger=ledger)
    expected = np.array(ORACLE["su2"][0]["gradient" if kind == "jacobian" else "hessian"])
    if kind == "hvp":
        expected = expected @ direction
    assert result.code == 0
    np.testing.assert_allclose(result.derivative, expected, atol=2e-9, rtol=0)
    assert result.metadata["gradient_method"] == "mps-tangent"
    work = result.metadata["mps_tangent_work"]
    assert result.receipt["consumed_tapes"] == work["tape_count"]
    assert result.receipt["consumed_derivative_work"] == work["adjoint_operations"]
    assert result.receipt["consumed_shots"] == 0
    del result
    gc.collect()
    assert ledger.receipt()["live_memory_bytes"] == 0


@pytest.mark.parametrize("field", ["max_derivative_work", "max_total_memory_bytes", "max_total_tapes"])
@pytest.mark.parametrize("kind,order", [("jacobian", 1), ("hessian", 2), ("hvp", 2)])
def test_shared_device_budget_refuses_before_first_mps_update_and_preserves_owner(field, kind, order, monkeypatch):
    source, node = node_for()
    before = source.to_ir().to_json()
    node.device.last_execution_metadata = {"sentinel": "unchanged"}
    monkeypatch.setattr(MatrixProductState, "_apply", lambda *a, **k: pytest.fail("Unadmitted MPS update"))
    result = node.device.execute_derivatives(Request(node, (np.array(ORACLE["point"]),),
        derivative_kind=kind, derivative_order=order, tangent=np.array([0.4, -0.3]),
        limits=Limits(**{field: 0})), return_status=True)
    assert result.code == 3
    assert result.receipt["consumed_tapes"] == result.receipt["consumed_shots"] == 0
    assert result.receipt["live_memory_bytes"] == 0
    assert node.device.last_execution_metadata == {"sentinel": "unchanged"}
    assert source.to_ir().to_json() == before


def test_non_moving_mps_gates_keep_existing_best_shift_schedule():
    node = QNode(lambda tape, x: (tape.ry(x, 99), tape.expval(qb.PauliZ(99)))[1], 100,
        device=qb.MatrixProductStateDevice(max_bond_dim=2, cutoff=0), max_diff=2)
    node.compute_hvp(0.4, 0.37)
    assert node.last_metadata["gradient_method"] == "parameter-shift"
    assert node.last_metadata["shifted_evaluation_count"] > 0


@pytest.mark.parametrize("offset", [-1e-4, 1e-4])
def test_near_cut_jet_refuses_before_device_update_with_real_numerical_diagnostics(offset, monkeypatch):
    p, q = qb.Parameter("p"), qb.Parameter("q")
    source = qb.QuantumCircuit(100)
    source.h(0)
    source.append(qb.Circuit(1).ry(-p, 0).rz(q, 0).ry(p, 0).to_gate()
        .power(0.5, annotated=True).control(), (0, 99))
    node = QNode.from_circuit(source, qb.PauliX(0), max_diff=2,
        device=qb.MatrixProductStateDevice(max_bond_dim=4, cutoff=0))
    before = source.to_ir().to_json()
    node.device.last_execution_metadata = {"sentinel": True}
    monkeypatch.setattr(MatrixProductState, "_apply", lambda *a, **k: pytest.fail("Unreliable jet followed simulation"))
    with pytest.raises(np.linalg.LinAlgError, match="gap=.*coupling.*resolution=.*screen=") as failed:
        node.compute_hvp(np.array([0.4, -0.3]), np.array([0.37, 2*np.pi+offset]))
    diagnostics = failed.value.diagnostics
    assert 0 < diagnostics["gap"] < 1e-3
    assert diagnostics["screen"] > diagnostics["threshold"]
    assert diagnostics["coupling"] >= 0 and diagnostics["resolution"] > 0
    assert node.device.last_execution_metadata == {"sentinel": True}
    assert source.to_ir().to_json() == before
