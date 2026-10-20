# Copyright 2026 QuantumBridge Contributors.
# Licensed under the Apache License, Version 2.0.
"""Real TensorFlow function outcomes, independent mathematical references."""

import numpy as np
import pytest

tf = pytest.importorskip("tensorflow")

from quantumbridge import Hamiltonian, PauliX, PauliZ, StatevectorDevice, UnsupportedFeature
from quantumbridge.execution import UnifiedExecutionLimits
from quantumbridge.qml import QNode
from quantumbridge.transforms import split_non_commuting


def test_same_tf_function_runtime_work_budget_success_failure_success():
    def fn(t, x):
        t.ry(x[0]*x[0], 0)
        return t.expval(PauliZ(0))
    qnode = QNode(fn, 1, interface="tf", max_diff=2, diff_method="parameter-shift",
        unified_limits=UnifiedExecutionLimits(max_derivative_work=4))
    compiled = tf.function(lambda x: qnode.tensorflow_hvp_with_status(tf.ones_like(x), x), autograph=False)
    for point, expected in ((0., 0), (.3, 3), (0., 0)):
        value, status = compiled(tf.constant([point], tf.float64))
        assert int(status) == expected
        if expected: assert np.all(np.isnan(value))
        else: np.testing.assert_allclose(value, [0.], atol=1e-11)


def node(**options):
    def fn(t, x):
        t.ry(x[0], 0)
        return t.expval(PauliZ(0))
    return QNode(fn, 1, interface="tf", max_diff=2, **options)


def test_same_tf_function_hvp_valid_invalid_valid_has_current_status():
    qnode = node()
    compiled = tf.function(lambda x: qnode.tensorflow_hvp_with_status(tf.ones_like(x), x), autograph=False)
    for x in (.2, np.nan, .7, .2):
        product, status = compiled(tf.constant([x], tf.float64))
        assert int(status) == (1 if np.isnan(x) else 0)
        np.testing.assert_allclose(product, [np.nan if np.isnan(x) else -np.cos(x)], atol=1e-11)


def test_tf_function_hvp_budget_is_not_forward_success():
    qnode = node(unified_limits=UnifiedExecutionLimits(max_derivative_work=1))
    x = tf.constant([.3], tf.float64)
    value, status = tf.function(qnode.tensorflow_value_with_status, autograph=False)(x)
    assert int(status) == 0
    np.testing.assert_allclose(value, np.cos(.3), atol=1e-12)
    product, status = tf.function(lambda x: qnode.tensorflow_hvp_with_status(tf.ones_like(x), x), autograph=False)(x)
    assert int(status) == 3 and np.all(np.isnan(product))


def test_tf_function_finite_second_adjoint_has_unsupported_status():
    qnode = node(diff_method="second_adjoint", shots=20, seed=2)
    product, status = tf.function(lambda x: qnode.tensorflow_hvp_with_status(tf.ones_like(x), x), autograph=False)(tf.constant([.3], tf.float64))
    assert int(status) == 2 and np.all(np.isnan(product))


def test_tf_function_native_exception_has_runtime_status(monkeypatch):
    def fail(*a, **k): raise RuntimeError("injected test failure")
    monkeypatch.setattr(StatevectorDevice, "statevector", fail)
    qnode = node()
    product, status = tf.function(lambda x: qnode.tensorflow_hvp_with_status(tf.ones_like(x), x), autograph=False)(tf.constant([.3], tf.float64))
    assert int(status) == 4 and np.all(np.isnan(product))


def test_tf_jacobian_vjp_hessian_queries_use_real_native_math():
    qnode = node(diff_method="adjoint")
    x = tf.constant([.3], tf.float64)
    jac, status = tf.function(qnode.tensorflow_jacobian_with_status, autograph=False)(x)
    assert int(status) == 0
    product, status = tf.function(lambda x: qnode.tensorflow_vjp_with_status(tf.constant(2., tf.float64), x), autograph=False)(x)
    assert int(status) == 0
    hessian, status = tf.function(qnode.tensorflow_hessian_with_status, autograph=False)(x)
    assert int(status) == 0
    np.testing.assert_allclose(jac, [-np.sin(.3)], atol=1e-12)
    np.testing.assert_allclose(product, [-2*np.sin(.3)], atol=1e-12)
    np.testing.assert_allclose(hessian, [[-np.cos(.3)]], atol=1e-12)


def test_tf_nonlinear_gate_coefficient_hvp_retains_both_source_maps():
    def fn(t, x):
        t.ry(tf.sin(x[0])+2*x[0], 0)
        return t.expval(Hamiltonian([(.7+.1*x[0], PauliX(0)), (.2, PauliX(0).tensor(PauliZ(1)))]))
    qnode = split_non_commuting(QNode(fn, 2, interface="tf", max_diff=2, diff_method="adjoint"))
    x, v = .37, .4
    angle, first, coefficient = np.sin(x)+2*x, np.cos(x)+2, .9+.1*x
    expected = .2*np.cos(angle)*first-coefficient*np.sin(angle)*first**2-coefficient*np.cos(angle)*np.sin(x)
    product, status = tf.function(lambda x: qnode.tensorflow_hvp_with_status(tf.constant([v], tf.float64), x), autograph=False)(tf.constant([x], tf.float64))
    assert int(status) == 0
    np.testing.assert_allclose(product, [v*expected], atol=1e-10)


def test_tf_query_payload_extra_nested_tape_explicitly_rejects():
    qnode, x = node(), tf.Variable([.3], dtype=tf.float64)
    with tf.GradientTape() as outer:
        product, status = qnode.tensorflow_hvp_with_status(tf.ones_like(x), x)
    assert int(status) == 0
    with pytest.raises(UnsupportedFeature, match="Differentiate the QNode"):
        outer.gradient(product, x)


