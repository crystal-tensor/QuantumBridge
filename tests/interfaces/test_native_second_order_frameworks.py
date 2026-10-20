# Copyright 2026 QuantumBridge Contributors.
# Licensed under the Apache License, Version 2.0.
# Genuine framework graphs, compared to independently differentiated formulas.

import numpy as np
import pytest

from quantumbridge import Hamiltonian, PauliX, PauliZ, UnsupportedFeature
from quantumbridge.qml import QNode
from quantumbridge.transforms import split_non_commuting


def _node(sin, interface):
    def program(t, x):
        t.ry(sin(x[0])+2*x[1], 0)
        return t.expval(Hamiltonian([(.7+.1*x[0], PauliX(0)), (.2, PauliX(0).tensor(PauliZ(1)))]))
    return split_non_commuting(QNode(program, 2, interface=interface, max_diff=2, diff_method="parameter-shift"))


def _loss(node, x):
    value = node(x)
    return value*value+.3*value


def _expected(x):
    a, angle = .9+.1*x[0], np.sin(x[0])+2*x[1]
    value = a*np.sin(angle)
    gradient = np.array([.1*np.sin(angle)+a*np.cos(angle)*np.cos(x[0]), 2*a*np.cos(angle)])
    hessian = np.array([[.2*np.cos(angle)*np.cos(x[0])-a*np.sin(angle)*np.cos(x[0])**2-a*np.cos(angle)*np.sin(x[0]),
                         .2*np.cos(angle)-2*a*np.sin(angle)*np.cos(x[0])],
                        [.2*np.cos(angle)-2*a*np.sin(angle)*np.cos(x[0]), -4*a*np.sin(angle)]])
    return (2*value+.3)*hessian+2*np.outer(gradient, gradient)


def test_torch_real_mixed_hessian_coefficient_graph_and_nonlinear_loss():
    torch = pytest.importorskip("torch")
    node = _node(torch.sin, "torch")
    x = torch.tensor([.37, .2], dtype=torch.float64, requires_grad=True)
    actual = torch.autograd.functional.hessian(lambda value: _loss(node, value), x)
    np.testing.assert_allclose(actual.detach().numpy(), _expected(np.array([.37, .2])), atol=1e-10, rtol=0)
    assert torch.autograd.gradgradcheck(lambda value: _loss(node, value), (x,), eps=1e-5, atol=1e-7)


def test_autograd_real_mixed_hessian_and_third_derivative_rejection():
    autograd = pytest.importorskip("autograd")
    anp = pytest.importorskip("autograd.numpy")
    node = _node(anp.sin, "autograd")
    x = anp.array([.37, .2])
    np.testing.assert_allclose(autograd.hessian(lambda value: _loss(node, value))(x), _expected(x), atol=1e-10, rtol=0)
    def scalar(t, angle):
        t.ry(angle, 0)
        return t.expval(PauliZ(0))
    scalar_node = QNode(scalar, 1, interface="autograd", max_diff=2)
    with pytest.raises(UnsupportedFeature, match="third"):
        autograd.grad(autograd.grad(autograd.grad(scalar_node)))(.37)


def test_tensorflow_actual_nested_jacobian_and_tf_function_runtime_updates():
    tf = pytest.importorskip("tensorflow")
    node = _node(tf.sin, "tf")
    def second(x):
        with tf.GradientTape(persistent=True) as outer:
            outer.watch(x)
            with tf.GradientTape() as inner:
                inner.watch(x)
                loss = _loss(node, x)
            first = inner.gradient(loss, x)
        return outer.jacobian(first, x, experimental_use_pfor=False)
    for function in (second, tf.function(second, autograph=False)):
        for point in ([.37, .2], [.45, -.1]):
            x = tf.Variable(point, dtype=tf.float64)
            np.testing.assert_allclose(function(x), _expected(np.array(point)), atol=1e-10, rtol=0)


