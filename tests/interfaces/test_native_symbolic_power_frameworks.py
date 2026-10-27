# Copyright 2026 QuantumBridge Contributors. Apache-2.0.
"""Actual optional-framework second derivatives through branch-correct powers."""

import numpy as np
import pytest

import quantumbridge as qb
from quantumbridge.circuit_library import CRYGate
from quantumbridge.qml import QNode


def make_node(interface, method):
    p = qb.Parameter("p")
    circuit = qb.QuantumCircuit(2)
    circuit.h(0)
    circuit.append(CRYGate(p, ctrl_state=0).power(0.5, annotated=True), [0, 1])
    return QNode.from_circuit(
        circuit, qb.PauliX(0), interface=interface, max_diff=2, diff_method=method
    )


def reference(x):
    phase = np.angle(np.exp(-0.5j * x)) / 2
    return np.cos(phase), 0.25 * np.sin(phase), -0.0625 * np.cos(phase)


@pytest.mark.parametrize("method", ["parameter-shift", "adjoint"])
@pytest.mark.parametrize("point", [7.3, 1e12 + 0.37])
def test_actual_torch_second_gradient(method, point):
    torch = pytest.importorskip("torch")
    node = make_node("torch", method)
    x = torch.tensor(point, dtype=torch.float64, requires_grad=True)
    value = node(x)
    (first,) = torch.autograd.grad(value, x, create_graph=True)
    (second,) = torch.autograd.grad(first, x)
    np.testing.assert_allclose(
        [value.item(), first.item(), second.item()],
        reference(point),
        atol=5e-11,
        rtol=0,
    )


@pytest.mark.parametrize("method", ["parameter-shift", "adjoint"])
@pytest.mark.parametrize("point", [7.3, 1e12 + 0.37])
def test_actual_autograd_second_gradient(method, point):
    autograd = pytest.importorskip("autograd")
    node = make_node("autograd", method)
    x = np.array(point)
    np.testing.assert_allclose(
        [node(x), autograd.grad(node)(x), autograd.grad(autograd.grad(node))(x)],
        reference(point),
        atol=5e-11,
        rtol=0,
    )


@pytest.mark.parametrize("method", ["parameter-shift", "adjoint"])
@pytest.mark.parametrize("point", [7.3, 1e12 + 0.37])
def test_actual_jax_jit_and_second_gradient(method, point):
    jax = pytest.importorskip("jax")
    import jax.numpy as jnp

    if not jax.config.x64_enabled:
        pytest.skip("Strict complex128 oracle requires JAX_ENABLE_X64=True.")
    node = make_node("jax", method)
    function = jax.jit(node)
    x = jnp.asarray(point, dtype=jnp.float64)
    np.testing.assert_allclose(
        [function(x), jax.jit(jax.grad(node))(x), jax.jit(jax.hessian(node))(x)],
        reference(point),
        atol=6e-11,
        rtol=0,
    )


@pytest.mark.parametrize("method", ["parameter-shift", "adjoint"])
@pytest.mark.parametrize("point", [7.3, 1e12 + 0.37])
def test_actual_tensorflow_graph_second_gradient(method, point):
    tf = pytest.importorskip("tensorflow")
    node = make_node("tensorflow", method)

    @tf.function(autograph=False)
    def differentiated(x):
        with tf.GradientTape() as outer:
            outer.watch(x)
            with tf.GradientTape() as inner:
                inner.watch(x)
                value = node(x)
            first = inner.gradient(value, x)
        return value, first, outer.gradient(first, x)

    actual = differentiated(tf.constant(point, dtype=tf.float64))
    np.testing.assert_allclose(
        [float(value) for value in actual], reference(point), atol=6e-11, rtol=0
    )
