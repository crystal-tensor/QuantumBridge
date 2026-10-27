# Copyright 2026 QuantumBridge Contributors. Apache-2.0.
"""Explicit cached requests have separate, enforceable resource contracts."""

from dataclasses import replace

import numpy as np
import pytest

import quantumbridge as qb
from quantumbridge.core.classical import UnsupportedFeature
from quantumbridge.diff import HigherOrderLimits
from quantumbridge.execution.derivative_request import DerivativeExecutionRequest
from quantumbridge.execution.resource_context import ResourceScope
from quantumbridge.execution.resource_ledger import UnifiedResourceLedger
from quantumbridge.execution.resource_limits import UnifiedExecutionLimits
from quantumbridge.qml import QNode

from test_native_tf_managed_cached_execution import CASE, compile_node, make_node, tf


@pytest.fixture(scope="module")
def compiled():
    node, _ = make_node()
    return node, compile_node(node)


def request(node, kind):
    return DerivativeExecutionRequest(node, tf.constant(CASE["point"], tf.float64),
        derivative_kind=kind, derivative_order=0 if kind == "value" else 2 if kind in {"hessian", "hvp"} else 1,
        tangent=tf.constant([0.4, -0.3], tf.float64) if kind in {"hvp", "jvp"} else None,
        cotangent=tf.constant([0.7, -0.2], tf.float64) if kind in {"hvp", "vjp"} else None)


@pytest.mark.parametrize("kind", ["value", "jacobian", "jvp", "vjp", "hvp", "hessian"])
@pytest.mark.parametrize("difference", [-1, 0])
def test_each_request_has_its_own_exact_shared_work_cap(compiled, kind, difference, monkeypatch):
    node, handle = compiled
    query = request(node, kind)
    bound = handle.estimate(query)
    ledger = UnifiedResourceLedger(UnifiedExecutionLimits(max_derivative_work=bound["first_call_work"]+difference))
    if difference:
        monkeypatch.setattr(handle, "_run_graph", lambda *a: pytest.fail("A refused query executed a graph"))
    with ResourceScope(ledger):
        if difference:
            with pytest.raises(MemoryError):
                handle.execute(query)
        else:
            result = handle.execute(query)
            assert result.receipt["consumed_derivative_work"] == bound["first_call_work"]
            assert result.metadata["request"]["operation"] == kind
            assert result.metadata["tensor_plan_work"]["planning_mode"] == "explicit_derivative_request"
    receipt = ledger.receipt()
    assert receipt["consumed_tapes"] == (0 if difference else bound["logical_evaluations"])
    assert receipt["reserved_derivative_work"] == receipt["live_memory_bytes"] == 0


@pytest.mark.parametrize("kind", ["jvp", "vjp", "hvp"])
def test_batched_directions_and_cotangents_have_real_values_and_increased_work(compiled, kind):
    node, handle = compiled
    query = request(node, kind)
    single = handle.estimate(query)
    vectors = np.array([[0.4, -0.3], [-0.1, 0.8]])
    weights = np.array([[0.7, -0.2], [0.3, 0.9]])
    many = replace(query,
        tangent=tf.constant(vectors, tf.float64) if kind != "vjp" else None,
        cotangent=tf.constant(weights, tf.float64) if kind != "jvp" else None)
    bound = handle.estimate(many)
    multiplier = 4 if kind == "hvp" else 2
    assert bound["logical_evaluations"] == multiplier*single["logical_evaluations"]
    assert bound["planned_work"] == multiplier*single["planned_work"]
    result = handle.execute(many)
    jacobian, hessians = np.array(CASE["jacobian"]), np.array(CASE["hessians"])
    expected = vectors @ jacobian.T if kind == "jvp" else weights @ jacobian if kind == "vjp" else np.einsum("co,oij,dj->cdi", weights, hessians, vectors)
    np.testing.assert_allclose(result.derivative, expected, atol=2e-9, rtol=0)
    assert result.receipt["consumed_tapes"] == multiplier*single["logical_evaluations"]
    assert result.metadata["request"]["direction_count"] == (0 if kind == "vjp" else 2)
    assert result.metadata["request"]["cotangent_count"] == (0 if kind == "jvp" else 2)


def test_scalar_gradient_request_is_native_and_budgeted():
    p, q = qb.ParameterVector("point", 2)
    source = qb.Circuit(1).ry(p*p+q, 0)
    node = QNode.from_circuit(source, qb.PauliZ(0), interface="tensorflow", diff_method="adjoint", max_diff=2)
    handle = compile_node(node)
    point = np.array(CASE["point"])
    query = DerivativeExecutionRequest(node, tf.constant(point, tf.float64), derivative_kind="gradient", derivative_order=1)
    result = handle.execute(query)
    np.testing.assert_allclose(result.derivative, -np.sin(point[0]**2+point[1])*np.array([2*point[0], 1.]), atol=1e-12, rtol=0)
    assert result.metadata["request"]["order"] == 1
    assert result.receipt["consumed_tapes"] == 1


