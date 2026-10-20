# Copyright 2026 QuantumBridge Contributors.
# Licensed under the Apache License, Version 2.0.
# Independent direction-only contracts, persisted before streaming runtime edits.

import numpy as np
import pytest

from quantumbridge import Hamiltonian, PauliX, PauliZ
from quantumbridge.diff import HigherOrderLimits
from quantumbridge.diff.qnode_engine import ExecutionPlan
from quantumbridge.qml import QNode
from quantumbridge.transforms import split_non_commuting
from quantumbridge.transforms.program import TransformedExecutionPlan


def expected_product(x, direction):
    a, angle = .9+.1*x[0], np.sin(x[0])+2*x[1]
    value = a*np.sin(angle)
    gradient = np.array([.1*np.sin(angle)+a*np.cos(angle)*np.cos(x[0]), 2*a*np.cos(angle)])
    mixed = .2*np.cos(angle)-2*a*np.sin(angle)*np.cos(x[0])
    hessian = np.array([[.2*np.cos(angle)*np.cos(x[0])-a*np.sin(angle)*np.cos(x[0])**2-a*np.cos(angle)*np.sin(x[0]), mixed],
                        [mixed, -4*a*np.sin(angle)]])
    return ((2*value+.3)*hessian+2*np.outer(gradient, gradient)) @ direction


def make_node(sin, interface):
    def circuit(t, x):
        t.ry(sin(x[0])+2*x[1], 0)
        return t.expval(Hamiltonian([(.7+.1*x[0], PauliX(0)), (.2, PauliX(0).tensor(PauliZ(1)))]))
    return split_non_commuting(QNode(circuit, 2, interface=interface, max_diff=2,
        higher_order_limits=HigherOrderLimits(max_hessian_elements=1), diff_method="parameter-shift"))


def loss(node, x):
    value = node(x)
    return value*value+.3*value


@pytest.fixture
def direction_only_spy(monkeypatch):
    calls = []
    for cls in (ExecutionPlan, TransformedExecutionPlan):
        original = cls.second_derivatives
        def wrap(self, values, *args, _original=original, **kwargs):
            assert kwargs.get("direction") is not None, "framework HVP may not materialize a native full Hessian"
            result = _original(self, values, *args, **kwargs)
            assert result[2].shape[-1] == 1
            calls.append(self.metadata)
            return result
        monkeypatch.setattr(cls, "second_derivatives", wrap)
    return calls


@pytest.mark.parametrize("interface", ["torch", "autograd", "jax", "tf"])
def test_real_framework_hvp_does_not_require_full_hessian_storage(interface, direction_only_spy):
    point, direction = np.array([.37, .2]), np.array([.4, -.3])
    if interface == "torch":
        torch = pytest.importorskip("torch")
        node = make_node(torch.sin, interface)
        x = torch.tensor(point, dtype=torch.float64, requires_grad=True)
        first = torch.autograd.grad(loss(node, x), x, create_graph=True)[0]
        actual = torch.autograd.grad(torch.dot(first, torch.tensor(direction)), x)[0].detach().numpy()
    elif interface == "autograd":
        autograd = pytest.importorskip("autograd")
        anp = pytest.importorskip("autograd.numpy")
        node = make_node(anp.sin, interface)
        actual = autograd.grad(lambda x: anp.dot(autograd.grad(lambda y: loss(node, y))(x), direction))(anp.array(point))
    elif interface == "jax":
        jax = pytest.importorskip("jax")
        jnp = pytest.importorskip("jax.numpy")
        node = make_node(jnp.sin, interface)
        dtype = jnp.float64 if jax.config.x64_enabled else jnp.float32
        actual = jax.jvp(jax.grad(lambda x: loss(node, x)), (jnp.array(point, dtype=dtype),), (jnp.array(direction, dtype=dtype),))[1]
    else:
        tf = pytest.importorskip("tensorflow")
        node = make_node(tf.sin, interface)
        x = tf.Variable(point, dtype=tf.float64)
        with tf.GradientTape() as outer:
            with tf.GradientTape() as inner:
                value = loss(node, x)
            first = inner.gradient(value, x)
            directional = tf.reduce_sum(first*tf.constant(direction))
        actual = outer.gradient(directional, x).numpy()
    np.testing.assert_allclose(actual, expected_product(point, direction), atol=3e-6 if interface == "jax" else 1e-10, rtol=0)
    assert direction_only_spy
    assert all(receipt["hvp_streamed"] for receipt in direction_only_spy)


