# Copyright 2026 QuantumBridge Contributors. Apache-2.0.
"""Original managed contract, frozen native expressions and real loss RoF."""

import numpy as np
import pytest

from quantumbridge.diff.compiled_parameters import FrozenParameterBinding
from quantumbridge.execution.resource_context import ResourceScope
from quantumbridge.execution.resource_ledger import UnifiedResourceLedger
from test_native_tf_managed_cached_execution import compile_node, make_node, tf
from test_native_tf_trace_inline_qnode import POINTS, forbid_rebuild


def test_managed_native_circuit_keeps_the_original_frozen_parameter_map():
    node, source = make_node()
    handle = compile_node(node)
    binding = getattr(handle, "_frozen_binding", None)
    assert isinstance(binding, FrozenParameterBinding)
    assert tuple(binding.parameters) == tuple(source.parameters)
    assert len(binding.expressions) == handle._kernel.size


@pytest.mark.parametrize("mode", ["for", "rof", "tape"])
@pytest.mark.parametrize("loss_kind", ["square", "exponential_cubic"])
def test_same_managed_contract_keeps_loss_curvature_without_inner_cached_math(mode, loss_kind, monkeypatch):
    node, _ = make_node()
    handle = compile_node(node)
    forbid_rebuild(monkeypatch)
    complete = handle._run_graph
    def no_cached_function(function, packet):
        assert not hasattr(function, "get_concrete_function"), "Managed callable invoked an inner cached quantum graph"
        return complete(function, packet)
    monkeypatch.setattr(handle, "_run_graph", no_cached_function)
    function_type, pack = type(handle._pack), handle._pack
    call = function_type.__call__
    def no_cached_pack(function, *args, **kwargs):
        assert function is not pack, "Managed callable invoked its old cached scalar mapper"
        return call(function, *args, **kwargs)
    monkeypatch.setattr(function_type, "__call__", no_cached_pack)
    weights = tf.constant([0.7, -0.2], tf.float64)
    direction = tf.constant([0.4, -0.3], tf.float64)
    ledger = UnifiedResourceLedger()
    for case in (*POINTS, POINTS[0]):
        point = tf.constant(case["point"], tf.float64)
        def loss():
            y = tf.stack(handle(point))
            return tf.reduce_sum(weights*((y-0.3)**2 if loss_kind == "square" else tf.exp(y)+0.2*y**3))
        with ResourceScope(ledger):
            if mode == "for":
                with tf.autodiff.ForwardAccumulator(point, direction) as forward:
                    with tf.GradientTape() as reverse:
                        reverse.watch(point)
                        value = loss()
                    gradient = reverse.gradient(value, point)
                actual = forward.jvp(gradient)
            elif mode == "rof":
                with tf.GradientTape() as reverse:
                    reverse.watch(point)
                    with tf.autodiff.ForwardAccumulator(point, direction) as forward:
                        value = loss()
                    tangent = forward.jvp(value)
                actual = reverse.gradient(tangent, point)
            else:
                with tf.GradientTape() as outer:
                    outer.watch(point)
                    with tf.GradientTape() as inner:
                        inner.watch(point)
                        value = loss()
                    gradient = inner.gradient(value, point)
                    tangent = tf.reduce_sum(gradient*direction)
                actual = outer.gradient(tangent, point)
        y, j, h = (np.array(case[key]) for key in ("outputs", "jacobian", "hessians"))
        first, second = (2*(y-0.3), np.full(2, 2.)) if loss_kind == "square" else (np.exp(y)+0.6*y*y, np.exp(y)+1.2*y)
        curvature = np.einsum("o,oij,j->i", np.array([0.7, -0.2])*first, h, [0.4, -0.3])
        expected = j.T @ (np.array([0.7, -0.2])*second*(j @ [0.4, -0.3]))+curvature
        assert actual is not None and np.linalg.norm(curvature) > 1e-4
        np.testing.assert_allclose(actual, expected, atol=2e-9, rtol=0)
    assert ledger.receipt()["consumed_derivative_work"] > 0
    assert ledger.receipt()["live_memory_bytes"] == 0


def test_same_managed_snapshot_keeps_complete_complex_primal(monkeypatch):
    node, _ = make_node()
    handle = compile_node(node)
    forbid_rebuild(monkeypatch)
    for case in POINTS:
        point = tf.constant(case["point"], tf.float64)
        packed = tf.stack(handle._frozen_binding.evaluate(tuple(tf.unstack(point))))
        actual = handle._whole.state(packed)
        raw = np.array(case["state"])[:, 0]
        np.testing.assert_allclose(actual, raw[:, 0]+1j*raw[:, 1], atol=3e-12, rtol=0)


@pytest.mark.parametrize("name", ["requested_reverse", "full_entangling", "open_control", "closed_control"])
def test_managed_frozen_native_plan_covers_real_two_and_four_qubit_lineage(name, monkeypatch):
    from quantumbridge.diff import HigherOrderLimits
    from quantumbridge.execution.resource_limits import UnifiedExecutionLimits
    from test_native_tf_whole_qnode_execution import CASES, node_for, source_and_observables
    case = next(case for case in CASES if case["name"] == name)
    source, observables = source_and_observables(case)
    node = node_for(source, observables)
    node.higher_order_limits = HigherOrderLimits(max_adjoint_operations=1_000_000_000)
    node.unified_limits = UnifiedExecutionLimits(max_derivative_work=1_000_000_000)
    handle = compile_node(node)
    assert isinstance(handle._frozen_binding, FrozenParameterBinding)
    forbid_rebuild(monkeypatch)
    point, direction = tf.constant(case["point"], tf.float64), tf.constant([.4, -.3], tf.float64)
    state = handle._whole.state(tf.stack(handle._frozen_binding.evaluate(tuple(tf.unstack(point)))))
    raw = np.array(case["state"])[:, 0]
    np.testing.assert_allclose(state, raw[:, 0]+1j*raw[:, 1], atol=3e-12, rtol=0)
    for loss_kind in ("square", "exponential_cubic"):
        with tf.GradientTape() as reverse:
            reverse.watch(point)
            with tf.autodiff.ForwardAccumulator(point, direction) as forward:
                y = tf.stack(handle(point))
                loss = tf.reduce_sum(tf.constant([.7, -.2], tf.float64)*((y-.3)**2 if loss_kind == "square" else tf.exp(y)+.2*y**3))
            tangent = forward.jvp(loss)
        actual = reverse.gradient(tangent, point)
        y, j, h = (np.array(case[key]) for key in ("outputs", "jacobian", "hessians"))
        first, second = (2*(y-.3), np.full(2, 2.)) if loss_kind == "square" else (np.exp(y)+.6*y*y, np.exp(y)+1.2*y)
        expected = j.T @ (np.array([.7, -.2])*second*(j @ [.4, -.3]))+np.einsum("o,oij,j->i", np.array([.7, -.2])*first, h, [.4, -.3])
        np.testing.assert_allclose(actual, expected, atol=2e-9, rtol=0)
