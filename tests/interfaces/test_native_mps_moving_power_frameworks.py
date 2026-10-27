# Copyright 2026 QuantumBridge Contributors. Apache-2.0.
"""Actual four-framework graphs through public 100-wire MPS QNodes."""

import json
from pathlib import Path

import numpy as np
import pytest

import quantumbridge as qb
from quantumbridge.qml import QNode

ORACLE = json.loads((Path(__file__).parents[1] / "information/data/native_mixed_power_oracles.json").read_text())


@pytest.mark.parametrize("case", ORACLE["su2"])
@pytest.mark.parametrize("interface", ["torch", "autograd", "jax", "tensorflow"])
@pytest.mark.parametrize("loss_kind", ["square", "exponential_cubic"])
def test_actual_100_wire_mps_graphs_first_mixed_second_hvp_jvp_vjp(case, interface, loss_kind, monkeypatch):
    from quantumbridge.core.gates import Gate
    from quantumbridge.information import MatrixProductState, Operator

    def forbidden(*a, **k):
        pytest.fail("Actual MPS framework graph fell back to a dense state or Gate")
    p, q = qb.Parameter("p"), qb.Parameter("q")
    source = qb.QuantumCircuit(100)
    source.append(qb.Circuit(1).rx(p, 0).rz(q, 0).to_gate().power(case["power"], annotated=True), (99,))
    node = QNode.from_circuit(source, qb.PauliZ(99), interface=interface, max_diff=2,
        device=qb.MatrixProductStateDevice(max_bond_dim=4, cutoff=0))
    for cls, name in [(Gate, "to_matrix"), (Operator, "__init__"),
                      (MatrixProductState, "statevector"), (MatrixProductState, "reduced_density_matrix"),
                      (qb.StatevectorDevice, "statevector"), (qb.DensityMatrixDevice, "density_matrix")]:
        monkeypatch.setattr(cls, name, forbidden)
    value, gradient, hessian = case["value"], np.array(case["gradient"]), np.array(case["hessian"])
    direction = np.array([0.4, -0.3])
    first_loss, second_loss = ((2*(value-0.3), 2.) if loss_kind == "square"
                              else (np.exp(value)+0.6*value**2, np.exp(value)+1.2*value))
    expected_second = first_loss*hessian+second_loss*np.outer(gradient, gradient)

    def loss(x):
        result = node(x)
        if loss_kind == "square":
            return (result-0.3)**2
        return exp(result)+0.2*result**3

    if interface == "torch":
        torch = pytest.importorskip("torch")
        exp = torch.exp
        x = torch.tensor(ORACLE["point"], dtype=torch.float64, requires_grad=True)
        d = torch.tensor(direction, dtype=torch.float64)
        first = torch.autograd.grad(node(x), x, create_graph=True)[0]
        mixed = torch.autograd.functional.hessian(loss, x).detach().numpy()
        product = torch.autograd.grad((torch.autograd.grad(loss(x), x, create_graph=True)[0]*d).sum(), x)[0].detach().numpy()
        raw, jvp = torch.autograd.functional.jvp(node, x, d)
        _, vjp = torch.autograd.functional.vjp(node, x, torch.tensor(0.7, dtype=torch.float64))
        raw, jvp, vjp, first = (a.detach().numpy() for a in (raw, jvp, vjp, first))
    elif interface == "autograd":
        ag = pytest.importorskip("autograd")
        anp = pytest.importorskip("autograd.numpy")
        exp = anp.exp
        x = anp.array(ORACLE["point"])
        first, mixed = ag.grad(node)(x), ag.hessian(loss)(x)
        product = ag.grad(lambda a: anp.dot(ag.grad(loss)(a), direction))(x)
        raw, jvp = ag.make_jvp(node)(x)(direction)
        pullback, _ = ag.make_vjp(node)(x)
        vjp = pullback(0.7)
        forward_reverse = ag.make_jvp(ag.grad(loss))(x)(direction)[1]
        reverse_forward = ag.grad(lambda a: ag.make_jvp(loss)(a)(direction)[1])(x)
        np.testing.assert_allclose(forward_reverse, expected_second @ direction, atol=2e-9, rtol=0)
        np.testing.assert_allclose(reverse_forward, expected_second @ direction, atol=2e-9, rtol=0)
    elif interface == "jax":
        jax = pytest.importorskip("jax")
        jnp = pytest.importorskip("jax.numpy")
        exp = jnp.exp
        assert jax.config.x64_enabled, "This strict numerical graph suite requires JAX_ENABLE_X64=True."
        x, d = jnp.array(ORACLE["point"], dtype=jnp.float64), jnp.array(direction)
        first = jax.jit(jax.grad(node))(x)
        mixed = jax.jit(jax.hessian(loss))(x)
        product = jax.jit(lambda a: jax.jvp(jax.grad(loss), (a,), (d,))[1])(x)
        raw, jvp = jax.jit(lambda a: jax.jvp(node, (a,), (d,)))(x)
        _, pullback = jax.vjp(node, x)
        vjp = pullback(jnp.array(0.7))[0]
    else:
        tf = pytest.importorskip("tensorflow")
        exp = tf.exp
        @tf.function(autograph=False)
        def differentiated(x):
            with tf.GradientTape(persistent=True) as outer:
                outer.watch(x)
                with tf.GradientTape(persistent=True) as inner:
                    inner.watch(x)
                    raw = node(x)
                    result = (raw-0.3)**2 if loss_kind == "square" else exp(raw)+0.2*raw**3
                first = inner.gradient(raw, x)
                loss_first = inner.gradient(result, x)
                contracted = tf.reduce_sum(loss_first*tf.constant(direction, dtype=tf.float64))
            mixed = outer.jacobian(loss_first, x, experimental_use_pfor=False)
            product = outer.gradient(contracted, x)
            vjp = inner.gradient(raw, x, output_gradients=tf.constant(0.7, dtype=tf.float64))
            with tf.autodiff.ForwardAccumulator(x, tf.constant(direction, dtype=tf.float64)) as forward:
                raw_forward = node(x)
            return raw, first, mixed, product, vjp, forward.jvp(raw_forward)
        raw, first, mixed, product, vjp, jvp = differentiated(tf.constant(ORACLE["point"], dtype=tf.float64))
        assert jvp is not None
    np.testing.assert_allclose(raw, value, atol=8e-12, rtol=0)
    np.testing.assert_allclose(first, gradient, atol=8e-11, rtol=0)
    np.testing.assert_allclose(mixed, expected_second, atol=2e-9, rtol=0)
    np.testing.assert_allclose(product, expected_second @ direction, atol=2e-9, rtol=0)
    np.testing.assert_allclose(jvp, gradient @ direction, atol=8e-11, rtol=0)
    np.testing.assert_allclose(vjp, 0.7*gradient, atol=8e-11, rtol=0)


