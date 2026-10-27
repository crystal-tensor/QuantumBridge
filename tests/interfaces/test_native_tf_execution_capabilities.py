# Copyright 2026 QuantumBridge Contributors. Apache-2.0.
"""Verified contracts are not the same as a configured experimental envelope."""

from copy import copy

import numpy as np
import pytest

from quantumbridge.core.classical import UnsupportedFeature
from quantumbridge.execution.derivative_request import DerivativeExecutionRequest
from quantumbridge.execution.resource_context import ResourceScope
from quantumbridge.execution.resource_ledger import UnifiedResourceLedger
from test_native_tf_managed_cached_execution import CASE, compile_node, make_node, tf


@pytest.fixture(scope="module")
def handles():
    node, source = make_node()
    return node, compile_node(node), node.compile_tensorflow_inline(
        parameters=tuple(source.parameters), input_signature=[tf.TensorSpec((2,), tf.float64)])


def request(node, kind="hvp", order=2, method="best"):
    return DerivativeExecutionRequest(node, tf.constant(CASE["point"], tf.float64),
        derivative_kind=kind, derivative_order=order, method=method,
        tangent=tf.constant([0.4, -0.3], tf.float64) if kind in {"hvp", "jvp"} else None)


def test_mode_descriptions_are_deeply_readonly_and_do_not_claim_cached_second_order(handles):
    _, managed, inline = handles
    query = managed.execution_capabilities["MANAGED_EXPLICIT_QUERY"]
    diagnostic = managed.execution_capabilities["EXPERIMENTAL_CACHED_CALLABLE"]
    emitted = inline.execution_capabilities["TRACE_INLINE_DIFFERENTIABLE"]
    assert query["maximum_verified_quantum_derivative_order"] == emitted["maximum_verified_quantum_derivative_order"] == 2
    assert diagnostic["maximum_verified_quantum_derivative_order"] == 1
    assert diagnostic["eligible_for_verified_second_order"] is False
    assert diagnostic["external_mixed_ad_contract"] == "UNGUARANTEED_EXTERNAL_AD"
    assert query["resource_accounting_scope"] == "CONTROLLED_SYNCHRONOUS_ENTRY"
    assert emitted["resource_accounting_scope"] == "STATIC_BOUND_AND_RUNTIME_ASSERTIONS_ONLY"
    for handle in (managed, inline):
        with pytest.raises(TypeError):
            handle.execution_capabilities["invented"] = {}
    with pytest.raises(TypeError):
        diagnostic["maximum_verified_quantum_derivative_order"] = 2


@pytest.mark.parametrize("mode", ["EXPERIMENTAL_CACHED_CALLABLE", "MANAGED_EXPLICIT_QUERY"])
def test_explicit_unsupported_external_ad_contract_refuses_before_tensor_execution(handles, mode, monkeypatch):
    node, managed, _ = handles
    before = managed.cache_info()
    monkeypatch.setattr(managed, "_invoke", lambda *a, **k: pytest.fail("Unsupported contract executed quantum tensors"))
    ledger = UnifiedResourceLedger()
    with ResourceScope(ledger), pytest.raises(UnsupportedFeature):
        managed.require_derivative_contract(request(node), execution_mode=mode, external_ad="eager")
    assert managed.cache_info() == before
    assert ledger.receipt()["consumed_derivative_work"] == 0


def test_shared_explicit_query_contract_retains_its_verified_second_order(handles):
    node, managed, _ = handles
    query = request(node)
    assert managed.supports_derivatives(query)
    contract = managed.require_derivative_contract(query)
    assert contract["native_selected_method"] == "adjoint"
    np.testing.assert_allclose(managed.execute(query).derivative,
        np.array(CASE["hessians"]) @ [0.4, -0.3], atol=2e-9, rtol=0)


@pytest.mark.parametrize("context", ["eager", "co_traced"])
def test_inline_verified_contexts_remain_supported(handles, context):
    node, _, inline = handles
    assert inline.supports_derivatives(request(node), external_ad=context)
    contract = inline.require_derivative_contract(request(node), external_ad=context)
    assert contract["execution_mode"] == "TRACE_INLINE_DIFFERENTIABLE"


def test_direct_outer_cached_graph_derivatives_are_not_promised(handles):
    node, managed, inline = handles
    for handle in (managed, inline):
        with pytest.raises(UnsupportedFeature, match="EXTERNAL|external|cached"):
            handle.require_derivative_contract(request(node), external_ad="cached_outer_graph")
        assert not handle.supports_derivatives(request(node), external_ad="cached_outer_graph")


@pytest.mark.parametrize("method", ["parameter-shift", "backprop", "finite-diff"])
def test_optional_tensor_handles_do_not_expand_native_method_support(handles, method):
    node, managed, inline = handles
    query = request(node, method=method)
    assert not managed.supports_derivatives(query)
    assert not inline.supports_derivatives(query, external_ad="eager")


def test_first_order_explicit_callable_and_its_approved_envelope_are_real(handles):
    _, managed, _ = handles
    point = tf.constant(CASE["point"], tf.float64)
    with tf.GradientTape() as reverse:
        reverse.watch(point)
        value = tf.reduce_sum(tf.stack(managed.differentiable_call(point, derivative_order=1)))
    np.testing.assert_allclose(reverse.gradient(value, point), np.sum(CASE["jacobian"], axis=0), atol=5e-10, rtol=0)
    assert managed.last_metadata["execution_mode"] == "EXPERIMENTAL_CACHED_CALLABLE"
    assert managed.last_metadata["execution_capability"]["maximum_verified_quantum_derivative_order"] == 1