def test_tf_vjp_preserves_native_output_key_order_not_tf_nest_sorting():
    def fn(t, x):
        t.ry(x[0], 0)
        return {"z": t.expval(PauliZ(0)), "a": t.expval(PauliX(0))}
    qnode = QNode(fn, 1, interface="tf", max_diff=2)
    compiled = tf.function(lambda x: qnode.tensorflow_vjp_with_status({"a": tf.constant(.7, tf.float64),
        "z": tf.constant(.2, tf.float64)}, x), autograph=False)
    product, status = compiled(tf.constant([.3], tf.float64))
    assert int(status) == 0
    np.testing.assert_allclose(product, [-.2*np.sin(.3)+.7*np.cos(.3)], atol=1e-12)


def test_tf_complex_cotangent_and_hidden_variable_explicitly_reject():
    qnode = node()
    with pytest.raises(ValueError, match="dtypes"):
        qnode.tensorflow_vjp_with_status(tf.constant(1.+.2j), tf.constant([.3], tf.float64))
    hidden = tf.Variable(.2, dtype=tf.float64)
    def fn(t, x):
        t.ry(x[0]+hidden, 0)
        return t.expval(PauliZ(0))
    qnode = QNode(fn, 1, interface="tf", max_diff=2)
    with pytest.raises(UnsupportedFeature, match="explicit derivative-query input"):
        qnode.tensorflow_hvp_with_status(tf.constant([1.], tf.float64), tf.constant([.3], tf.float64))


def test_tf_static_dtype_shape_order_and_direction_contracts_reject():
    qnode = node()
    with pytest.raises(TypeError): qnode.tensorflow_jacobian_with_status(tf.constant([1], tf.int32))
    with pytest.raises(UnsupportedFeature, match="one floating array"):
        qnode.tensorflow_jacobian_with_status(tf.constant([.3]), tf.constant([.2]))
    with pytest.raises(UnsupportedFeature):
        tf.function(qnode.tensorflow_jacobian_with_status, autograph=False).get_concrete_function(tf.TensorSpec([None], tf.float64))
    with pytest.raises(ValueError): qnode.tensorflow_hvp_with_status(tf.constant([1., 2.]), tf.constant([.3]))
    first_order = QNode(lambda t, x: (t.ry(x[0], 0), t.expval(PauliZ(0)))[-1], 1, interface="tf")
    with pytest.raises(UnsupportedFeature, match="max_diff=2"):
        first_order.tensorflow_hessian_with_status(tf.constant([.3]))


def test_tf_distributed_query_is_explicitly_unsupported(monkeypatch):
    monkeypatch.setattr(tf.distribute, "has_strategy", lambda: True)
    with pytest.raises(UnsupportedFeature, match="local CPU"):
        node().tensorflow_jacobian_with_status(tf.constant([.3]))


def test_tf_tuple_vjp_checks_actual_container_before_execution():
    def fn(t, x):
        t.ry(x[0], 0)
        return (t.expval(PauliZ(0)), t.expval(PauliX(0)))
    qnode = QNode(fn, 1, interface="tf", max_diff=2)
    point = tf.constant([.3], tf.float64)
    product, status = qnode.tensorflow_vjp_with_status((.2, .7), point)
    assert int(status) == 0
    np.testing.assert_allclose(product, [-.2*np.sin(.3)+.7*np.cos(.3)], atol=1e-12)
    with pytest.raises(ValueError, match="containers"):
        qnode.tensorflow_vjp_with_status([.2, .7], point)


def test_native_mapped_host_validates_source_maps_before_quantum(monkeypatch):
    from quantumbridge.interfaces.native_host import NativeHostKernel
    from quantumbridge.interfaces.tensorflow_autodiff import TensorFlowBridgeLimits
    from quantumbridge.interfaces.framework_derivatives import execute_mapped_derivative
    qnode = node(diff_method="adjoint")
    source, recorder, program = qnode._construct((tf.constant([.3], tf.float64),), {}, prepare_only=True)
    kernel = NativeHostKernel(qnode, source, recorder, program, TensorFlowBridgeLimits(),
        interface="tensorflow", validate_derivatives=False)
    def call(**overrides):
        options = dict(raw=np.array([.3]), packed=np.array([.3]), classical=np.ones((1, 1)),
            second_map=np.zeros((1, 1, 0)), direction=np.ones(1), kind="vjp",
            input_shape=(1,), method="adjoint", limits=None, cotangent=.7)
        options.update(overrides)
        return execute_mapped_derivative(kernel, **options)
    actual = call()
    assert actual.code == 0
    np.testing.assert_allclose(actual.derivative, [-.7*np.sin(.3)], atol=1e-12)
    def forbidden(*a, **k): pytest.fail("invalid maps must reject before quantum execution")
    monkeypatch.setattr(StatevectorDevice, "statevector", forbidden)
    assert call(classical=np.ones((1, 2))).code == 1
    assert call(cotangent=[.7]).code == 1
    assert call(cotangent=np.nan).code == 1
    assert call(method="second_adjoint").code == 1
    assert call(kind="hvp", second_map=np.zeros((1, 1, 2))).code == 1


def test_ordinary_tf_graph_rejects_unimplemented_shared_account_instead_of_ignoring_limit():
    qnode = node(unified_limits=UnifiedExecutionLimits(max_total_memory_bytes=1))
    with pytest.raises(UnsupportedFeature, match="shared request account"):
        tf.function(qnode, autograph=False)(tf.constant([.3], tf.float64))
