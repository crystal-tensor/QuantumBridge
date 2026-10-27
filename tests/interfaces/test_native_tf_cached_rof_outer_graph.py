# Copyright 2026 QuantumBridge Contributors. Apache-2.0.
"""Separate external graph mathematics from managed Python accounting."""

import gc
import math

import numpy as np
import pytest

from quantumbridge.core.classical import UnsupportedFeature
from quantumbridge.execution.resource_context import ResourceScope
from quantumbridge.execution.resource_ledger import UnifiedResourceLedger
from quantumbridge.execution.resource_limits import UnifiedExecutionLimits
from test_native_tf_managed_cached_execution import make_node, tf
from test_native_tf_trace_inline_qnode import POINTS, forbid_rebuild


def frozen():
    node, source = make_node()
    handle = node.compile_tensorflow_inline(parameters=tuple(source.parameters),
        input_signature=[tf.TensorSpec((2,), tf.float64)])
    return node, source, handle


@pytest.mark.parametrize("mode", ["for", "rof", "tape"])
@pytest.mark.parametrize("loss_kind", ["square", "exponential_cubic"])
def test_user_cached_outer_graph_cotraces_real_native_loss_and_derivatives(mode, loss_kind, monkeypatch):
    node, _, handle = frozen()
    forbid_rebuild(monkeypatch)
    weights, direction = tf.constant([.7, -.2], tf.float64), tf.constant([.4, -.3], tf.float64)
    def execute(point):
        def loss():
            y = tf.stack(handle(point))
            return tf.reduce_sum(weights*((y-.3)**2 if loss_kind == "square" else tf.exp(y)+.2*y**3))
        if mode == "for":
            with tf.autodiff.ForwardAccumulator(point, direction) as forward:
                with tf.GradientTape() as reverse:
                    reverse.watch(point)
                    value = loss()
                gradient = reverse.gradient(value, point)
            return forward.jvp(gradient)
        if mode == "rof":
            with tf.GradientTape() as reverse:
                reverse.watch(point)
                with tf.autodiff.ForwardAccumulator(point, direction) as forward:
                    value = loss()
                tangent = forward.jvp(value)
            return reverse.gradient(tangent, point)
        with tf.GradientTape() as outer:
            outer.watch(point)
            with tf.GradientTape() as inner:
                inner.watch(point)
                value = loss()
            gradient = inner.gradient(value, point)
            tangent = tf.reduce_sum(gradient*direction)
        return outer.gradient(tangent, point)
    function = tf.function(execute, input_signature=[tf.TensorSpec((2,), tf.float64)], autograph=False)
    concrete = function.get_concrete_function()
    for case in (*POINTS, POINTS[0]):
        y, j, h = (np.array(case[key]) for key in ("outputs", "jacobian", "hessians"))
        first, second = (2*(y-.3), np.full(2, 2.)) if loss_kind == "square" else (np.exp(y)+.6*y*y, np.exp(y)+1.2*y)
        expected = j.T @ (np.array([.7, -.2])*second*(j @ [.4, -.3]))+np.einsum("o,oij,j->i", np.array([.7, -.2])*first, h, [.4, -.3])
        np.testing.assert_allclose(function(tf.constant(case["point"], tf.float64)), expected, atol=2e-9, rtol=0)
        assert function.get_concrete_function() is concrete
    assert function.experimental_get_tracing_count() == 1
    graph = concrete.graph.as_graph_def()
    nodes = list(graph.node)+[n for definition in graph.library.function for n in definition.node_def]
    assert not any(n.op in {"PyFunc", "EagerPyFunc", "PyFuncStateless"} for n in nodes)
    assert not any("prepare" in definition.signature.name for definition in graph.library.function)
    assert handle.metadata["external_graph_execution"] == "OUT_OF_SCOPE"


@pytest.mark.parametrize("change", ["owner_expired", "limits_tightened", "source_changed"])
def test_post_trace_ownership_is_explicitly_outside_direct_outer_graph_execution(change):
    node, source, handle = frozen()
    function = tf.function(lambda point: tf.stack(handle(point)),
        input_signature=[tf.TensorSpec((2,), tf.float64)], autograph=False)
    concrete = function.get_concrete_function()
    point = tf.constant(POINTS[0]["point"], tf.float64)
    if change == "owner_expired":
        del node
        gc.collect()
    elif change == "limits_tightened":
        node.unified_limits = UnifiedExecutionLimits(max_derivative_work=0)
    else:
        source.x(1)
    ledger = UnifiedResourceLedger()
    with ResourceScope(ledger):
        np.testing.assert_allclose(concrete(point), POINTS[0]["outputs"], atol=3e-12, rtol=0)
    assert ledger.receipt()["consumed_derivative_work"] == 0
    assert handle.metadata["controlled_execution"] == "OUT_OF_SCOPE"
    if change != "source_changed":
        with pytest.raises(UnsupportedFeature, match="owner|configuration"):
            handle(point)
    else:
        np.testing.assert_allclose(handle(point), POINTS[0]["outputs"], atol=3e-12, rtol=0)


def test_inline_python_entry_refuses_tracing_with_a_shared_ledger():
    node, _, handle = frozen()
    function = tf.function(handle, input_signature=[tf.TensorSpec((2,), tf.float64)], autograph=False)
    ledger = UnifiedResourceLedger()
    with ResourceScope(ledger), pytest.raises(UnsupportedFeature, match="shared-ledger|scope"):
        function.get_concrete_function()
    assert ledger.receipt()["consumed_derivative_work"] == 0


@pytest.mark.parametrize("point", [[float("nan"), .82], [float("inf"), .82], [0., math.sqrt(2*math.pi-.4)]])
def test_same_cached_outer_value_graph_checks_runtime_nan_inf_and_cut(point):
    node, _, handle = frozen()
    function = tf.function(lambda x: tf.stack(handle(x)), input_signature=[tf.TensorSpec((2,), tf.float64)], autograph=False)
    concrete = function.get_concrete_function()
    with pytest.raises(tf.errors.InvalidArgumentError):
        concrete(tf.constant(point, tf.float64))
    np.testing.assert_allclose(concrete(tf.constant(POINTS[0]["point"], tf.float64)), POINTS[0]["outputs"], atol=3e-12, rtol=0)
    assert function.experimental_get_tracing_count() == 1