@pytest.mark.parametrize("mode", ["first", "forward_reverse", "reverse_forward"])
def test_torch_real_forward_ad_and_mixed_modes_are_not_reverse_jvp_surrogates(mode):
    torch = pytest.importorskip("torch")
    fw = torch.autograd.forward_ad
    p, q = qb.Parameter("p"), qb.Parameter("q")
    source = qb.QuantumCircuit(100)
    source.append(qb.Circuit(1).rx(p, 0).rz(q, 0).to_gate().power(0.5, annotated=True), (99,))
    node = QNode.from_circuit(source, qb.PauliZ(99), interface="torch", max_diff=2,
        device=qb.MatrixProductStateDevice(max_bond_dim=4, cutoff=0))
    case = ORACLE["su2"][0]
    value, gradient, hessian = case["value"], np.array(case["gradient"]), np.array(case["hessian"])
    loss_hessian = 2*(value-0.3)*hessian+2*np.outer(gradient, gradient)
    x = torch.tensor(ORACLE["point"], dtype=torch.float64, requires_grad=mode != "first")
    direction = torch.tensor([0.4, -0.3], dtype=torch.float64)
    with fw.dual_level():
        dual = fw.make_dual(x, direction)
        raw = node(dual)
        loss = (raw-0.3)**2
        if mode == "first":
            tangent = fw.unpack_dual(raw).tangent
            assert tangent is not None, "Forward AD must not detach a nonzero tangent"
            actual, expected = tangent, gradient @ direction.numpy()
        elif mode == "forward_reverse":
            first = torch.autograd.grad(loss, dual, create_graph=True)[0]
            actual = fw.unpack_dual(first).tangent
            assert actual is not None
            expected = loss_hessian @ direction.numpy()
        else:
            directional = fw.unpack_dual(loss).tangent
            assert directional is not None
            expected = loss_hessian @ direction.numpy()
    if mode == "reverse_forward":
        # Close the first tangent level before the reverse pass. Keeping it
        # active additionally requests the third-order tangent of this HVP.
        actual = torch.autograd.grad(directional, x)[0]
    np.testing.assert_allclose(actual.detach().numpy(), expected, atol=2e-9, rtol=0)


