# Copyright 2026 QuantumBridge Contributors. Apache-2.0.
"""Wider real public scalar-capture RoF math; unsupported results stay red."""

import numpy as np
import pytest

import quantumbridge as qb
from quantumbridge.qml import QNode
from test_native_tf_managed_cached_execution import tf


@pytest.mark.parametrize("source_kind", ["direct_tf", "remapped_native", "mixed_native"])
@pytest.mark.parametrize("loss_kind", ["square", "exponential_cubic"])
def test_real_scalar_capture_cached_rof_keeps_the_complete_chain_rule(source_kind, loss_kind):
    p, q = qb.ParameterVector("input", 2)
    source = qb.QuantumCircuit(1)
    source.ry(p*p+q, 0)
    builder = QNode.from_circuit(source, qb.PauliZ(0)).fn
    def program(tape, point):
        if source_kind == "direct_tf":
            tape.ry(tf.sin(point[0])**2+point[1], 0)
            return tape.expval(qb.PauliZ(0))
        result = builder(tape, tf.reverse(point, [0]) if source_kind == "remapped_native" else point)
        if source_kind == "mixed_native":
            tape.rx(.2*point[0], 0)
        return result
    node = QNode(program, 1, interface="tensorflow", diff_method="adjoint", max_diff=2)
    handle = node.compile_tensorflow(input_signature=[tf.TensorSpec((2,), tf.float64)])
    direction = tf.constant([.4, -.3], tf.float64)
    for raw in ([.37, .82], [.41, .91]):
        point = tf.constant(raw, tf.float64)
        with tf.GradientTape() as reverse:
            reverse.watch(point)
            with tf.autodiff.ForwardAccumulator(point, direction) as forward:
                y = handle(point)
                loss = (y-.3)**2 if loss_kind == "square" else tf.exp(y)+.2*y**3
            tangent = forward.jvp(loss)
        actual = reverse.gradient(tangent, point)
        x, z = raw
        if source_kind == "direct_tf":
            angle, slope, classical_h = np.sin(x)**2+z, np.array([np.sin(2*x), 1.]), np.diag([2*np.cos(2*x), 0.])
        else:
            angle = z*z+x if source_kind == "remapped_native" else x*x+z
            slope = np.array([1., 2*z]) if source_kind == "remapped_native" else np.array([2*x, 1.])
            classical_h = np.diag([0., 2.]) if source_kind == "remapped_native" else np.diag([2., 0.])
        value, gradient = np.cos(angle), -np.sin(angle)*slope
        hessian = -np.cos(angle)*np.outer(slope, slope)-np.sin(angle)*classical_h
        if source_kind == "mixed_native":
            b, other = .2*x, np.array([.2, 0.])
            gradient = gradient*np.cos(b)-np.cos(angle)*np.sin(b)*other
            hessian = hessian*np.cos(b)-np.cos(angle)*np.cos(b)*np.outer(other, other)+np.sin(angle)*np.sin(b)*(np.outer(slope, other)+np.outer(other, slope))
            value *= np.cos(b)
        first, second = (2*(value-.3), 2.) if loss_kind == "square" else (np.exp(value)+.6*value*value, np.exp(value)+1.2*value)
        expected = second*gradient*(gradient @ [.4, -.3])+first*hessian @ [.4, -.3]
        assert actual is not None
        np.testing.assert_allclose(actual, expected, atol=2e-9, rtol=0)
