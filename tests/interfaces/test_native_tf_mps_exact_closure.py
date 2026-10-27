# Copyright 2026 QuantumBridge Contributors. Apache-2.0.
"""Existing native local matrix semantics must close under exact TF MPS."""

import numpy as np
import pytest

import quantumbridge as qb
from quantumbridge.qml import QNode
from quantumbridge.utils.math import gate_matrix

tf = pytest.importorskip("tensorflow")
POINT = np.array([.37, -.41])


def fixture(width=6, local_width=1, *, interface="numpy"):
    p, q = qb.ParameterVector("closure", 2)
    body = qb.Circuit(1).rx(p, 0).rz(q, 0)
    body.global_phase = .04*p*q
    source = qb.Circuit(width)
    source.h(0)
    source.append(body.to_gate().power(.5, annotated=True), (width-1,))
    matrix = (gate_matrix("sx") @ gate_matrix("rz", (.29,))*np.exp(.13j)
        if local_width == 1 else gate_matrix("ecr") @ gate_matrix("swap")*np.exp(-.07j))
    wires = (0,) if local_width == 1 else (width-1, 0)
    source.unitary(matrix, wires)
    source.cx(0, width-1)
    source.ry(.4*p, 0)
    source.global_phase = .17+.03*p*q
    base = QNode.from_circuit(source, qb.PauliZ(width-1), max_diff=2)
    observable = qb.Hamiltonian([(.4, qb.PauliString(())),
        (.7, qb.PauliX(0).tensor(qb.PauliX(width-1))), (-.2, qb.PauliY(0))])
    def program(tape, point):
        first = base.fn(tape, point)
        return first, tape.expval(observable)
    node = QNode(program, width, interface=interface, max_diff=2,
        device=qb.MatrixProductStateDevice(max_bond_dim=16, cutoff=0))
    return source, node


@pytest.mark.parametrize("local_width", [1, 2])
def test_existing_one_two_site_unitary_primal_and_phase_has_tensor_rule(local_width, record_property):
    from quantumbridge.interfaces.tensorflow_mps_execution import TensorFlowMPSPlan
    source, node = fixture(local_width=local_width)
    plan = node._construct((POINT,), {})
    actual_local = [op for op in plan.circuit.operations if op.name == "unitary"]
    assert len(actual_local) == 1 and len(actual_local[0].wires) == local_width
    record_property("actual_lowered_names", ",".join(op.name for op in plan.circuit.operations))
    record_property("local_matrix_wire_order", str(actual_local[0].wires))
    angles = plan.recorder.native_values()
    dense = qb.StatevectorDevice()
    expected = dense.statevector(plan.circuit, dict(zip(plan.recorder.parameters, angles)))
    np.testing.assert_allclose(expected, dense.statevector(source,
        dict(zip(source.parameters, POINT))), atol=2e-12, rtol=0)
    mps = node.device.matrix_product_state(plan.circuit, dict(zip(plan.recorder.parameters, angles)))
    np.testing.assert_allclose(mps.statevector(), expected, atol=2e-12, rtol=0)
    tensor = TensorFlowMPSPlan(plan)
    chain, scale = tensor.chain(tf.constant(angles, tf.float64))
    actual = chain[0]
    for site in chain[1:]:
        actual = tf.tensordot(actual, site, axes=([-1], [0]))
    np.testing.assert_allclose(tf.reshape(actual, (-1,))*scale, expected, atol=2e-12, rtol=0)


@pytest.mark.parametrize("width", [2, 4, 6])
@pytest.mark.parametrize("local_width", [1, 2])
def test_fixed_native_unitary_complete_public_jacobian_and_hessian(width, local_width, monkeypatch):
    from test_native_tf_mps_tensor_chain import no_dense_or_host
    source, native = fixture(width, local_width)
    dense = QNode(native.fn, width, max_diff=2, device=qb.StatevectorDevice())
    expected = np.array(dense(POINT))
    expected_j = np.array(dense.jacobian(POINT, method="adjoint"))
    expected_h = np.array(dense.hessian(POINT, method="adjoint"))
    np.testing.assert_allclose(native(POINT), expected, atol=2e-12, rtol=0)
    np.testing.assert_allclose(native.jacobian(POINT, method="mps-tangent"), expected_j, atol=2e-10, rtol=0)
    np.testing.assert_allclose(native.hessian(POINT, method="mps-tangent"), expected_h, atol=2e-9, rtol=0)
    node = QNode(native.fn, width, max_diff=2, interface="tensorflow",
        device=qb.MatrixProductStateDevice(max_bond_dim=16, cutoff=0))
    before = source.to_ir().to_json()
    no_dense_or_host(monkeypatch)
    x = tf.constant(POINT)
    with tf.GradientTape(persistent=True) as second:
        second.watch(x)
        with tf.GradientTape(persistent=True) as first:
            first.watch(x)
            value = tf.stack(node(x))
        j = first.jacobian(value, x, experimental_use_pfor=False)
    h = second.jacobian(j, x, experimental_use_pfor=False)
    for actual, reference in zip((value, j, h), (expected, expected_j, expected_h)):
        np.testing.assert_allclose(actual, reference, atol=2e-9, rtol=0)
    assert node.last_metadata["native_tensor_execution"]
    assert source.to_ir().to_json() == before


