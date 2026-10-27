# Copyright 2026 QuantumBridge Contributors. Apache-2.0.
"""Actual mixed framework graphs against independent 70-digit math oracles."""

import json
from pathlib import Path

import numpy as np
import pytest

import quantumbridge as qb
from quantumbridge.qml import QNode

ORACLE = json.loads(
    (
        Path(__file__).parents[1] / "information/data/native_mixed_power_oracles.json"
    ).read_text()
)


def node_for(interface, power):
    p, q = qb.Parameter("p"), qb.Parameter("q")
    source = qb.QuantumCircuit(1)
    source.append(
        qb.Circuit(1).rx(p, 0).rz(q, 0).to_gate().power(power, annotated=True), (0,)
    )
    return QNode.from_circuit(
        source, qb.PauliZ(0), interface=interface, diff_method="adjoint", max_diff=2
    )


@pytest.mark.parametrize("case", ORACLE["su2"])
@pytest.mark.parametrize("interface", ["torch", "autograd", "jax", "tensorflow"])
def test_actual_first_mixed_second_jvp_vjp_and_directional_outer_loss_graphs(
    case, interface
):
    node = node_for(interface, case["power"])
    value, gradient, hessian = (
        case["value"],
        np.array(case["gradient"]),
        np.array(case["hessian"]),
    )
    direction = np.array([0.4, -0.3])
    expected_loss_hessian = (2 * value + 0.3) * hessian + 2 * np.outer(
        gradient, gradient
    )

    def loss(x):
        result = node(x)
        return result * result + 0.3 * result

    if interface == "torch":
        torch = pytest.importorskip("torch")
        x = torch.tensor(ORACLE["point"], dtype=torch.float64, requires_grad=True)
        d = torch.tensor(direction, dtype=torch.float64)
        (first,) = torch.autograd.grad(loss(x), x, create_graph=True)
        (actual_hvp,) = torch.autograd.grad((first * d).sum(), x)
        actual_hessian = torch.autograd.functional.hessian(loss, x).detach().numpy()
        raw, actual_jvp = torch.autograd.functional.jvp(node, x, d)
        _, actual_vjp = torch.autograd.functional.vjp(
            node, x, torch.tensor(0.7, dtype=torch.float64)
        )
        actual_hvp, actual_vjp = (
            actual_hvp.detach().numpy(),
            actual_vjp.detach().numpy(),
        )
        raw, actual_jvp = raw.detach().numpy(), actual_jvp.detach().numpy()
    elif interface == "autograd":
        ag = pytest.importorskip("autograd")
        anp = pytest.importorskip("autograd.numpy")
        x = anp.array(ORACLE["point"])
        actual_hessian = ag.hessian(loss)(x)
        actual_hvp = ag.grad(lambda a: anp.dot(ag.grad(loss)(a), direction))(x)
        raw, actual_jvp = ag.make_jvp(node)(x)(direction)
        vjp, _ = ag.make_vjp(node)(x)
        actual_vjp = vjp(0.7)
    elif interface == "jax":
        jax = pytest.importorskip("jax")
        import jax.numpy as jnp

        if not jax.config.x64_enabled:
            pytest.skip("Strict oracle requires JAX_ENABLE_X64=True.")
        x, d = jnp.array(ORACLE["point"], dtype=jnp.float64), jnp.array(direction)
        actual_hessian = jax.jit(jax.hessian(loss))(x)
        actual_hvp = jax.jit(lambda a: jax.jvp(jax.grad(loss), (a,), (d,))[1])(x)
        raw, actual_jvp = jax.jit(lambda a: jax.jvp(node, (a,), (d,)))(x)
        _, vjp = jax.vjp(node, x)
        (actual_vjp,) = vjp(jnp.asarray(0.7, dtype=jnp.float64))
    else:
        tf = pytest.importorskip("tensorflow")

        @tf.function(autograph=False)
        def differentiated(x):
            with tf.GradientTape(persistent=True) as outer:
                outer.watch(x)
                with tf.GradientTape() as inner:
                    inner.watch(x)
                    result = loss(x)
                first = inner.gradient(result, x)
                product = tf.reduce_sum(
                    first * tf.constant(direction, dtype=tf.float64)
                )
            second = outer.jacobian(first, x, experimental_use_pfor=False)
            hvp = outer.gradient(product, x)
            with tf.GradientTape() as tape:
                tape.watch(x)
                raw = node(x)
            vjp = tape.gradient(
                raw, x, output_gradients=tf.constant(0.7, dtype=tf.float64)
            )
            with tf.autodiff.ForwardAccumulator(
                x, tf.constant(direction, dtype=tf.float64)
            ) as forward:
                raw_forward = node(x)
            return raw, second, hvp, vjp, forward.jvp(raw_forward)

        raw, actual_hessian, actual_hvp, actual_vjp, actual_jvp = differentiated(
            tf.constant(ORACLE["point"], dtype=tf.float64)
        )
        assert actual_jvp is not None, "A missing JVP is not a zero derivative."
    np.testing.assert_allclose(raw, value, atol=8e-12, rtol=0)
    np.testing.assert_allclose(actual_hessian, expected_loss_hessian, atol=2e-9, rtol=0)
    np.testing.assert_allclose(
        actual_hvp, expected_loss_hessian @ direction, atol=2e-9, rtol=0
    )
    np.testing.assert_allclose(actual_vjp, 0.7 * gradient, atol=8e-11, rtol=0)
    np.testing.assert_allclose(actual_jvp, gradient @ direction, atol=8e-11, rtol=0)


