# Copyright 2026 QuantumBridge Contributors.
# Licensed under the Apache License, Version 2.0.
"""Actual framework differentiation through the native symbolic circuit AST."""

import numpy as np
import pytest

from quantumbridge import Circuit, Parameter, PauliZ
from quantumbridge.qml import QNode


def node_for(interface):
    p, q = Parameter("p"), Parameter("q")
    circuit = Circuit(2).ry((p*q+p*p).sin()+(2*p-q).exp(), 0).rx(p*q, 1).cz(0, 1)
    circuit.global_phase = p.sin()/7
    return QNode.from_circuit(circuit, PauliZ(0).tensor(PauliZ(1)), interface=interface,
                             diff_method="parameter-shift", max_diff=2)


def analytic(point):
    p, q = point
    a, b = p*q+p*p, 2*p-q
    da, db = np.array([q+2*p, p]), np.array([2., -1.])
    f, g = np.sin(a)+np.exp(b), p*q
    df, dg = np.cos(a)*da+np.exp(b)*db, np.array([q, p])
    hf = -np.sin(a)*np.outer(da, da)+np.cos(a)*np.array([[2., 1.], [1., 0.]])+np.exp(b)*np.outer(db, db)
    value = np.cos(f)*np.cos(g)
    gradient = -np.sin(f)*np.cos(g)*df-np.cos(f)*np.sin(g)*dg
    hessian = (-np.cos(f)*np.cos(g)*(np.outer(df, df)+np.outer(dg, dg))
               +np.sin(f)*np.sin(g)*(np.outer(df, dg)+np.outer(dg, df))
               -np.sin(f)*np.cos(g)*hf-np.cos(f)*np.sin(g)*np.array([[0., 1.], [1., 0.]]))
    return value, gradient, hessian


def test_torch_symbolic_circuit_actual_first_and_second_graph():
    torch = pytest.importorskip("torch")
    node = node_for("torch")
    point = np.array([.4, -.2])
    value, gradient, hessian = analytic(point)
    x = torch.tensor(point, dtype=torch.float64, requires_grad=True)
    actual = node(x)
    np.testing.assert_allclose(actual.detach(), value, atol=3e-14, rtol=0)
    np.testing.assert_allclose(torch.autograd.grad(actual, x)[0], gradient, atol=8e-11, rtol=0)
    np.testing.assert_allclose(torch.autograd.functional.hessian(node, x).detach(), hessian, atol=6e-10, rtol=0)


def test_autograd_symbolic_circuit_actual_first_and_second_graph():
    autograd = pytest.importorskip("autograd")
    anp = pytest.importorskip("autograd.numpy")
    node = node_for("autograd")
    point = anp.array([.4, -.2])
    value, gradient, hessian = analytic(point)
    assert node(point) == pytest.approx(value, abs=3e-14)
    np.testing.assert_allclose(autograd.grad(node)(point), gradient, atol=8e-11, rtol=0)
    np.testing.assert_allclose(autograd.hessian(node)(point), hessian, atol=6e-10, rtol=0)


def test_jax_symbolic_circuit_actual_jit_gradient_and_hessian():
    jax = pytest.importorskip("jax")
    jnp = pytest.importorskip("jax.numpy")
    node = node_for("jax")
    point = jnp.array([.4, -.2], dtype=jnp.float64 if jax.config.x64_enabled else jnp.float32)
    value, gradient, hessian = analytic(np.asarray(point, dtype=float))
    tolerance = 6e-10 if jax.config.x64_enabled else 2e-4
    actual, first = jax.jit(jax.value_and_grad(node))(point)
    np.testing.assert_allclose(actual, value, atol=tolerance, rtol=0)
    np.testing.assert_allclose(first, gradient, atol=tolerance, rtol=0)
    np.testing.assert_allclose(jax.jit(jax.hessian(node))(point), hessian, atol=tolerance, rtol=0)


