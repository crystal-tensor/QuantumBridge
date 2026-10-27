# Copyright 2026 QuantumBridge Contributors. Apache-2.0.
"""Real native plans, pfor quantum curvature and full format lineage."""

import numpy as np
import pytest

from quantumbridge.diff import HigherOrderLimits
from quantumbridge.execution.resource_limits import UnifiedExecutionLimits
from test_native_tf_managed_cached_execution import tf
from test_native_tf_whole_qnode_execution import CASES, node_for, restore, source_and_observables


@pytest.mark.parametrize("case", CASES, ids=lambda case: case["name"])
@pytest.mark.parametrize("transport", [None, "ir", "qpy"])
@pytest.mark.parametrize("traced", [False, True])
def test_real_native_inline_pfor_retains_all_quantum_curvature(case, transport, traced, monkeypatch):
    source, observables = source_and_observables(case)
    source = restore(source, transport)
    node = node_for(source, observables)
    node.higher_order_limits = HigherOrderLimits(max_adjoint_operations=1_000_000_000)
    node.unified_limits = UnifiedExecutionLimits(max_derivative_work=1_000_000_000)
    inline = node.compile_tensorflow_inline(parameters=tuple(source.parameters), input_signature=[tf.TensorSpec((2,), tf.float64)])
    from test_native_tf_trace_inline_qnode import forbid_rebuild
    forbid_rebuild(monkeypatch)
    def execute(point):
        with tf.GradientTape(persistent=True) as outer:
            outer.watch(point)
            with tf.GradientTape(persistent=True) as inner:
                inner.watch(point)
                y = tf.stack(inline(point))
                square = tf.reduce_sum(tf.constant([0.7, -0.2], tf.float64)*(y-0.3)**2)
                exponential = tf.reduce_sum(tf.constant([0.7, -0.2], tf.float64)*(tf.exp(y)+0.2*y**3))
            jacobian = inner.jacobian(y, point, experimental_use_pfor=True)
            gradients = (inner.gradient(square, point), inner.gradient(exponential, point))
        return y, jacobian, outer.jacobian(jacobian, point, experimental_use_pfor=True), tuple(
            outer.jacobian(g, point, experimental_use_pfor=True) for g in gradients)
    function = tf.function(execute, input_signature=[tf.TensorSpec((2,), tf.float64)], autograph=False) if traced else execute
    y, j, h = np.asarray(case["outputs"]), np.asarray(case["jacobian"]), np.asarray(case["hessians"])
    actual_y, actual_j, actual_h, actual_loss_h = function(tf.constant(case["point"], tf.float64))
    for actual, expected in ((actual_y, y), (actual_j, j), (actual_h, h)):
        np.testing.assert_allclose(actual, expected, atol=2e-9, rtol=0)
    for result, first, second in ((actual_loss_h[0], 2*(y-0.3), np.full(2, 2.)),
            (actual_loss_h[1], np.exp(y)+0.6*y*y, np.exp(y)+1.2*y)):
        expected = j.T @ np.diag(np.array([0.7, -0.2])*second) @ j + np.einsum("o,oij->ij", np.array([0.7, -0.2])*first, h)
        np.testing.assert_allclose(result, expected, atol=2e-9, rtol=0)
    if traced:
        assert function.experimental_get_tracing_count() == 1
        graph = function.get_concrete_function().graph.as_graph_def()
        assert not any(n.op in {"PyFunc", "EagerPyFunc", "PyFuncStateless"} for n in list(graph.node)+[
            node for f in graph.library.function for node in f.node_def])


@pytest.mark.parametrize("case", CASES, ids=lambda case: case["name"])
@pytest.mark.parametrize("transport", [None, "ir", "qpy"])
def test_same_frozen_pfor_plan_preserves_complete_complex_primal(case, transport, monkeypatch):
    source, observables = source_and_observables(case)
    source = restore(source, transport)
    node = node_for(source, observables)
    node.higher_order_limits = HigherOrderLimits(max_adjoint_operations=1_000_000_000)
    node.unified_limits = UnifiedExecutionLimits(max_derivative_work=1_000_000_000)
    inline = node.compile_tensorflow_inline(parameters=tuple(source.parameters), input_signature=[tf.TensorSpec((2,), tf.float64)])
    from test_native_tf_trace_inline_qnode import forbid_rebuild
    forbid_rebuild(monkeypatch)
    state = inline.state(tf.constant(case["point"], tf.float64))
    raw = np.array(case["state"])[:, 0]
    np.testing.assert_allclose(state, raw[:, 0]+1j*raw[:, 1], atol=3e-12, rtol=0)
