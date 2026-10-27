# Copyright 2026 QuantumBridge Contributors. Apache-2.0.
"""TensorFlow's automatic Jacobian tracing after a real eager forward."""

import numpy as np
import pytest

import quantumbridge as qb
from quantumbridge.core.classical import UnsupportedFeature
from quantumbridge.execution.resource_context import ResourceScope
from quantumbridge.execution.resource_ledger import UnifiedResourceLedger
from quantumbridge.qml import QNode
from test_native_tf_managed_cached_execution import tf


def assert_tf_policy_error(error, feature):
    if isinstance(error, UnsupportedFeature):
        assert error.feature == feature
    else:
        # pfor/AutoGraph may wrap a native policy error. Check the exact
        # carrier and feature marker, not a blanket unsupported exception.
        assert type(error).__module__.startswith("tensorflow.")
        assert type(error).__name__ in {"StagingError", "InvalidArgumentError"}
        assert "QB_UNSUPPORTED["+feature+"]" in str(error)


def node_and_reference(method, maximum=2):
    def program(tape, point):
        tape.ry(point[0]**2+point[1], 0)
        return tape.expval(qb.PauliZ(0)), tape.expval(qb.PauliX(0))
    point = np.array([0.37, 0.82])
    angle, slope = point[0]**2+point[1], np.array([2*point[0], 1.])
    jacobian = np.array([-np.sin(angle)*slope, np.cos(angle)*slope])
    hessians = np.array([-np.cos(angle)*np.outer(slope, slope)-np.sin(angle)*np.diag([2., 0.]),
        -np.sin(angle)*np.outer(slope, slope)+np.cos(angle)*np.diag([2., 0.])])
    return QNode(program, 1, interface="tensorflow", diff_method=method, max_diff=maximum), tf.constant(point, tf.float64), jacobian, hessians


@pytest.mark.parametrize("method", ["best", "adjoint", "parameter-shift"])
@pytest.mark.parametrize("pfor", [False, True])
def test_eager_forward_jacobian_and_complete_second_jets(method, pfor):
    node, point, expected_jacobian, expected_hessians = node_and_reference(method)
    with tf.GradientTape(persistent=True) as outer:
        outer.watch(point)
        with tf.GradientTape(persistent=True) as inner:
            inner.watch(point)
            values = tf.stack(node(point))
        jacobian = inner.jacobian(values, point, experimental_use_pfor=pfor)
    hessians = outer.jacobian(jacobian, point, experimental_use_pfor=pfor)
    np.testing.assert_allclose(jacobian, expected_jacobian, atol=1e-11, rtol=0)
    np.testing.assert_allclose(hessians, expected_hessians, atol=1e-10, rtol=0)
    if pfor:
        assert node.last_metadata["traced_eager_vjp"] is True
        assert node.last_metadata["traced_vjp_accounting"] == "OUT_OF_SCOPE"


def test_traced_eager_vjp_does_not_bypass_an_active_shared_scope():
    node, point, _, _ = node_and_reference("adjoint")
    parent = UnifiedResourceLedger()
    with ResourceScope(parent):
        with tf.GradientTape() as reverse:
            reverse.watch(point)
            values = tf.stack(node(point))
        before = parent.receipt()["consumed_derivative_work"]
        with pytest.raises(Exception, match="shared-ledger") as failure:
            reverse.jacobian(values, point)
        assert_tf_policy_error(failure.value, "tensorflow_unified_graph_resources")
        assert parent.receipt()["consumed_derivative_work"] == before
    assert parent.receipt()["live_memory_bytes"] == 0


def test_retraced_jacobian_does_not_upgrade_max_diff_one():
    node, point, expected, _ = node_and_reference("adjoint", maximum=1)
    with tf.GradientTape() as outer:
        outer.watch(point)
        with tf.GradientTape() as inner:
            inner.watch(point)
            values = tf.stack(node(point))
        jacobian = inner.jacobian(values, point)
    np.testing.assert_allclose(jacobian, expected, atol=1e-11, rtol=0)
    with pytest.raises(Exception, match="max_diff=2") as failure:
        outer.jacobian(jacobian, point)
    assert_tf_policy_error(failure.value, "higher_order_derivatives")
