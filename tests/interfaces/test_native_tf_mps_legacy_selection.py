# Copyright 2026 QuantumBridge Contributors. Apache-2.0.
"""Protect old MPS APIs outside the newly admitted tensor specialization."""

import numpy as np
import pytest

import quantumbridge as qb
from quantumbridge.qml import QNode

tf = pytest.importorskip("tensorflow")


@pytest.mark.parametrize("kind,powered", [("expval", False), ("var", False),
    ("probs", False), ("var", True), ("probs", True)])
def test_existing_mps_queries_keep_their_existing_method_contract(kind, powered):
    p = qb.Parameter("angle")
    source = qb.QuantumCircuit(2)
    source.append(qb.Circuit(1).rx(p, 0).rz(.3*p, 0).to_gate().power(0.5, annotated=True), (0,))
    base = QNode.from_circuit(source, qb.PauliZ(0), max_diff=2)
    def program(tape, point):
        if powered:
            base.fn(tape, (point,))
        else:
            tape.ry(point, 0)
        if kind == "probs":
            return tape.probs(wires=(0,))
        return getattr(tape, kind)(qb.PauliZ(0))
    node = QNode(program, 2, interface="tensorflow", max_diff=2,
        device=qb.MatrixProductStateDevice(cutoff=0, max_bond_dim=4))
    x = tf.constant(0.37, tf.float64)
    weights = tf.constant([0.7, -0.2] if kind == "probs" else [1.], tf.float64)
    with tf.GradientTape() as tape:
        tape.watch(x)
        value = tf.stack(tf.nest.flatten(node(x)))
        loss = tf.reduce_sum(value*weights)
    gradient = tape.gradient(loss, x)
    scale = .5 if powered else 1.
    angle = .37*scale
    expected = [np.cos(angle)] if kind == "expval" else [np.sin(angle)**2] if kind == "var" else [np.cos(angle/2)**2, np.sin(angle/2)**2]
    first = scale*(-np.sin(angle) if kind == "expval" else np.sin(2*angle) if kind == "var" else -.45*np.sin(angle))
    if powered:
        native = QNode(program, 2, max_diff=2, device=qb.MatrixProductStateDevice(cutoff=0, max_bond_dim=4))
        expected = tf.nest.flatten(native(.37))
        first = np.array(tf.nest.flatten(native.jacobian(.37, method="mps-tangent"))) @ weights.numpy()
    np.testing.assert_allclose(value, expected, atol=2e-12, rtol=0)
    np.testing.assert_allclose(gradient, first, atol=2e-11, rtol=0)
    assert not node.last_metadata.get("native_tensor_execution", False)
    assert node.last_metadata["gradient_method"] == ("mps-tangent" if powered else "parameter-shift")


@pytest.mark.parametrize("feature", ["resource", "tensorflow_native_source_identity"])
def test_tensor_capability_selection_never_falls_back_on_fatal_errors(feature, monkeypatch):
    from quantumbridge.core.classical import UnsupportedFeature
    from quantumbridge.interfaces.tensorflow_mps_execution import TensorFlowMPSPlan
    from quantumbridge.interfaces.native_host import NativeHostKernel
    p, q = qb.ParameterVector("fatal", 2)
    source = qb.QuantumCircuit(2)
    source.append(qb.Circuit(1).rx(p, 0).rz(q, 0).to_gate().power(.5, annotated=True), (1,))
    node = QNode.from_circuit(source, qb.PauliZ(1), interface="tensorflow", max_diff=2,
        device=qb.MatrixProductStateDevice(cutoff=0, max_bond_dim=4))
    def fail(*args, **kwargs):
        if feature == "resource":
            raise MemoryError("injected resource refusal")
        raise UnsupportedFeature(feature, "injected source identity refusal")
    monkeypatch.setattr(TensorFlowMPSPlan, "__init__", fail)
    monkeypatch.setattr(NativeHostKernel, "run", lambda *a: pytest.fail("Fatal tensor refusal entered host math"))
    with pytest.raises(MemoryError if feature == "resource" else UnsupportedFeature, match="injected"):
        node(tf.constant([.37, -.41], tf.float64))


def test_existing_two_qubit_power_retains_native_host_math_when_tensor_domain_misses():
    p, q = qb.ParameterVector("legacy", 2)
    body = qb.Circuit(2).rx(p, 0).rz(q, 0).ry(.3*p, 1)
    body.global_phase = 0.23
    source = qb.QuantumCircuit(2)
    source.append(body.to_gate().power(0.5, annotated=True), (0, 1))
    device = qb.MatrixProductStateDevice(cutoff=0, max_bond_dim=4)
    native = QNode.from_circuit(source, qb.PauliZ(1), max_diff=2, device=device)
    node = QNode.from_circuit(source, qb.PauliZ(1), interface="tensorflow", max_diff=2, device=device)
    point = tf.constant([.37, -.41], tf.float64)
    reference = native(point.numpy())
    reference_gradient = native.jacobian(point.numpy(), method="mps-tangent")
    with tf.GradientTape() as tape:
        tape.watch(point)
        baseline, status = node.tensorflow_with_status(point)
    np.testing.assert_allclose(baseline, reference, atol=2e-12, rtol=0)
    np.testing.assert_allclose(tape.gradient(baseline, point), reference_gradient, atol=2e-10, rtol=0)
    assert int(status) == 0
    with tf.GradientTape() as tape:
        tape.watch(point)
        value = node(point)
    gradient = tape.gradient(value, point)
    np.testing.assert_allclose(value, reference, atol=2e-12, rtol=0)
    np.testing.assert_allclose(gradient, reference_gradient, atol=2e-10, rtol=0)
    assert not node.last_metadata.get("native_tensor_execution", False)
