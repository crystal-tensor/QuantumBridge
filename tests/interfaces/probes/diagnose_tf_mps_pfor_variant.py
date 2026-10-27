# Copyright 2026 QuantumBridge Contributors. Apache-2.0.
"""Explicit negative diagnostic, not an auto-collected supported-domain test.

The mathematical assertions remain real. An upstream variant failure is saved
as a failed diagnostic receipt, not relabelled as a passing implementation.
"""

import numpy as np
import pytest

from test_native_tf_mps_exact_closure import POINT, fixture, tf
from quantumbridge.qml import QNode
import quantumbridge as qb


@pytest.mark.parametrize("kind", ["pure_tensorflow", "native_mps"])
def test_active_forward_jacobian_loop_keeps_second_derivative(kind):
    direction = np.array([.4, -.3])
    if kind == "pure_tensorflow":
        def function(x):
            return tf.stack((tf.sin(x[0]) * tf.cos(x[1]), tf.cos(x[0]) + tf.exp(.2 * x[1])))
        p, q = POINT
        expected_j = np.array([[np.cos(p) * np.cos(q), -np.sin(p) * np.sin(q)],
            [-np.sin(p), .2 * np.exp(.2 * q)]])
        h = np.array([[[-np.sin(p) * np.cos(q), -np.cos(p) * np.sin(q)],
            [-np.cos(p) * np.sin(q), -np.sin(p) * np.cos(q)]],
            [[-np.cos(p), 0.], [0., .04 * np.exp(.2 * q)]]])
    else:
        _, native = fixture(2, 2)
        dense = QNode(native.fn, 2, max_diff=2, device=qb.StatevectorDevice())
        expected_j, h = np.array(dense.jacobian(POINT)), np.array(dense.hessian(POINT))
        _, node = fixture(2, 2, interface="tensorflow")
        function = lambda x: tf.stack(node(x))

    @tf.function(autograph=False)
    def graph(x, d):
        with tf.autodiff.ForwardAccumulator(x, d) as forward:
            with tf.GradientTape(persistent=True) as reverse:
                reverse.watch(x)
                value = function(x)
            jacobian = reverse.jacobian(value, x, experimental_use_pfor=False)
        return jacobian, forward.jvp(jacobian)

    jacobian, directional = graph(tf.constant(POINT), tf.constant(direction))
    np.testing.assert_allclose(jacobian, expected_j, atol=2e-9, rtol=0)
    assert directional is not None
    np.testing.assert_allclose(directional, np.einsum("ijk,k->ij", h, direction), atol=2e-9, rtol=0)