@pytest.mark.parametrize(
    "mode", ["forward_reverse", "reverse_forward", "forward_forward"]
)
def test_autograd_composed_forward_modes_use_true_mixed_second_direction(mode):
    ag = pytest.importorskip("autograd")
    anp = pytest.importorskip("autograd.numpy")
    node = node_for("autograd", 0.5)
    x, left, right = (
        anp.array(ORACLE["point"]),
        anp.array([0.2, 0.6]),
        anp.array([0.4, -0.3]),
    )
    hessian = np.array(ORACLE["su2"][0]["hessian"])
    if mode == "forward_reverse":
        _, actual = ag.make_jvp(ag.grad(node))(x)(right)
        expected = hessian @ right
    elif mode == "reverse_forward":
        actual = ag.grad(lambda a: ag.make_jvp(node)(a)(right)[1])(x)
        expected = hessian @ right
    else:
        _, actual = ag.make_jvp(lambda a: ag.make_jvp(node)(a)(right)[1])(x)(left)
        expected = left @ hessian @ right
    np.testing.assert_allclose(actual, expected, atol=2e-9, rtol=0)


def test_autograd_forward_order_limits_reject_instead_of_returning_fake_zero():
    ag = pytest.importorskip("autograd")
    anp = pytest.importorskip("autograd.numpy")
    from quantumbridge.core.classical import UnsupportedFeature

    node = node_for("autograd", 0.5)
    x, direction = anp.array(ORACLE["point"]), anp.array([0.4, -0.3])
    node.max_diff = 1
    np.testing.assert_allclose(
        ag.make_jvp(node)(x)(direction)[1],
        np.array(ORACLE["su2"][0]["gradient"]) @ direction,
        atol=8e-11,
    )
    with pytest.raises(UnsupportedFeature) as rejected:
        ag.make_jvp(ag.grad(node))(x)(direction)
    assert rejected.value.feature == "higher_order_derivatives"
    node.max_diff = 2

    def first(a):
        return ag.make_jvp(node)(a)(direction)[1]

    def second(a):
        return ag.make_jvp(first)(a)(direction)[1]

    with pytest.raises(UnsupportedFeature, match="third"):
        ag.make_jvp(second)(x)(direction)


def test_multiple_output_directions_preflight_aggregate_matrix_function_work(
    monkeypatch,
):
    jnp = pytest.importorskip("jax.numpy")
    from quantumbridge import StatevectorDevice
    from quantumbridge.diff import HigherOrderLimits
    from quantumbridge.interfaces.jax_autodiff import JAXBridgeLimits
    from quantumbridge.interfaces.native_host import NativeHostKernel

    base = node_for("jax", 0.5)

    def program(tape, x):
        base.fn(tape, x)
        return tape.expval(qb.PauliZ(0)), tape.expval(qb.PauliX(0))

    node = QNode(program, 1, interface="jax", max_diff=2, diff_method="adjoint")
    point = np.array(ORACLE["point"])
    source, recorder, transforms = node._construct(
        (jnp.array(point),), {}, prepare_only=True
    )
    kernel = NativeHostKernel(node, source, recorder, transforms, JAXBridgeLimits())
    work = kernel.prepare_second(point, direction=np.ones(2))[-1]["adjoint_operations"]
    kernel.node.higher_order_limits = HigherOrderLimits(max_adjoint_operations=work)
    monkeypatch.setattr(
        StatevectorDevice,
        "statevector",
        lambda *a, **k: pytest.fail("Aggregate bound must precede every simulation"),
    )
    monkeypatch.setattr(
        StatevectorDevice,
        "expectation",
        lambda *a, **k: pytest.fail("Aggregate bound must precede every expectation"),
    )
    with pytest.raises(MemoryError, match="max_adjoint_operations"):
        kernel.run_second_transpose(point, np.eye(2))