def test_explicit_second_order_callable_is_a_typed_early_refusal(handles, monkeypatch):
    _, managed, _ = handles
    monkeypatch.setattr(managed, "_invoke", lambda *a, **k: pytest.fail("Second-order contract executed"))
    with pytest.raises(UnsupportedFeature, match="verified|cached"):
        managed.differentiable_call(tf.constant(CASE["point"], tf.float64), derivative_order=2)


def test_declared_first_order_callable_supports_real_forward_jvp_and_weighted_vjp(handles):
    _, managed, _ = handles
    point = tf.constant(CASE["point"], tf.float64)
    with tf.GradientTape() as reverse:
        reverse.watch(point)
        with tf.autodiff.ForwardAccumulator(point, tf.constant([0.4, -0.3], tf.float64)) as forward:
            values = tf.stack(managed.differentiable_call(point, derivative_order=1))
    np.testing.assert_allclose(forward.jvp(values), np.array(CASE["jacobian"]) @ [0.4, -0.3], atol=5e-10, rtol=0)
    actual = reverse.gradient(values, point, output_gradients=tf.constant([0.7, -0.2], tf.float64))
    np.testing.assert_allclose(actual, np.array(CASE["jacobian"]).T @ [0.7, -0.2], atol=5e-10, rtol=0)


@pytest.mark.parametrize("traced", [False, True])
def test_inline_order_one_allows_genuine_first_jvp_without_upgrading_quantum_order(traced):
    node, source = make_node()
    handle = node.compile_tensorflow_inline(parameters=tuple(source.parameters),
        input_signature=[tf.TensorSpec((2,), tf.float64)], max_derivative_order=1)
    def evaluate(point):
        with tf.autodiff.ForwardAccumulator(point, tf.constant([0.4, -0.3], tf.float64)) as forward:
            values = tf.stack(handle(point))
        return forward.jvp(values)
    function = tf.function(evaluate, input_signature=[tf.TensorSpec((2,), tf.float64)], autograph=False, jit_compile=False) if traced else evaluate
    actual = function(tf.constant(CASE["point"], tf.float64))
    np.testing.assert_allclose(actual, np.array(CASE["jacobian"]) @ [0.4, -0.3], atol=5e-10, rtol=0)
    assert node.max_diff == 2


def test_copy_and_mutable_metadata_cannot_upgrade_capabilities(handles):
    _, managed, inline = handles
    for handle in (managed, inline):
        alias = copy(handle)
        assert alias.execution_capabilities is handle.execution_capabilities
    info = managed.execute(request(handles[0], "value", 0)).metadata
    info["execution_capability"]["maximum_verified_quantum_derivative_order"] = 0
    assert managed.execution_capabilities["MANAGED_EXPLICIT_QUERY"]["maximum_verified_quantum_derivative_order"] == 2


@pytest.mark.parametrize("maximum", [0, 1])
def test_capabilities_follow_the_approved_order_not_the_original_node_max_diff(maximum):
    node, source = make_node()
    managed = compile_node(node, max_derivative_order=maximum)
    inline = node.compile_tensorflow_inline(parameters=tuple(source.parameters),
        input_signature=[tf.TensorSpec((2,), tf.float64)], max_derivative_order=maximum)
    assert managed.execution_capabilities["MANAGED_EXPLICIT_QUERY"]["maximum_verified_quantum_derivative_order"] == maximum
    assert inline.execution_capabilities["TRACE_INLINE_DIFFERENTIABLE"]["maximum_verified_quantum_derivative_order"] == maximum
    assert not managed.supports_derivatives(request(node))
    assert not inline.supports_derivatives(request(node), external_ad="co_traced")


@pytest.mark.parametrize("field,value", [("shots", 32), ("seed", 5), ("observable", "Z"), ("limits", {})])
def test_inline_contract_does_not_silently_ignore_request_overrides(handles, field, value, monkeypatch):
    from dataclasses import replace
    node, _, inline = handles
    query = replace(request(node), **{field: value})
    monkeypatch.setattr(inline, "_input", lambda *a, **k: pytest.fail("Unsupported override emitted tensors"))
    with pytest.raises(UnsupportedFeature, match="override"):
        inline.require_derivative_contract(query, external_ad="eager")
    assert not inline.supports_derivatives(query, external_ad="eager")


@pytest.mark.parametrize("boundary", ["checked_cached", "inline"])
@pytest.mark.parametrize("mode", ["for", "tape"])
def test_actual_order_one_owner_refuses_recognizable_second_quantum_point(boundary, mode):
    node, source = make_node()
    node.max_diff = 1
    handle = compile_node(node) if boundary == "checked_cached" else node.compile_tensorflow_inline(
        parameters=tuple(source.parameters), input_signature=[tf.TensorSpec((2,), tf.float64)], max_derivative_order=1)
    point = tf.constant(CASE["point"], tf.float64)
    direction = tf.constant([0.4, -0.3], tf.float64)
    def loss():
        value = handle.differentiable_call(point, derivative_order=1) if boundary == "checked_cached" else handle(point)
        return tf.reduce_sum(tf.stack(value))
    with pytest.raises(UnsupportedFeature, match="second|order two"):
        if mode == "for":
            with tf.autodiff.ForwardAccumulator(point, direction) as forward:
                with tf.GradientTape() as reverse:
                    reverse.watch(point)
                    value = loss()
                gradient = reverse.gradient(value, point)
            forward.jvp(gradient)
        else:
            with tf.GradientTape() as outer:
                outer.watch(point)
                with tf.GradientTape() as inner:
                    inner.watch(point)
                    value = loss()
                projected = tf.reduce_sum(inner.gradient(value, point)*direction)
            outer.gradient(projected, point)
