# Copyright 2026 QuantumBridge Contributors. Apache-2.0.
"""Original symbolic sources through standard native IR/QPY to MPS jets."""

import json
from pathlib import Path

import numpy as np
import pytest

import quantumbridge as qb
from quantumbridge.qml import QNode

ORACLE = json.loads((Path(__file__).parents[1] / "information/data/native_mixed_power_oracles.json").read_text())


@pytest.mark.parametrize("format", ["ir", "qpy"])
@pytest.mark.parametrize("control", [0, 1])
@pytest.mark.parametrize("case", ORACLE["two_wire"][:2])
def test_unbound_vector_control_phase_roundtrip_reaches_actual_100_wire_mps_derivatives(format, control, case, monkeypatch):
    from quantumbridge.compat.qiskit_adapter import circuit_from_ir
    from quantumbridge.core.gates import Gate
    from quantumbridge.information import MatrixProductState, Operator
    from quantumbridge.ir.qb_ir import IRProgram
    from quantumbridge.serialization import qpy_dumps, qpy_loads

    p, q = qb.ParameterVector("angles", 2)
    body = qb.Circuit(2).rx(p, 0).rz(q, 1).rxx(p*q, 0, 1)
    body.global_phase = 0.13*p*q
    source = qb.QuantumCircuit(100)
    source.h(0)
    source.append(body.to_gate().power(case["power"], annotated=True).control(ctrl_state=control), (0, 1, 99))
    before = source.to_ir().to_json()
    restored = circuit_from_ir(IRProgram.from_json(before)) if format == "ir" else qpy_loads(qpy_dumps(source))[0]
    assert [parameter.uuid for parameter in source.parameters] == [parameter.uuid for parameter in restored.parameters]
    assert "native_matrix_power" not in before
    assert source.to_ir().to_json() == before
    def forbidden(*a, **k):
        pytest.fail("100-wire restored MPS path reached a dense entry")
    for cls, name in [(Gate, "to_matrix"), (Operator, "__init__"),
                      (MatrixProductState, "statevector"), (MatrixProductState, "reduced_density_matrix"),
                      (qb.StatevectorDevice, "statevector"), (qb.DensityMatrixDevice, "density_matrix")]:
        monkeypatch.setattr(cls, name, forbidden)
    node = QNode.from_circuit(restored, qb.PauliX(0), max_diff=2,
        device=qb.MatrixProductStateDevice(max_bond_dim=8, cutoff=0))
    expected, point, direction = case["controlled"], np.array(ORACLE["point"]), np.array([0.4, -0.3])
    np.testing.assert_allclose(node(point), expected["value"], atol=2e-11, rtol=0)
    np.testing.assert_allclose(node.compute_jacobian(point), expected["gradient"], atol=2e-10, rtol=0)
    np.testing.assert_allclose(node.compute_hessian(point), expected["hessian"], atol=3e-9, rtol=0)
    monkeypatch.setattr(QNode, "compute_hessian", lambda *a, **k: pytest.fail("Restored HVP built full Hessian"))
    np.testing.assert_allclose(node.compute_hvp(direction, point), np.array(expected["hessian"]) @ direction, atol=3e-9, rtol=0)
    assert node.last_metadata["gradient_method"] == "mps-tangent"
    assert node.last_metadata["mps_tangent_resources"]["max_bond_observed"] <= 8