def vector_node(interface, **options):
    def circuit(t, x):
        t.ry(x[0], 0); t.rx(x[1], 0)
        return {"z": t.expval(PauliZ(0)), "p": t.probs([0]), "x": t.expval(PauliX(0))}
    return QNode(circuit, 1, interface=interface, max_diff=2,
                 higher_order_limits=HigherOrderLimits(max_hessian_elements=1), **options)


def vector_loss(node, x):
    value = node(x)
    return value["z"]**2+.4*value["p"]["1"]+.3*value["x"]**2


def vector_expected(point, direction):
    x, y = point
    z, local_x = np.cos(x)*np.cos(y), np.sin(x)
    gz, gx = np.array([-np.sin(x)*np.cos(y), -np.cos(x)*np.sin(y)]), np.array([np.cos(x), 0.])
    hz = np.array([[-z, np.sin(x)*np.sin(y)], [np.sin(x)*np.sin(y), -z]])
    hx = np.diag([-local_x, 0.])
    return ((2*z-.2)*hz+2*np.outer(gz, gz)+.6*(local_x*hx+np.outer(gx, gx))) @ direction


@pytest.mark.parametrize("interface", ["torch", "autograd", "jax", "tf"])
def test_nested_vector_outputs_and_second_cotangent_chain_rule(interface, direction_only_spy):
    point, direction = np.array([.37, .2]), np.array([.4, -.3])
    node = vector_node(interface)
    if interface == "torch":
        torch = pytest.importorskip("torch")
        x = torch.tensor(point, dtype=torch.float64, requires_grad=True)
        first = torch.autograd.grad(vector_loss(node, x), x, create_graph=True)[0]
        actual = torch.autograd.grad(torch.dot(first, torch.tensor(direction)), x)[0].detach().numpy()
    elif interface == "autograd":
        autograd, anp = pytest.importorskip("autograd"), pytest.importorskip("autograd.numpy")
        actual = autograd.grad(lambda x: anp.dot(autograd.grad(lambda y: vector_loss(node, y))(x), direction))(anp.array(point))
    elif interface == "jax":
        jax, jnp = pytest.importorskip("jax"), pytest.importorskip("jax.numpy")
        dtype = jnp.float64 if jax.config.x64_enabled else jnp.float32
        gradient = jax.grad(lambda x: vector_loss(node, x))
        actual = jax.grad(lambda x: jnp.vdot(gradient(x), jnp.array(direction, dtype=dtype)))(jnp.array(point, dtype=dtype))
    else:
        tf = pytest.importorskip("tensorflow")
        x = tf.Variable(point, dtype=tf.float64)
        with tf.GradientTape() as outer:
            with tf.GradientTape() as inner:
                value = vector_loss(node, x)
            first = inner.gradient(value, x)
            contracted = tf.reduce_sum(first*tf.constant(direction))
        actual = outer.gradient(contracted, x).numpy()
    np.testing.assert_allclose(actual, vector_expected(point, direction), atol=3e-6 if interface == "jax" else 1e-10, rtol=0)
    assert direction_only_spy
    if interface == "jax":
        assert len(direction_only_spy) >= 3, "the transposed vector Jacobian must execute actual output-row HVPs"


def test_jax_reverse_forward_jit_and_nested_mapping_remain_direction_only(direction_only_spy):
    jax, jnp = pytest.importorskip("jax"), pytest.importorskip("jax.numpy")
    dtype = jnp.float64 if jax.config.x64_enabled else jnp.float32
    tolerance = 1e-10 if jax.config.x64_enabled else 3e-6
    node = make_node(jnp.sin, "jax")
    gradient = jax.grad(lambda x: loss(node, x))
    def reverse(x, direction):
        return jax.grad(lambda point: jnp.vdot(gradient(point), direction))(x)
    point = jnp.array([.37, .2], dtype=dtype)
    direction = jnp.array([.4, -.3], dtype=dtype)
    for operation in (reverse, jax.jit(reverse)):
        np.testing.assert_allclose(operation(point, direction), expected_product(np.asarray(point), np.asarray(direction)), atol=tolerance, rtol=0)
    points = jnp.array([[.37, .2], [.45, -.1]], dtype=dtype)
    directions = jnp.array([[.4, -.3], [.2, .1]], dtype=dtype)
    expected = [expected_product(np.asarray(x), np.asarray(v)) for x, v in zip(points, directions)]
    np.testing.assert_allclose(jax.jit(jax.vmap(reverse))(points, directions), expected, atol=tolerance, rtol=0)
    np.testing.assert_allclose(jax.jit(jax.vmap(lambda v: reverse(point, v)))(directions),
                               [expected_product(np.asarray(point), np.asarray(v)) for v in directions], atol=tolerance, rtol=0)
    # Differentiating only the linear direction does not request a third
    # derivative of the quantum function at its fixed primal point.
    actual = jax.jvp(lambda v: reverse(point, v), (direction,), (directions[1],))[1]
    np.testing.assert_allclose(actual, expected_product(np.asarray(point), np.asarray(directions[1])), atol=tolerance, rtol=0)


