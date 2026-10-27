# Copyright 2026 QuantumBridge Contributors. Apache-2.0.
"""Public 100-wire QNode derivatives against independent small-system data."""

import json
from pathlib import Path

import numpy as np
import pytest

import quantumbridge as qb
from quantumbridge.qml import QNode

ORACLE = json.loads((Path(__file__).parents[1] / "information/data/native_mixed_power_oracles.json").read_text())
MPS_ORACLE = json.loads((Path(__file__).parents[1] / "information/data/native_mps_power_oracles.json").read_text())


def build(power=0.5, active=99, method="best", **options):
    p, q = qb.Parameter("p"), qb.Parameter("q")
    body = qb.Circuit(1).rx(p, 0).rz(q, 0)
    source = qb.QuantumCircuit(100)
    source.append(body.to_gate().power(power, annotated=True), (active,))
    return source, QNode.from_circuit(source, qb.PauliZ(active), max_diff=2,
        diff_method=method, device=qb.MatrixProductStateDevice(max_bond_dim=4, cutoff=0), **options)


def forbid_dense(monkeypatch):
    from quantumbridge.core.gates import Gate
    from quantumbridge.information import MatrixProductState, Operator

    def forbidden(*a, **k):
        pytest.fail("Public 100-wire MPS derivative reached a dense-state entry")
    for cls, name in [(Gate, "to_matrix"), (Operator, "__init__"),
                      (MatrixProductState, "statevector"), (MatrixProductState, "reduced_density_matrix"),
                      (qb.StatevectorDevice, "statevector"), (qb.DensityMatrixDevice, "density_matrix")]:
        monkeypatch.setattr(cls, name, forbidden)


@pytest.mark.parametrize("active", [0, 99])
@pytest.mark.parametrize("case", ORACLE["su2"])
def test_public_mps_first_mixed_hessian_and_hvp_select_native_tangents(active, case, monkeypatch):
    source, node = build(case["power"], active)
    before = source.to_ir().to_json()
    forbid_dense(monkeypatch)
    point, direction = np.array(ORACLE["point"]), np.array([0.4, -0.3])
    assert node(point) == pytest.approx(case["value"], abs=8e-12)
    np.testing.assert_allclose(node.compute_jacobian(point), case["gradient"], atol=8e-11, rtol=0)
    np.testing.assert_allclose(node.compute_hessian(point), case["hessian"], atol=2e-9, rtol=0)
    monkeypatch.setattr(QNode, "compute_hessian", lambda *a, **k: pytest.fail("HVP requested a full Hessian"))
    np.testing.assert_allclose(node.compute_hvp(direction, point), np.array(case["hessian"]) @ direction, atol=2e-9, rtol=0)
    assert node.last_metadata["gradient_method"] == "mps-tangent"
    assert node.last_metadata["hvp_streamed"]
    assert source.to_ir().to_json() == before


@pytest.mark.parametrize("active", [0, 99])
@pytest.mark.parametrize("case", MPS_ORACLE["requested"])
def test_requested_noncommuting_three_rotation_body_and_local_complex_matrix(case, active, monkeypatch):
    p, q = qb.Parameter("p"), qb.Parameter("q")
    body = qb.Circuit(1).rx(p, 0).rz(q*q+0.4, 0).ry(-p, 0)
    source = qb.QuantumCircuit(100)
    source.append(body.to_gate().power(case["power"], annotated=True), (active,))
    before = source.to_ir().to_json()
    node = QNode.from_circuit(source, qb.PauliZ(active), max_diff=2,
        device=qb.MatrixProductStateDevice(max_bond_dim=4, cutoff=0))
    forbid_dense(monkeypatch)
    point, direction = np.array(MPS_ORACLE["point"]), np.array([0.4, -0.3])
    np.testing.assert_allclose(node(point), case["value"], atol=8e-12, rtol=0)
    np.testing.assert_allclose(node.compute_jacobian(point), case["gradient"], atol=8e-11, rtol=0)
    np.testing.assert_allclose(node.compute_hessian(point), case["hessian"], atol=3e-9, rtol=0)
    np.testing.assert_allclose(node.compute_hvp(direction, point), np.array(case["hessian"]) @ direction, atol=3e-9, rtol=0)
    np.testing.assert_allclose(node.compute_jvp(direction, point), np.array(case["gradient"]) @ direction, atol=8e-11, rtol=0)
    np.testing.assert_allclose(node.compute_vjp(0.7, point), 0.7*np.array(case["gradient"]), atol=8e-11, rtol=0)
    plan = node._construct((point,), {})
    bound = plan.circuit.bind(dict(zip(plan.recorder.parameters, plan.recorder.native_values())))
    from quantumbridge.utils.math import gate_matrix
    operation = bound.operations[0]
    encoded = np.array(case["matrix"])
    np.testing.assert_allclose(gate_matrix(operation.name, operation.params, operation.metadata),
        encoded[:, :, 0]+1j*encoded[:, :, 1], atol=8e-12, rtol=0)
    assert source.to_ir().to_json() == before