def test_tensorflow_symbolic_circuit_actual_nested_tapes_and_graph_updates():
    tf = pytest.importorskip("tensorflow")
    node = node_for("tensorflow")
    def evaluate(x):
        with tf.GradientTape(persistent=True) as outer:
            outer.watch(x)
            with tf.GradientTape() as inner:
                inner.watch(x)
                value = node(x)
            first = inner.gradient(value, x)
        return value, first, outer.jacobian(first, x, experimental_use_pfor=False)
    for function in (evaluate, tf.function(evaluate, autograph=False)):
        for point in ([.4, -.2], [-.7, .5]):
            actual = function(tf.constant(point, dtype=tf.float64))
            expected = analytic(np.array(point))
            for received, reference in zip(actual, expected):
                np.testing.assert_allclose(received, reference, atol=6e-10, rtol=0)


@pytest.mark.parametrize("name,number", [("abs", 0.), ("sign", 0.), ("arcsin", 1.), ("arccos", 1.)])
def test_torch_symbolic_nonsmooth_zero_cannot_silently_acquire_a_smooth_hessian(name, number):
    torch = pytest.importorskip("torch")
    p = Parameter("p")
    node = QNode.from_circuit(Circuit(1).ry(getattr(p, name)(), 0), PauliZ(0), interface="torch", max_diff=2)
    point = torch.tensor(number, dtype=torch.float64, requires_grad=True)
    assert np.isfinite(node(point).item())
    with pytest.raises(ValueError, match="zero|nondifferentiable"):
        torch.autograd.functional.hessian(node, point)


@pytest.mark.parametrize("interface", ["torch", "autograd", "jax", "tensorflow"])
@pytest.mark.parametrize("name", ["abs", "sign", "arcsin", "arccos"])
def test_framework_symbolic_domain_guards_keep_nonzero_second_derivatives_correct(interface, name):
    import math
    p, value = Parameter("p"), .4
    node = QNode.from_circuit(Circuit(1).ry(getattr(p, name)(), 0), PauliZ(0), interface=interface, max_diff=2)
    if name == "abs": f, df, ddf = value, 1., 0.
    elif name == "sign": f, df, ddf = 1., 0., 0.
    else:
        f = math.asin(value) if name == "arcsin" else math.acos(value)
        df = (1 if name == "arcsin" else -1)/math.sqrt(1-value*value)
        ddf = (1 if name == "arcsin" else -1)*value/(1-value*value)**1.5
    expected = -math.cos(f)*df*df-math.sin(f)*ddf
    if interface == "torch":
        torch = pytest.importorskip("torch")
        actual = torch.autograd.functional.hessian(node, torch.tensor(value, dtype=torch.float64)).item()
    elif interface == "autograd":
        ag = pytest.importorskip("autograd")
        actual = ag.grad(ag.grad(node))(value)
    elif interface == "jax":
        jax = pytest.importorskip("jax")
        jnp = pytest.importorskip("jax.numpy")
        actual = np.asarray(jax.jit(jax.grad(jax.grad(node)))(jnp.asarray(value)))
    else:
        tf = pytest.importorskip("tensorflow")
        x = tf.constant(value, dtype=tf.float64)
        with tf.GradientTape() as outer:
            outer.watch(x)
            with tf.GradientTape() as inner:
                inner.watch(x)
                output = node(x)
            first = inner.gradient(output, x)
        actual = outer.gradient(first, x).numpy()
    np.testing.assert_allclose(actual, expected, atol=4e-6 if interface == "jax" else 1e-10, rtol=0)