def host_kernel(**options):
    from quantumbridge.interfaces.jax_autodiff import JAXBridgeLimits
    from quantumbridge.interfaces.native_host import NativeHostKernel
    jnp = pytest.importorskip("jax.numpy")
    node = QNode(lambda t, x: (t.ry(x[0], 0), t.rx(x[1], 0), (t.expval(PauliZ(0)), t.expval(PauliX(0))))[-1],
                 1, max_diff=2, interface="jax", **options)
    source, recorder, program = node._construct((jnp.array([.37, .2]),), {}, prepare_only=True)
    return NativeHostKernel(node, source, recorder, program, JAXBridgeLimits())


@pytest.mark.parametrize("budget", ["max_shifted_circuits", "max_total_tapes", "max_total_physical_shots"])
def test_transpose_preflights_total_output_row_work_before_any_execution(budget, monkeypatch):
    from quantumbridge import StatevectorDevice
    options = {"higher_order_limits": HigherOrderLimits(**{budget: 20 if budget == "max_shifted_circuits" else 25 if budget == "max_total_tapes" else 5000})}
    if budget == "max_total_physical_shots": options.update(shots=100, seed=7)
    kernel = host_kernel(**options)
    def forbidden(*a, **k): pytest.fail("aggregate transpose budget must reject before any native execution")
    monkeypatch.setattr(StatevectorDevice, "expectation", forbidden)
    monkeypatch.setattr(StatevectorDevice, "sample", forbidden)
    with pytest.raises(MemoryError, match=budget):
        kernel.run_second_transpose(np.array([.37, .2]), np.eye(2))


def test_transpose_validates_zero_and_invalid_inputs_without_dense_hessian():
    kernel = host_kernel(higher_order_limits=HigherOrderLimits(max_hessian_elements=1))
    result, metadata = kernel.run_second_transpose(np.array([.37, .2]), np.zeros((2, 2)))
    np.testing.assert_array_equal(result, [0., 0.])
    assert metadata["native_hvp_calls"] == metadata["total_physical_shots"] == 0
    for point, vector in [(np.array([float("nan"), .2]), np.zeros((2, 2))),
                          (np.array([.37, .2]), np.zeros(2)),
                          (np.array([.37, .2]), np.ones((2, 2), dtype=complex))]:
        with pytest.raises(ValueError): kernel.run_second_transpose(point, vector)


@pytest.mark.parametrize("interface", ["torch", "autograd", "jax", "tf"])
def test_real_sampled_framework_hvp_has_native_shift_receipts(interface, direction_only_spy):
    def circuit(t, x):
        t.ry(x, 0)
        return t.expval(PauliZ(0))
    node = QNode(circuit, 1, interface=interface, max_diff=2, shots=10000, seed=31, diff_method="parameter-shift")
    if interface == "torch":
        torch = pytest.importorskip("torch")
        x = torch.tensor(.37, dtype=torch.float64, requires_grad=True)
        first = torch.autograd.grad(node(x), x, create_graph=True)[0]
        actual = torch.autograd.grad(.4*first, x)[0].detach().numpy()
    elif interface == "autograd":
        autograd = pytest.importorskip("autograd")
        actual = autograd.grad(lambda x: .4*autograd.grad(node)(x))(.37)
    elif interface == "jax":
        jax, jnp = pytest.importorskip("jax"), pytest.importorskip("jax.numpy")
        actual = jax.jvp(jax.grad(node), (jnp.asarray(.37),), (jnp.asarray(.4),))[1]
    else:
        tf = pytest.importorskip("tensorflow")
        x = tf.Variable(.37, dtype=tf.float64)
        with tf.GradientTape() as outer:
            with tf.GradientTape() as inner:
                value = node(x)
            first = inner.gradient(value, x)
            contracted = .4*first
        actual = outer.gradient(contracted, x).numpy()
        assert node.last_metadata["observed_physical_shots"] == 130000
    np.testing.assert_allclose(actual, -.4*np.cos(.37), atol=.04, rtol=0)
    assert direction_only_spy
    for receipt in direction_only_spy:
        assert receipt["total_physical_shots"] == 80000
        assert receipt["second_order_work"]["direction_independent_sampling_schedule"]
        assert len(receipt["second_order_evaluations"]) == 8