@pytest.mark.parametrize("loss_kind", ["square", "exponential_cubic"])
def test_fixed_two_site_unitary_mixed_chain_rule_streams_all_quantum_curvature(loss_kind, monkeypatch):
    from test_native_tf_mps_tensor_chain import no_dense_or_host
    _, native = fixture(4, 2)
    dense = QNode(native.fn, 4, max_diff=2, device=qb.StatevectorDevice())
    y, j, h = np.array(dense(POINT)), np.array(dense.jacobian(POINT)), np.array(dense.hessian(POINT))
    weights = np.array([.7, -.2])
    first, second = (2*(y-.3), np.full(2, 2.)) if loss_kind == "square" else (np.exp(y)+.6*y*y, np.exp(y)+1.2*y)
    expected_h = j.T @ np.diag(weights*second) @ j+np.einsum("i,ijk->jk", weights*first, h)
    node = QNode(native.fn, 4, max_diff=2, interface="tensorflow",
        device=qb.MatrixProductStateDevice(max_bond_dim=16, cutoff=0))
    no_dense_or_host(monkeypatch)
    monkeypatch.setattr(tf.GradientTape, "jacobian", lambda *a, **k: pytest.fail("A streamed closure HVP built a full Hessian"))
    def loss(x):
        value = tf.stack(node(x))
        terms = (value-.3)**2 if loss_kind == "square" else tf.exp(value)+.2*value**3
        return tf.reduce_sum(tf.constant(weights)*terms)
    @tf.function(autograph=False)
    def graph(x, direction):
        with tf.autodiff.ForwardAccumulator(x, direction) as forward:
            with tf.GradientTape() as reverse:
                reverse.watch(x)
                value = loss(x)
            gradient = reverse.gradient(value, x)
        for_value = forward.jvp(gradient)
        with tf.GradientTape() as reverse:
            reverse.watch(x)
            with tf.autodiff.ForwardAccumulator(x, direction) as forward:
                value = loss(x)
            tangent = forward.jvp(value)
        rof_value = reverse.gradient(tangent, x)
        with tf.GradientTape() as reverse:
            reverse.watch(x)
            value = tf.stack(node(x))
        vjp = reverse.gradient(value, x, output_gradients=tf.constant(weights))
        with tf.autodiff.ForwardAccumulator(x, direction) as forward:
            value = tf.stack(node(x))
        return for_value, rof_value, vjp, forward.jvp(value)
    for direction in (np.array([.4, -.3]), np.array([-.1, .8]), np.zeros(2)):
        result = graph(tf.constant(POINT), tf.constant(direction))
        for actual, reference in zip(result, (expected_h @ direction, expected_h @ direction, j.T @ weights, j @ direction)):
            assert actual is not None
            np.testing.assert_allclose(actual, reference, atol=2e-9, rtol=0)
    assert graph.experimental_get_tracing_count() == 1
    definition = graph.get_concrete_function(tf.TensorSpec((2,), tf.float64),
        tf.TensorSpec((2,), tf.float64)).graph.as_graph_def()
    operations = {n.op for n in definition.node}
    operations.update(n.op for f in definition.library.function for n in f.node_def)
    assert not operations & {"PyFunc", "EagerPyFunc", "PyFuncStateless", "Svd", "Qr", "StopGradient"}


@pytest.mark.parametrize("local_width", [1, 2])
def test_exact_tensor_rule_refuses_only_approximately_unitary_source_matrix(local_width):
    from quantumbridge.interfaces.tensorflow_mps_execution import TensorFlowMPSPlan
    p, q = qb.ParameterVector("near_unitary", 2)
    source = qb.Circuit(2)
    source.append(qb.Circuit(1).rx(p, 0).rz(q, 0).to_gate().power(.5, annotated=True), (1,))
    source.unitary((1+1e-7)*np.eye(1 << local_width), tuple(range(local_width)))
    native = QNode.from_circuit(source, qb.PauliZ(1), max_diff=2,
        device=qb.MatrixProductStateDevice(cutoff=0, max_bond_dim=4))
    # The Circuit builder's loose input screen is not execution admission.
    # Both existing native execution and the TF rule require strict unitarity.
    with pytest.raises(ValueError, match="unitar"):
        native(POINT)
    plan = native._construct((POINT,), {})
    with pytest.raises(ValueError, match="fixed primitive"):
        TensorFlowMPSPlan(plan)
