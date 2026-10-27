# Copyright 2026 QuantumBridge Contributors. Apache-2.0.
"""Approved orders on the same managed native callable, not a new API."""

import numpy as np
import pytest

import quantumbridge as qb
from quantumbridge.core.classical import UnsupportedFeature
from quantumbridge.diff import HigherOrderLimits
from quantumbridge.qml import QNode
from test_native_tf_managed_cached_execution import tf


def simple(max_diff=2, **options):
    p, q = qb.ParameterVector("point", 2)
    source = qb.QuantumCircuit(1)
    source.ry(p*p+q, 0)
    node = QNode.from_circuit(source, qb.PauliZ(0), interface="tensorflow", diff_method="adjoint",
        max_diff=max_diff, **options)
    handle = node.compile_tensorflow(input_signature=[tf.TensorSpec((2,), tf.float64)])
    return node, handle


def reference():
    a, slope = .37**2+.82, np.array([.74, 1.])
    return np.cos(a), -np.sin(a)*slope, -np.cos(a)*np.outer(slope, slope)-np.sin(a)*np.diag([2., 0.])


def test_max_diff_one_allows_actual_first_jvp():
    node, handle = simple(max_diff=1)
    point, direction = tf.constant([.37, .82], tf.float64), tf.constant([.4, -.3], tf.float64)
    with tf.autodiff.ForwardAccumulator(point, direction) as forward:
        value = handle(point)
    expected, gradient, _ = reference()
    np.testing.assert_allclose(value, expected, atol=2e-12, rtol=0)
    np.testing.assert_allclose(forward.jvp(value), gradient @ [.4, -.3], atol=2e-11, rtol=0)


def test_max_diff_one_refuses_a_real_second_quantum_derivative():
    node, handle = simple(max_diff=1)
    point = tf.constant([.37, .82], tf.float64)
    with tf.GradientTape() as outer:
        outer.watch(point)
        with tf.GradientTape() as inner:
            inner.watch(point)
            value = handle(point)
        gradient = inner.gradient(value, point)
        weighted = tf.reduce_sum(gradient)
    with pytest.raises(UnsupportedFeature, match="second"):
        outer.gradient(weighted, point)


def test_actual_second_derivative_can_be_recorded_before_true_third_refusal():
    node, handle = simple()
    point = tf.constant([.37, .82], tf.float64)
    with tf.GradientTape() as third:
        third.watch(point)
        with tf.GradientTape() as second:
            second.watch(point)
            with tf.GradientTape() as first:
                first.watch(point)
                value = handle(point)
            gradient = first.gradient(value, point)
            scalar = tf.reduce_sum(gradient)
        second_gradient = second.gradient(scalar, point)
        scalar_second = tf.reduce_sum(second_gradient)
    np.testing.assert_allclose(second_gradient, np.sum(reference()[2], axis=0), atol=2e-10, rtol=0)
    with pytest.raises(UnsupportedFeature, match="third"):
        third.gradient(scalar_second, point)


@pytest.mark.parametrize("direction", [[.4, -.3], [-.1, .8]])
def test_streamed_managed_hvp_keeps_full_hessian_budget_separate(direction, monkeypatch):
    node, handle = simple(higher_order_limits=HigherOrderLimits(max_hessian_elements=1))
    point = tf.constant([.37, .82], tf.float64)
    monkeypatch.setattr(QNode, "compute_hessian", lambda *a, **k: pytest.fail("Managed HVP built a host Hessian"))
    monkeypatch.setattr(tf.GradientTape, "jacobian", lambda *a, **k: pytest.fail("Managed HVP built a complete Jacobian/Hessian"))
    with tf.GradientTape() as outer:
        outer.watch(point)
        with tf.GradientTape() as inner:
            inner.watch(point)
            value = handle(point)
        gradient = inner.gradient(value, point)
        weighted = tf.reduce_sum(gradient*tf.constant(direction, tf.float64))
    actual = outer.gradient(weighted, point)
    np.testing.assert_allclose(actual, reference()[2] @ direction, atol=2e-10, rtol=0)