def test_jax_linear_primitive_transpose_and_direction_derivative_match_independent_math():
    jax, jnp = pytest.importorskip("jax"), pytest.importorskip("jax.numpy")
    from quantumbridge.interfaces.jax_directional import DirectionalRule, directional_second
    dtype = jnp.float64 if jax.config.x64_enabled else jnp.float32
    kernel = host_kernel(higher_order_limits=HigherOrderLimits(max_hessian_elements=1))
    rule = DirectionalRule(kernel, np.dtype(dtype))
    point, direction = jnp.array([.37, .2], dtype=dtype), jnp.array([.4, -.3], dtype=dtype)
    z = np.cos(.37)*np.cos(.2)
    hz = np.array([[-z, np.sin(.37)*np.sin(.2)], [np.sin(.37)*np.sin(.2), -z]])
    hx = np.diag([-np.sin(.37), 0.])
    incoming = jnp.array([[.4, -.3], [.2, .1]], dtype=dtype)
    actual, = jax.linear_transpose(lambda v: directional_second(point, v, rule), direction)(incoming)
    tolerance = 1e-10 if jax.config.x64_enabled else 3e-6
    np.testing.assert_allclose(actual, hz @ np.asarray(incoming[0])+hx @ np.asarray(incoming[1]), atol=tolerance, rtol=0)
    _, actual = jax.jvp(lambda v: directional_second(point, v, rule), (direction,), (direction,))
    np.testing.assert_allclose(actual, [hz @ np.asarray(direction), hx @ np.asarray(direction)], atol=tolerance, rtol=0)


def test_jax_linear_primitive_invalid_abstract_shapes_and_third_point_derivatives_reject(monkeypatch):
    jax, jnp = pytest.importorskip("jax"), pytest.importorskip("jax.numpy")
    from quantumbridge import StatevectorDevice, UnsupportedFeature
    from quantumbridge.interfaces.jax_directional import DirectionalRule, directional_second
    kernel = host_kernel()
    point, direction = jnp.array([.37, .2]), jnp.array([.4, -.3])
    rule = DirectionalRule(kernel, np.dtype(point.dtype))
    monkeypatch.setattr(StatevectorDevice, "expectation", lambda *a, **k: pytest.fail("invalid directional rules must reject before quantum work"))
    with pytest.raises(ValueError, match="shapes/dtypes"):
        jax.eval_shape(lambda v: directional_second(point, v, rule), jax.ShapeDtypeStruct((3,), point.dtype))
    with pytest.raises(TypeError, match="float32/float64"):
        jax.eval_shape(lambda p: directional_second(p, p, rule), jax.ShapeDtypeStruct((2,), jnp.complex64))
    with pytest.raises(UnsupportedFeature, match="third"):
        jax.jvp(lambda p: directional_second(p, direction, rule), (point,), (jnp.ones_like(point),))


@pytest.mark.parametrize("limit", ["max_vmap_batch", "max_callback_executions"])
def test_jax_directional_mapped_budget_rejects_before_callback(limit, monkeypatch):
    from dataclasses import replace
    from quantumbridge import StatevectorDevice
    jax, jnp = pytest.importorskip("jax"), pytest.importorskip("jax.numpy")
    from quantumbridge.interfaces.jax_directional import DirectionalRule, directional_second
    kernel = host_kernel()
    kernel.limits = replace(kernel.limits, **{limit: 2})
    point = jnp.array([.37, .2])
    rule = DirectionalRule(kernel, np.dtype(point.dtype))
    monkeypatch.setattr(StatevectorDevice, "expectation", lambda *a, **k: pytest.fail("mapped budget must reject before any callback"))
    with pytest.raises(MemoryError, match=limit):
        jax.vmap(lambda v: directional_second(point, v, rule))(jnp.ones((3, 2), dtype=point.dtype))


def test_jax_directional_callback_failure_is_nan_not_a_zero_gradient(monkeypatch):
    jax, jnp = pytest.importorskip("jax"), pytest.importorskip("jax.numpy")
    from quantumbridge.interfaces.jax_directional import DirectionalRule, directional_second
    from quantumbridge.interfaces.native_host import NativeHostKernel
    kernel = host_kernel()
    point, direction = jnp.array([.37, .2]), jnp.array([.4, -.3])
    rule = DirectionalRule(kernel, np.dtype(point.dtype))
    def failure(*unused, **kwargs): raise MemoryError("injected directional budget failure")
    monkeypatch.setattr(NativeHostKernel, "run_second", failure)
    with pytest.raises(MemoryError, match="injected"):
        directional_second(point, direction, rule)
    value = jax.jit(lambda v: directional_second(point, v, rule))(direction)
    assert np.all(np.isnan(np.asarray(value)))
