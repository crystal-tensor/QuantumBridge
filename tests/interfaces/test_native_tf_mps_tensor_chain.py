# Copyright 2026 QuantumBridge Contributors. Apache-2.0.
"""Real MPS contractions, with independent native dense and tangent oracles."""

import numpy as np
import pytest

import quantumbridge as qb
from quantumbridge.qml import QNode

tf = pytest.importorskip("tensorflow")
POINT = np.array([0.37, -0.41])
DIRECTION = np.array([0.4, -0.3])
WEIGHTS = np.array([0.7, -0.2])


def build(width, *, interface="numpy", device=None, **options):
    p, q = qb.ParameterVector("mps_angles", 2)
    body = qb.Circuit(1).rx(p, 0).rz(q, 0)
    body.global_phase = 0.04*p*q
    source = qb.QuantumCircuit(width)
    source.h(0)
    source.append(body.to_gate().power(0.5, annotated=True), (width-1,))
    source.cx(0, width-1)
    source.ry(0.7*p, 0)
    source.rz(q, width-1)
    source.global_phase = 0.17+p*q*0.03
    base = QNode.from_circuit(source, qb.PauliZ(width-1), max_diff=2)
    def program(tape, point):
        first = base.fn(tape, point)
        return first, tape.expval(qb.PauliX(0).tensor(qb.PauliX(width-1)))
    return source, QNode(program, width, interface=interface, max_diff=2,
        device=device or qb.MatrixProductStateDevice(max_bond_dim=16, cutoff=0), **options)


def no_dense_or_host(monkeypatch):
    from quantumbridge.interfaces.native_host import NativeHostKernel
    from quantumbridge.interfaces.tensorflow_graph import TensorFlowGraphKernel
    from quantumbridge.information import MatrixProductState, Operator
    def forbidden(*args, **kwargs):
        pytest.fail("TF MPS used a host quantum callback or full-state dense conversion")
    for cls, method in ((NativeHostKernel, "run"), (NativeHostKernel, "run_second"),
            (TensorFlowGraphKernel, "evaluate"), (MatrixProductState, "statevector"),
            (MatrixProductState, "reduced_density_matrix"), (MatrixProductState, "from_statevector"),
            (qb.StatevectorDevice, "statevector"), (qb.DensityMatrixDevice, "density_matrix"),
            (Operator, "__init__")):
        monkeypatch.setattr(cls, method, forbidden)
    monkeypatch.setattr(tf, "numpy_function", forbidden)
    monkeypatch.setattr(tf, "py_function", forbidden)


@pytest.mark.parametrize("width", [2, 4, 6])
def test_exact_chain_primal_full_j_h_and_existing_tangent(width, monkeypatch):
    from quantumbridge.interfaces.tensorflow_mps_execution import TensorFlowMPSPlan
    source, native = build(width)
    dense = QNode(native.fn, width, max_diff=2, device=qb.StatevectorDevice())
    expected = np.array(dense(POINT))
    expected_j = np.array(dense.jacobian(POINT, method="adjoint"))
    expected_h = np.array(dense.hessian(POINT, method="adjoint"))
    np.testing.assert_allclose(native(POINT), expected, atol=2e-12, rtol=0)
    np.testing.assert_allclose(native.jacobian(POINT, method="mps-tangent"), expected_j, atol=2e-10, rtol=0)
    np.testing.assert_allclose(native.hessian(POINT, method="mps-tangent"), expected_h, atol=2e-9, rtol=0)
    # The physical amplitudes additionally detect lost global complex phase.
    plan = native._construct((POINT,), {})
    tensor_plan = TensorFlowMPSPlan(plan)
    angles = plan.recorder.native_values()
    expected_state = qb.StatevectorDevice().statevector(plan.circuit,
        dict(zip(plan.recorder.parameters, angles)))
    np.testing.assert_allclose(expected_state, qb.StatevectorDevice().statevector(source,
        dict(zip(source.parameters, POINT))), atol=2e-12, rtol=0)
    chain, scale = tensor_plan.chain(tf.constant(angles, tf.float64))
    assert len(chain) == width
    amplitudes = chain[0]
    for tensor in chain[1:]:
        amplitudes = tf.tensordot(amplitudes, tensor, axes=([-1], [0]))
    np.testing.assert_allclose(tf.reshape(amplitudes, (-1,))*scale, expected_state, atol=2e-12, rtol=0)
    node = QNode(native.fn, width, interface="tensorflow", max_diff=2,
        device=qb.MatrixProductStateDevice(max_bond_dim=16, cutoff=0))
    before = source.to_ir().to_json()
    no_dense_or_host(monkeypatch)
    x = tf.constant(POINT, tf.float64)
    with tf.GradientTape(persistent=True) as second:
        second.watch(x)
        with tf.GradientTape(persistent=True) as first:
            first.watch(x)
            y = tf.stack(node(x))
        j = first.jacobian(y, x, experimental_use_pfor=False)
    h = second.jacobian(j, x, experimental_use_pfor=False)
    np.testing.assert_allclose(y, expected, atol=2e-12, rtol=0)
    np.testing.assert_allclose(j, expected_j, atol=2e-10, rtol=0)
    np.testing.assert_allclose(h, expected_h, atol=2e-9, rtol=0)
    assert node.last_metadata["tensor_plan_work"]["physical_tensor_count"] == width
    assert source.to_ir().to_json() == before