@pytest.mark.parametrize("active,target", [(0, 99), (99, 0), (1, 98), (98, 1)])
@pytest.mark.parametrize("case", [ORACLE["su2"][0], ORACLE["su2"][2]])
def test_remote_two_wire_gather_restore_keeps_actual_public_derivatives(active, target, case, monkeypatch):
    source, _ = build(case["power"], active)
    source.cx(active, target)
    node = QNode.from_circuit(source, qb.PauliZ(target), max_diff=2,
        device=qb.MatrixProductStateDevice(max_bond_dim=4, cutoff=0))
    forbid_dense(monkeypatch)
    point, direction = np.array(ORACLE["point"]), np.array([0.4, -0.3])
    np.testing.assert_allclose(node.compute_jacobian(point), case["gradient"], atol=8e-11, rtol=0)
    np.testing.assert_allclose(node.compute_hessian(point), case["hessian"], atol=2e-9, rtol=0)
    np.testing.assert_allclose(node.compute_hvp(direction, point), np.array(case["hessian"]) @ direction, atol=2e-9, rtol=0)
    assert node.last_metadata["mps_tangent_resources"]["max_bond_observed"] == 2


def test_eight_input_multilayer_streamed_hvp_under_hessian_budget_one(monkeypatch):
    from quantumbridge.diff import HigherOrderLimits

    parameters = qb.ParameterVector("angles", 8)
    source = qb.QuantumCircuit(100)
    for index in range(0, 8, 2):
        source.append(qb.Circuit(1).rx(parameters[index], 0).rz(parameters[index+1], 0)
            .to_gate().power(0.5, annotated=True), (99,))
    node = QNode.from_circuit(source, qb.PauliZ(99), max_diff=2,
        device=qb.MatrixProductStateDevice(max_bond_dim=4, cutoff=0),
        higher_order_limits=HigherOrderLimits(max_hessian_elements=1, max_adjoint_operations=100_000_000))
    forbid_dense(monkeypatch)
    monkeypatch.setattr(QNode, "compute_hessian", lambda *a, **k: pytest.fail("Eight-input HVP materialized a Hessian"))
    case = MPS_ORACLE["eight"]
    np.testing.assert_allclose(node(np.array(case["point"])), case["value"], atol=8e-12, rtol=0)
    np.testing.assert_allclose(node.compute_hvp(np.array(case["direction"]), np.array(case["point"])), case["hvp"], atol=3e-9, rtol=0)
    work = node.last_metadata["second_order_work"]
    assert work["direction_count"] == 8 and work["input_direction_columns"] == 1
    assert node.last_metadata["hvp_streamed"]


def test_mps_measurement_tree_variance_probabilities_and_live_observable_chain_rule(monkeypatch):
    from quantumbridge.diff.trace import flatten_tree

    _, base = build()
    def program(tape, x):
        base.fn(tape, x)
        return (tape.expval(qb.Hamiltonian([(0.7, qb.PauliZ(99)), (0.2, qb.PauliString([]))])),
                tape.var(qb.PauliZ(99)), tape.probs((99,)),
                tape.expval(qb.Hamiltonian([(x[0]*x[0], qb.PauliZ(99))])))
    node = QNode(program, 100, max_diff=2,
        device=qb.MatrixProductStateDevice(max_bond_dim=4, cutoff=0))
    forbid_dense(monkeypatch)
    case, x, d = ORACLE["su2"][0], np.array(ORACLE["point"]), np.array([0.4, -0.3])
    value, g, h = case["value"], np.array(case["gradient"]), np.array(case["hessian"])
    c, gc, hc = x[0]**2, np.array([2*x[0], 0]), np.diag([2., 0.])
    expected_first = np.stack([0.7*g, -2*value*g, 0.5*g, -0.5*g, c*g+value*gc])
    expected_second = np.stack([0.7*h, -2*(value*h+np.outer(g, g)), 0.5*h, -0.5*h,
        c*h+value*hc+np.outer(g, gc)+np.outer(gc, g)])
    np.testing.assert_allclose(flatten_tree(node(x))[0],
        [0.7*value+0.2, 1-value**2, (1+value)/2, (1-value)/2, c*value], atol=8e-12, rtol=0)
    np.testing.assert_allclose(flatten_tree(node.compute_jacobian(x))[0].reshape(5, 2), expected_first, atol=8e-11, rtol=0)
    np.testing.assert_allclose(flatten_tree(node.compute_hessian(x))[0].reshape(5, 2, 2), expected_second, atol=3e-9, rtol=0)
    np.testing.assert_allclose(flatten_tree(node.compute_hvp(d, x))[0].reshape(5, 2), expected_second @ d, atol=3e-9, rtol=0)


@pytest.mark.parametrize("kind", ["hessian", "hvp"])
def test_tangent_component_budget_rejects_before_every_mps_update(kind, monkeypatch):
    from quantumbridge.diff import HigherOrderLimits
    from quantumbridge.information import MatrixProductState

    p, q = qb.Parameter("p"), qb.Parameter("q")
    source = qb.QuantumCircuit(100)
    operation = qb.Circuit(1).rx(p, 0).rz(q, 0).to_gate().power(0.5, annotated=True)
    source.append(operation, (99,))
    source.append(operation, (99,))
    node = QNode.from_circuit(source, qb.PauliZ(99), max_diff=2,
        device=qb.MatrixProductStateDevice(max_bond_dim=4, cutoff=0),
        higher_order_limits=HigherOrderLimits(max_mps_tangent_components=1))
    before = source.to_ir().to_json()
    monkeypatch.setattr(MatrixProductState, "_apply", lambda *a, **k: pytest.fail("Budget refusal followed MPS execution"))
    with pytest.raises(MemoryError, match="max_mps_tangent_components"):
        if kind == "hessian":
            node.compute_hessian(np.array(ORACLE["point"]))
        else:
            node.compute_hvp(np.array([0.4, -0.3]), np.array(ORACLE["point"]))
    assert source.to_ir().to_json() == before
