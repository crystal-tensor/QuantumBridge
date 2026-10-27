# Copyright 2026 QuantumBridge Contributors. Apache-2.0.
"""Native scalar J/H references independent of the captured TF function."""

import numpy as np
import pytest

import quantumbridge as qb
from quantumbridge.interfaces.tensorflow_scalar_lowering import lower_scalar_graph
from test_native_tf_managed_cached_execution import tf


def model(name, x):
    p, q = x[0], x[1]
    if name == "sin":
        return tf.stack([tf.sin(p), q])
    if name == "reverse":
        return tf.reverse(x, [0])
    if name == "layout":
        matrix = tf.reshape(tf.stack([p, q, p+2*q, tf.sin(p*q+.4)]), (2, 2))
        return tf.reverse(matrix, [1])[:, 0]
    if name == "square":
        return tf.stack([tf.sin(p)**2+q, tf.cos(p*q)])
    return tf.stack([tf.sin(p*q+.4), tf.exp(p+q)])


def reference(name, point):
    p, q = point
    slope, cross = np.array([q, p]), np.array([[0., 1.], [1., 0.]])
    a, e = p*q+.4, np.exp(p+q)
    if name == "sin":
        return np.array([np.sin(p), q]), np.array([[np.cos(p), 0.], [0., 1.]]), np.array([[[-np.sin(p), 0.], [0., 0.]], np.zeros((2, 2))])
    if name == "reverse":
        return np.array([q, p]), np.array([[0., 1.], [1., 0.]]), np.zeros((2, 2, 2))
    if name == "layout":
        return np.array([q, np.sin(a)]), np.array([[0., 1.], np.cos(a)*slope]), np.array([np.zeros((2, 2)), -np.sin(a)*np.outer(slope, slope)+np.cos(a)*cross])
    if name == "square":
        b = p*q
        return np.array([np.sin(p)**2+q, np.cos(b)]), np.array([[np.sin(2*p), 1.], -np.sin(b)*slope]), np.array([np.diag([2*np.cos(2*p), 0.]), -np.cos(b)*np.outer(slope, slope)-np.sin(b)*cross])
    return np.array([np.sin(a), e]), np.array([np.cos(a)*slope, [e, e]]), np.array([-np.sin(a)*np.outer(slope, slope)+np.cos(a)*cross, np.full((2, 2), e)])


def capture(name):
    function = tf.function(lambda x: model(name, x), input_signature=[tf.TensorSpec((2,), tf.float64)], autograph=False)
    concrete = function.get_concrete_function()
    return concrete.graph.as_graph_def(add_shapes=True), concrete.inputs[0].name, concrete.outputs[0].name


@pytest.mark.parametrize("name", ["sin", "reverse", "layout", "nonlinear", "square"])
@pytest.mark.parametrize("point", [[.37, .82], [.41, .91], [-.7, .2], [0., .2]])
def test_native_binding_retains_full_values_uuid_columns_jacobians_and_hessians(name, point, monkeypatch):
    graph, input_name, output_name = capture(name)
    parameters = tuple(qb.ParameterVector("logical_input", 2))
    monkeypatch.setattr(tf, "import_graph_def", lambda *a, **k: pytest.fail("Native scalar source was imported as a TF graph"))
    binding, work = lower_scalar_graph(graph, input_name=input_name, output_name=output_name,
        parameters=parameters, allow_square=True)
    assert binding.parameters == parameters and work["graph_bytes"] == graph.ByteSize()
    x = tf.constant(point, tf.float64)
    with tf.GradientTape(persistent=True) as outer:
        outer.watch(x)
        with tf.GradientTape(persistent=True) as inner:
            inner.watch(x)
            value = tf.stack(binding.evaluate(tuple(tf.unstack(x))))
        jacobian = inner.jacobian(value, x)
        vjp = inner.gradient(value, x, output_gradients=tf.constant([.7, -.2], tf.float64))
    hessian = outer.jacobian(jacobian, x, unconnected_gradients=tf.UnconnectedGradients.ZERO)
    y, j, h = reference(name, point)
    np.testing.assert_allclose(value, y, atol=2e-12, rtol=0)
    np.testing.assert_allclose(jacobian, j, atol=2e-11, rtol=0)
    np.testing.assert_allclose(hessian, h, atol=2e-10, rtol=0)
    np.testing.assert_allclose(vjp, np.array([.7, -.2]) @ j, atol=2e-11, rtol=0)
    np.testing.assert_allclose(np.einsum("oij,j->oi", hessian, [.4, -.3]), h @ [.4, -.3], atol=2e-10, rtol=0)
