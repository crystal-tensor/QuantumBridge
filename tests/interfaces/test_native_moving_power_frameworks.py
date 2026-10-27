# Copyright 2026 QuantumBridge Contributors. Apache-2.0.
"""Actual four-framework AD through native noncommuting matrix functions."""

import numpy as np
import pytest

import quantumbridge as qb
from quantumbridge.qml import QNode


def make_node(interface):
    p = qb.Parameter("p")
    gate = qb.Circuit(1).ry(-p, 0).rz(p * p + 0.4, 0).ry(p, 0).to_gate()
    circuit = qb.QuantumCircuit(1)
    circuit.append(gate.power(0.5, annotated=True), (0,))
    return QNode.from_circuit(
        circuit, qb.PauliZ(0), max_diff=2, interface=interface, diff_method="adjoint"
    )


def reference(point):
    angle = -0.5 * np.angle(np.exp(-0.5j * (point * point + 0.4)))
    s, c, t, u = np.sin(point), np.cos(point), np.sin(angle), np.cos(angle)
    a, b = 0.5 * point, 0.5
    return (
        1 - 2 * s * s * t * t,
        -4 * (s * c * t * t + s * s * t * u * a),
        -4
        * (
            (c * c - s * s) * t * t
            + 4 * s * c * t * u * a
            + s * s * ((u * u - t * t) * a * a + t * u * b)
        ),
    )


@pytest.mark.parametrize("point", [0.37, 2.8])
def test_torch_actual_second_derivative(point):
    torch = pytest.importorskip("torch")
    node = make_node("torch")
    x = torch.tensor(point, dtype=torch.float64, requires_grad=True)
    value = node(x)
    (first,) = torch.autograd.grad(value, x, create_graph=True)
    (second,) = torch.autograd.grad(first, x)
    np.testing.assert_allclose(
        [value.item(), first.item(), second.item()],
        reference(point),
        atol=8e-10,
        rtol=0,
    )


@pytest.mark.parametrize("point", [0.37, 2.8])
def test_autograd_actual_second_derivative(point):
    autograd = pytest.importorskip("autograd")
    node = make_node("autograd")
    x = np.asarray(point)
    np.testing.assert_allclose(
        [node(x), autograd.grad(node)(x), autograd.grad(autograd.grad(node))(x)],
        reference(point),
        atol=8e-10,
        rtol=0,
    )


@pytest.mark.parametrize("point", [0.37, 2.8])
def test_jax_jit_actual_second_derivative(point):
    jax = pytest.importorskip("jax")
    import jax.numpy as jnp

    if not jax.config.x64_enabled:
        pytest.skip("Strict complex128 oracle requires JAX_ENABLE_X64=True.")
    node = make_node("jax")
    x = jnp.asarray(point, dtype=jnp.float64)
    np.testing.assert_allclose(
        [jax.jit(node)(x), jax.jit(jax.grad(node))(x), jax.jit(jax.hessian(node))(x)],
        reference(point),
        atol=8e-10,
        rtol=0,
    )


@pytest.mark.parametrize("point", [0.37, 2.8])
def test_tensorflow_graph_actual_second_derivative(point):
    tf = pytest.importorskip("tensorflow")
    node = make_node("tensorflow")

    @tf.function(autograph=False)
    def differentiated(x):
        with tf.GradientTape() as outer:
            outer.watch(x)
            with tf.GradientTape() as inner:
                inner.watch(x)
                value = node(x)
            first = inner.gradient(value, x)
        return value, first, outer.gradient(first, x)

    np.testing.assert_allclose(
        [float(x) for x in differentiated(tf.constant(point, dtype=tf.float64))],
        reference(point),
        atol=8e-10,
        rtol=0,
    )