@pytest.mark.parametrize("interface", ["autograd", "jax", "tensorflow"])
@pytest.mark.parametrize("name,number", [("abs", 0.), ("sign", 0.), ("arcsin", 1.), ("arccos", 1.)])
def test_other_framework_symbolic_boundary_derivatives_reject_while_forward_is_valid(interface, name, number):
    p = Parameter("p")
    node = QNode.from_circuit(Circuit(1).ry(getattr(p, name)(), 0), PauliZ(0), interface=interface, max_diff=2)
    if interface == "autograd":
        ag = pytest.importorskip("autograd")
        assert np.isfinite(node(number))
        with pytest.raises(ValueError, match="Symbolic derivative is nondifferentiable"):
            ag.grad(node)(number)
    elif interface == "jax":
        jax = pytest.importorskip("jax")
        jnp = pytest.importorskip("jax.numpy")
        point = jnp.asarray(number)
        assert np.isfinite(np.asarray(node(point)))
        with pytest.raises((ValueError, RuntimeError), match="Symbolic derivative is nondifferentiable"):
            np.asarray(jax.jit(jax.grad(node))(point))
    else:
        tf = pytest.importorskip("tensorflow")
        point = tf.constant(number, dtype=tf.float64)
        assert np.isfinite(node(point).numpy())
        with pytest.raises(tf.errors.InvalidArgumentError, match="Symbolic derivative is nondifferentiable"):
            with tf.GradientTape() as tape:
                tape.watch(point)
                output = node(point)
            tape.gradient(output, point).numpy()


@pytest.mark.parametrize("name", ["abs", "sign", "arcsin", "arccos"])
def test_tensorflow_graph_symbolic_domain_rule_has_no_per_request_payload_registration(name, monkeypatch):
    tf = pytest.importorskip("tensorflow")
    from quantumbridge.diff.compiled_parameters import _unary
    from quantumbridge.interfaces import symbolic_math
    registered = []
    original = tf.RegisterGradient
    def recording(label):
        decorate = original(label)
        def apply(function):
            registered.append(function)
            return decorate(function)
        return apply
    monkeypatch.setattr(tf, "RegisterGradient", recording)
    def second(source):
        with tf.GradientTape() as outer:
            outer.watch(source)
            with tf.GradientTape() as inner:
                inner.watch(source)
                result = _unary(name, source)
            first = inner.gradient(result, source)
        return outer.gradient(first, source)
    for _ in range(2):
        graph = tf.function(second, autograph=False)
        actual = graph(tf.constant(.4, dtype=tf.float64))
        sign = 1 if name == "arcsin" else -1
        expected = sign*.4/(1-.4**2)**1.5 if name in {"arcsin", "arccos"} else 0.
        np.testing.assert_allclose(actual, expected, atol=1e-12, rtol=0)
        point = 0. if name in {"abs", "sign"} else 1.
        with pytest.raises(tf.errors.InvalidArgumentError, match="Symbolic derivative is nondifferentiable"):
            graph(tf.constant(point, dtype=tf.float64)).numpy()
    assert len(registered) <= 2
    assert symbolic_math._tf_registered <= {"abs", "sign", "arcsin", "arccos"}
    assert symbolic_math._tf_guard_registered <= {"abs", "sign", "arcsin", "arccos"}
    for function in registered:
        captures = [cell.cell_contents for cell in function.__closure__ or ()]
        assert all(not isinstance(value, (tf.Tensor, tf.Variable, tf.Graph)) for value in captures)


@pytest.mark.parametrize("name", ["abs", "sign", "arcsin", "arccos"])
def test_jax_live_symbolic_scalar_jvp_keeps_the_domain_guard_through_nested_jit(name):
    jax = pytest.importorskip("jax")
    jnp = pytest.importorskip("jax.numpy")
    from quantumbridge.diff.compiled_parameters import _unary
    function = lambda value: _unary(name, value)
    point = jnp.asarray(.4)
    sign = 1 if name == "arcsin" else -1
    expected = sign*.4/(1-.4**2)**1.5 if name in {"arcsin", "arccos"} else 0.
    actual = np.asarray(jax.jit(jax.grad(jax.grad(function)))(point))
    np.testing.assert_allclose(actual, expected, atol=1e-11 if jax.config.x64_enabled else 2e-6, rtol=0)
    invalid = jnp.asarray(0. if name in {"abs", "sign"} else 1.)
    assert np.isfinite(np.asarray(jax.jit(function)(invalid)))
    with pytest.raises((ValueError, RuntimeError), match="Symbolic derivative is nondifferentiable"):
        np.asarray(jax.jit(jax.grad(jax.grad(function)))(invalid))