def test_jax_forward_reverse_jit_and_vmap_actual_second_rules():
    jax = pytest.importorskip("jax")
    jnp = pytest.importorskip("jax.numpy")
    node = _node(jnp.sin, "jax")
    dtype = jnp.float64 if jax.config.x64_enabled else jnp.float32
    atol = 1e-10 if jax.config.x64_enabled else 3e-6
    x = jnp.array([.37, .2], dtype=dtype)
    function = lambda value: _loss(node, value)
    expected = _expected(np.asarray(x, dtype=float))
    for derivative in (jax.hessian(function), jax.jacrev(jax.jacfwd(function)), jax.jacfwd(jax.jacfwd(function)), jax.jit(jax.hessian(function))):
        np.testing.assert_allclose(derivative(x), expected, atol=atol, rtol=0)
    batch = jnp.array([[.37, .2], [.45, -.1]], dtype=dtype)
    actual = jax.jit(jax.vmap(jax.hessian(function)))(batch)
    np.testing.assert_allclose(actual, [_expected(np.asarray(point, dtype=float)) for point in batch], atol=atol, rtol=0)


def test_torch_actual_third_order_rejects_without_fabricated_zero():
    torch = pytest.importorskip("torch")
    def program(t, angle):
        t.ry(angle, 0)
        return t.expval(PauliZ(0))
    node = QNode(program, 1, interface="torch", max_diff=2)
    x = torch.tensor(.37, dtype=torch.float64, requires_grad=True)
    first = torch.autograd.grad(node(x), x, create_graph=True)[0]
    second = torch.autograd.grad(first, x, create_graph=True)[0]
    np.testing.assert_allclose(second.detach(), -np.cos(.37), atol=1e-11)
    with pytest.raises(UnsupportedFeature, match="third"):
        torch.autograd.grad(second, x)


def test_tensorflow_actual_third_order_rejects_without_fabricated_zero():
    tf = pytest.importorskip("tensorflow")
    def program(t, angle):
        t.ry(angle, 0)
        return t.expval(PauliZ(0))
    node = QNode(program, 1, interface="tf", max_diff=2)
    x = tf.Variable(.37, dtype=tf.float64)
    with tf.GradientTape() as third:
        with tf.GradientTape() as outer:
            with tf.GradientTape() as inner:
                value = node(x)
            first = inner.gradient(value, x)
        second = outer.gradient(first, x)
    np.testing.assert_allclose(second, -np.cos(.37), atol=1e-11)
    with pytest.raises(UnsupportedFeature, match="third"):
        third.gradient(second, x)


def test_jax_actual_third_order_rejection():
    jax = pytest.importorskip("jax")
    jnp = pytest.importorskip("jax.numpy")
    def program(t, angle):
        t.ry(angle, 0)
        return t.expval(PauliZ(0))
    node = QNode(program, 1, interface="jax", max_diff=2)
    with pytest.raises(UnsupportedFeature, match="third"):
        jax.grad(jax.grad(jax.grad(node)))(jnp.asarray(.37))


@pytest.mark.parametrize("interface", ["jax", "tf"])
def test_declared_second_callback_shape_is_bounded_before_callback_creation(interface, monkeypatch):
    from quantumbridge import StatevectorDevice
    from quantumbridge.diff import HigherOrderLimits
    if interface == "jax":
        array = pytest.importorskip("jax.numpy").array([.3, .4])
    else:
        tf = pytest.importorskip("tensorflow")
        array = tf.constant([.3, .4], tf.float64)
    def circuit(t, x):
        t.ry(x[0], 0); t.rx(x[1], 0)
        return t.expval(PauliZ(0))
    node = QNode(circuit, 1, interface=interface, max_diff=2,
                 higher_order_limits=HigherOrderLimits(max_hessian_elements=1))
    monkeypatch.setattr(StatevectorDevice, "expectation", lambda *a, **k: pytest.fail("invalid second callback shape must reject before execution"))
    with pytest.raises(MemoryError, match="max_hessian_elements"):
        node(array)