@pytest.mark.parametrize("interface", ["jax", "tensorflow"])
@pytest.mark.parametrize("mode", ["forward_reverse", "reverse_forward"])
@pytest.mark.parametrize("loss_kind", ["square", "exponential_cubic"])
def test_host_framework_actual_mixed_mode_graphs(interface, mode, loss_kind):
    p, q = qb.Parameter("p"), qb.Parameter("q")
    source = qb.QuantumCircuit(100)
    source.append(qb.Circuit(1).rx(p, 0).rz(q, 0).to_gate().power(0.5, annotated=True), (99,))
    node = QNode.from_circuit(source, qb.PauliZ(99), interface=interface, max_diff=2,
        device=qb.MatrixProductStateDevice(max_bond_dim=4, cutoff=0))
    case, direction = ORACLE["su2"][0], np.array([0.4, -0.3])
    g, h = np.array(case["gradient"]), np.array(case["hessian"])
    value = case["value"]
    first_loss, second_loss = ((2*(value-0.3), 2.) if loss_kind == "square"
                              else (np.exp(value)+0.6*value**2, np.exp(value)+1.2*value))
    expected = (first_loss*h+second_loss*np.outer(g, g)) @ direction
    if interface == "jax":
        jax, jnp = pytest.importorskip("jax"), pytest.importorskip("jax.numpy")
        assert jax.config.x64_enabled
        x, d = jnp.array(ORACLE["point"]), jnp.array(direction)
        def loss(a):
            result = node(a)
            return (result-0.3)**2 if loss_kind == "square" else jnp.exp(result)+0.2*result**3
        if mode == "forward_reverse":
            actual = jax.jit(lambda a: jax.jvp(jax.grad(loss), (a,), (d,))[1])(x)
        else:
            actual = jax.jit(jax.grad(lambda a: jax.jvp(loss, (a,), (d,))[1]))(x)
    else:
        tf = pytest.importorskip("tensorflow")
        def loss(a):
            result = node(a)
            return (result-0.3)**2 if loss_kind == "square" else tf.exp(result)+0.2*result**3
        @tf.function(autograph=False)
        def graph(x):
            d = tf.constant(direction, dtype=tf.float64)
            if mode == "forward_reverse":
                with tf.autodiff.ForwardAccumulator(x, d) as forward:
                    with tf.GradientTape() as reverse:
                        reverse.watch(x)
                        value = loss(x)
                    first = reverse.gradient(value, x)
                return forward.jvp(first)
            with tf.GradientTape() as reverse:
                reverse.watch(x)
                with tf.autodiff.ForwardAccumulator(x, d) as forward:
                    value = loss(x)
                tangent = forward.jvp(value)
            return reverse.gradient(tangent, x)
        actual = graph(tf.constant(ORACLE["point"], dtype=tf.float64))
        assert actual is not None
    np.testing.assert_allclose(actual, expected, atol=2e-9, rtol=0)


def test_tf_graph_true_third_point_derivative_refuses_not_fabricated_zero():
    tf = pytest.importorskip("tensorflow")
    from quantumbridge.core.classical import UnsupportedFeature

    node = QNode(lambda tape, x: (tape.ry(x, 99), tape.expval(qb.PauliZ(99)))[1],
        100, interface="tensorflow", max_diff=2,
        device=qb.MatrixProductStateDevice(max_bond_dim=2, cutoff=0))
    @tf.function(autograph=False)
    def graph(x):
        with tf.GradientTape() as third:
            third.watch(x)
            with tf.GradientTape() as second:
                second.watch(x)
                with tf.GradientTape() as first:
                    first.watch(x)
                    value = node(x)
                gradient = first.gradient(value, x)
            hessian = second.gradient(gradient, x)
        return third.gradient(hessian, x)
    with pytest.raises((UnsupportedFeature, tf.errors.OpError), match="third"):
        graph(tf.constant(0.37, dtype=tf.float64))