@pytest.mark.parametrize("loss_kind", ["square", "exponential_cubic"])
def test_public_mps_two_loss_mixed_modes_and_streamed_directions(loss_kind, monkeypatch):
    _, dense = build(4, device=qb.StatevectorDevice())
    y, j, h = np.array(dense(POINT)), np.array(dense.jacobian(POINT)), np.array(dense.hessian(POINT))
    first, second = (2*(y-0.3), np.full(2, 2.)) if loss_kind == "square" else (np.exp(y)+0.6*y*y, np.exp(y)+1.2*y)
    expected_h = j.T @ np.diag(WEIGHTS*second) @ j+np.einsum("i,ijk->jk", WEIGHTS*first, h)
    _, node = build(4, interface="tensorflow")
    no_dense_or_host(monkeypatch)
    def loss(x):
        value = tf.stack(node(x))
        terms = (value-0.3)**2 if loss_kind == "square" else tf.exp(value)+0.2*value**3
        return tf.reduce_sum(tf.constant(WEIGHTS, tf.float64)*terms)
    @tf.function(autograph=False)
    def graph(x, d):
        with tf.autodiff.ForwardAccumulator(x, d) as forward:
            with tf.GradientTape() as reverse:
                reverse.watch(x)
                value = loss(x)
            g = reverse.gradient(value, x)
        for_value = forward.jvp(g)
        with tf.GradientTape() as reverse:
            reverse.watch(x)
            with tf.autodiff.ForwardAccumulator(x, d) as forward:
                value = loss(x)
            tangent = forward.jvp(value)
        rof_value = reverse.gradient(tangent, x)
        with tf.GradientTape() as reverse:
            reverse.watch(x)
            value = tf.stack(node(x))
        vjp = reverse.gradient(value, x, output_gradients=tf.constant(WEIGHTS, tf.float64))
        with tf.autodiff.ForwardAccumulator(x, d) as forward:
            value = tf.stack(node(x))
        return for_value, rof_value, vjp, forward.jvp(value)
    for direction in (DIRECTION, -DIRECTION, np.zeros(2)):
        actual = graph(tf.constant(POINT), tf.constant(direction))
        for result, reference in zip(actual, (expected_h @ direction, expected_h @ direction,
                j.T @ WEIGHTS, j @ direction)):
            assert result is not None
            np.testing.assert_allclose(result, reference, atol=2e-9, rtol=0)
    assert graph.experimental_get_tracing_count() == 1
    definition = graph.get_concrete_function(tf.TensorSpec((2,), tf.float64),
        tf.TensorSpec((2,), tf.float64)).graph.as_graph_def()
    operations = {n.op for n in definition.node}
    operations.update(n.op for f in definition.library.function for n in f.node_def)
    assert not operations & {"PyFunc", "PyFuncStateless", "EagerPyFunc", "Svd", "Qr", "StopGradient"}


def test_real_100_wire_remote_entanglement_primal_jacobian_streamed_hvp(monkeypatch):
    from quantumbridge.diff.higher_order_limits import HigherOrderLimits
    from quantumbridge.interfaces.tensorflow_mps_execution import TensorFlowMPSPlan
    _, dense = build(2, device=qb.StatevectorDevice())
    y, j, h = np.array(dense(POINT)), np.array(dense.jacobian(POINT)), np.array(dense.hessian(POINT))
    source, node = build(100, interface="tensorflow",
        higher_order_limits=HigherOrderLimits(max_hessian_elements=1))
    plan = node._construct((POINT,), {})
    chain_plan = TensorFlowMPSPlan(plan)
    no_dense_or_host(monkeypatch)
    chain, scale = chain_plan.chain(tf.constant(plan.recorder.native_values(), tf.float64))
    assert len(chain) == 100
    assert max(tensor.shape[2] for tensor in chain) == 4
    assert chain[0].shape[0] == chain[-1].shape[-1] == 1
    assert chain_plan.work["mps_routed_two_site_steps"] == 197
    from quantumbridge.core.parameters import resolve_parameter
    compiled_phase = resolve_parameter(plan.circuit.global_phase,
        dict(zip(plan.recorder.parameters, plan.recorder.native_values())))
    # Basis translation moves fixed/local phase into the compiled global scale.
    np.testing.assert_allclose(scale, np.exp(1j*compiled_phase), atol=2e-14, rtol=0)
    @tf.function(autograph=False)
    def graph(x, direction):
        with tf.autodiff.ForwardAccumulator(x, direction) as forward:
            with tf.GradientTape(persistent=True) as reverse:
                reverse.watch(x)
                values = tf.stack(node(x))
            gradient = reverse.gradient(values, x, output_gradients=tf.constant(WEIGHTS))
        product = forward.jvp(gradient)
        jacobian = reverse.jacobian(values, x, experimental_use_pfor=False)
        return values, jacobian, product
    for direction in (DIRECTION, np.zeros(2)):
        actual = graph(tf.constant(POINT), tf.constant(direction))
        for result, reference in zip(actual, (y, j, np.einsum("i,ijk,k->j", WEIGHTS, h, direction))):
            assert result is not None
            np.testing.assert_allclose(result, reference, atol=2e-9, rtol=0)
    work = node.last_metadata["tensor_plan_work"]
    assert source.num_qubits == work["physical_tensor_count"] == 100
    assert work["mps_bond_bound"] == 4 and not work["truncation"]
    assert work["host_quantum_calls"] == 0
