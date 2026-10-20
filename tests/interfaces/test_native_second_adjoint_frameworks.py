# Copyright 2026 QuantumBridge Contributors.
# Licensed under the Apache License, Version 2.0.
# Actual framework second graphs must reach the native adjoint engine.

import numpy as np
import pytest

from quantumbridge import PauliX, Hamiltonian
from quantumbridge.diff import HigherOrderLimits
from quantumbridge.diff.qnode_engine import ExecutionPlan
from quantumbridge.qml import QNode
from quantumbridge.transforms import split_non_commuting


@pytest.mark.parametrize("interface", ["torch", "autograd", "jax", "tf"])
def test_true_framework_second_adjoint_with_live_coefficient_and_outer_loss(interface, monkeypatch):
    monkeypatch.setattr(ExecutionPlan, "shift_recipe", lambda *a, **k: pytest.fail("framework adjoint must not substitute shifted circuits"))
    def circuit(t, x):
        t.ry(x*x, 0)
        return t.expval(Hamiltonian([(.7+.1*x, PauliX(0))]))
    node = split_non_commuting(QNode(circuit, 1, interface=interface, max_diff=2, diff_method="adjoint",
        higher_order_limits=HigherOrderLimits(max_hessian_elements=1)))
    def loss(x):
        value = node(x)
        return value*value+.3*value
    x, v = .37, .4
    a, angle = .7+.1*x, x*x
    value = a*np.sin(angle)
    first = .1*np.sin(angle)+2*x*a*np.cos(angle)
    second = .4*x*np.cos(angle)+2*a*np.cos(angle)-4*x*x*a*np.sin(angle)
    expected = v*((2*value+.3)*second+2*first**2)
    if interface == "torch":
        torch = pytest.importorskip("torch")
        point = torch.tensor(x, dtype=torch.float64, requires_grad=True)
        gradient = torch.autograd.grad(loss(point), point, create_graph=True)[0]
        actual = torch.autograd.grad(v*gradient, point)[0].detach().numpy()
    elif interface == "autograd":
        autograd = pytest.importorskip("autograd")
        actual = autograd.grad(lambda point: v*autograd.grad(loss)(point))(x)
    elif interface == "jax":
        jax, jnp = pytest.importorskip("jax"), pytest.importorskip("jax.numpy")
        point, direction = jnp.asarray(x), jnp.asarray(v)
        actual = jax.jvp(jax.grad(loss), (point,), (direction,))[1]
        reverse = lambda point: jax.grad(lambda p: v*jax.grad(loss)(p))(point)
        np.testing.assert_allclose(jax.jit(reverse)(point), expected, atol=3e-6)
    else:
        tf = pytest.importorskip("tensorflow")
        point = tf.Variable(x, dtype=tf.float64)
        with tf.GradientTape() as outer:
            with tf.GradientTape() as inner:
                value = loss(point)
            gradient = inner.gradient(value, point)
            directional = v*gradient
        actual = outer.gradient(directional, point).numpy()
    np.testing.assert_allclose(actual, expected, atol=3e-6 if interface == "jax" else 1e-11, rtol=0)
    if interface != "jax":
        assert node.last_metadata["shifted_evaluation_count"] == 0
        assert node.last_metadata["gradient_method"] == "adjoint"


def test_jax_transposed_second_adjoint_preflights_aggregate_work_before_any_row(monkeypatch):
    from quantumbridge import PauliZ, StatevectorDevice
    from quantumbridge.interfaces.jax_autodiff import JAXBridgeLimits
    from quantumbridge.interfaces.native_host import NativeHostKernel
    jnp = pytest.importorskip("jax.numpy")
    def circuit(t, x):
        t.ry(x[0], 0); t.rx(x[1], 0)
        return t.expval(PauliZ(0)), t.expval(PauliX(0))
    point = np.array([.37, .2])
    node = QNode(circuit, 1, max_diff=2, diff_method="adjoint", interface="jax")
    source, recorder, program = node._construct((jnp.asarray(point),), {}, prepare_only=True)
    kernel = NativeHostKernel(node, source, recorder, program, JAXBridgeLimits())
    work = kernel.prepare_second(point, direction=np.ones(2))[-1]["adjoint_operations"]
    kernel.node.higher_order_limits = HigherOrderLimits(max_adjoint_operations=work)
    monkeypatch.setattr(StatevectorDevice, "statevector", lambda *a, **k: pytest.fail("aggregate row budget must reject before every simulation"))
    with pytest.raises(MemoryError, match="max_adjoint_operations"):
        kernel.run_second_transpose(point, np.eye(2))