@pytest.mark.parametrize("approved", [0, 1, 2])
def test_callable_declares_its_conservative_envelope_without_fictitious_completed_tapes(approved):
    node, _ = make_node()
    handle = compile_node(node, max_derivative_order=approved)
    handle(tf.constant(CASE["point"], tf.float64))
    metadata = handle.last_metadata
    work = metadata["tensor_plan_work"]
    assert work["planning_mode"] == "approved_callable_order_envelope"
    assert work["envelope_order"] == approved
    assert metadata["receipt"]["consumed_tapes"] == 1
    assert metadata["external_loss"] == "OUT_OF_SCOPE"
    if approved < 2:
        with pytest.raises(UnsupportedFeature, match="approved"):
            handle.execute(request(node, "hvp"))


@pytest.mark.parametrize("approved", [0, 1])
def test_cached_callable_does_not_upgrade_its_approved_derivative_order(approved):
    node, _ = make_node()
    handle = compile_node(node, max_derivative_order=approved)
    point = tf.constant(CASE["point"], tf.float64)
    with pytest.raises(UnsupportedFeature, match="(approved|approval)"):
        with tf.GradientTape() as outer:
            outer.watch(point)
            with tf.GradientTape() as inner:
                inner.watch(point)
                value = tf.reduce_sum(tf.stack(handle(point)))
            gradient = inner.gradient(value, point)
            contracted = tf.reduce_sum(gradient)
        outer.gradient(contracted, point)


@pytest.mark.parametrize("bad", [tf.constant([0.37, 0.82], tf.float32), tf.constant([0.37], tf.float64), tf.constant([[0.37, 0.82]], tf.float64)])
def test_invalid_dtype_or_shape_is_rejected_before_cached_execution(compiled, bad, monkeypatch):
    _, handle = compiled
    monkeypatch.setattr(handle, "_run_graph", lambda *a: pytest.fail("Invalid signature executed a graph"))
    ledger = UnifiedResourceLedger()
    with ResourceScope(ledger), pytest.raises(ValueError, match="shape.*dtype"):
        handle(bad)
    assert ledger.receipt()["consumed_derivative_work"] == 0


@pytest.mark.parametrize("field", ["max_memory_bytes", "max_adjoint_operations", "max_total_tapes", "device_memory"])
def test_combined_second_rule_rechecks_limits_after_adding_its_projected_jvp(compiled, field):
    _, handle = compiled
    single = handle._work(handle._request("hvp"))
    node, _ = make_node()
    if field == "device_memory":
        node.device.max_memory_mb = single["workspace_bytes"]/1024**2
    else:
        key = {"max_memory_bytes": "workspace_bytes", "max_adjoint_operations": "planned_work", "max_total_tapes": "logical_evaluations"}[field]
        node.higher_order_limits = HigherOrderLimits(**{field: single[key]})
    with pytest.raises(MemoryError, match="(max_memory|max_adjoint|max_total_tapes)"):
        compile_node(node)


def test_cached_callable_refuses_a_genuine_third_point_derivative(compiled):
    _, handle = compiled
    point = tf.constant(CASE["point"], tf.float64)
    with pytest.raises(UnsupportedFeature, match="third"):
        with tf.GradientTape() as third:
            third.watch(point)
            with tf.GradientTape() as second:
                second.watch(point)
                with tf.GradientTape() as first:
                    first.watch(point)
                    value = tf.reduce_sum(tf.stack(handle(point)))
                gradient = first.gradient(value, point)
                projected = tf.reduce_sum(gradient)
            product = second.gradient(projected, point)
            contracted = tf.reduce_sum(product)
        third.gradient(contracted, point)


def test_asynchronous_mode_refuses_before_any_invocation_or_charge(compiled, monkeypatch):
    _, handle = compiled
    before = handle.cache_info()["attempted_calls"]
    monkeypatch.setattr(tf.config.experimental, "get_synchronous_execution", lambda: False)
    ledger = UnifiedResourceLedger()
    with ResourceScope(ledger), pytest.raises(UnsupportedFeature, match="synchronous"):
        handle(tf.constant(CASE["point"], tf.float64))
    assert handle.cache_info()["attempted_calls"] == before
    assert ledger.receipt()["consumed_derivative_work"] == 0
