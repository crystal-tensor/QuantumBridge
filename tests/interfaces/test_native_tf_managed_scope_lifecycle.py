# Copyright 2026 QuantumBridge Contributors. Apache-2.0.
"""Invocation ownership, exact caps, failure cleanup and frozen math."""

from copy import copy
from dataclasses import replace
import gc
import weakref

import numpy as np
import pytest

from quantumbridge.core.classical import UnsupportedFeature
from quantumbridge.execution.derivative_request import DerivativeExecutionRequest
from quantumbridge.execution.resource_context import ResourceScope
from quantumbridge.execution.resource_ledger import UnifiedResourceLedger
from quantumbridge.execution.resource_limits import UnifiedExecutionLimits

from test_native_tf_managed_cached_execution import CASE, compile_node, make_node, tf


@pytest.fixture(scope="module")
def compiled():
    node, source = make_node()
    return node, compile_node(node), source


def request(node, **options):
    return DerivativeExecutionRequest(node, tf.constant(CASE["point"], tf.float64),
        derivative_kind="value", derivative_order=0, **options)


@pytest.mark.parametrize("depth", [1, 2, 3])
def test_new_invocations_use_the_current_parent_and_nested_scope(compiled, depth):
    node, managed, _ = compiled
    parent = UnifiedResourceLedger()
    chain = [parent]
    for _ in range(depth-1):
        chain.append(UnifiedResourceLedger(parent=chain[-1]))
    with ResourceScope(chain[-1]):
        result = managed.execute(request(node))
    for ledger in chain:
        receipt = ledger.receipt()
        assert receipt["consumed_derivative_work"] == result.receipt["consumed_derivative_work"] > 0
        assert receipt["live_memory_bytes"] == 0
    assert result.receipt["consumed_tapes"] == 1


def test_handle_does_not_capture_an_exited_scope_for_future_calls():
    node, _ = make_node()
    first, second = UnifiedResourceLedger(), UnifiedResourceLedger()
    with ResourceScope(first):
        managed = compile_node(node)
        managed(tf.constant(CASE["point"], tf.float64))
    spent = first.receipt()["consumed_derivative_work"]
    with ResourceScope(second):
        managed(tf.constant(CASE["point"], tf.float64))
    assert first.receipt()["consumed_derivative_work"] == spent
    assert second.receipt()["consumed_derivative_work"] > 0
    assert first.receipt()["live_memory_bytes"] == second.receipt()["live_memory_bytes"] == 0


@pytest.mark.parametrize("field", ["max_total_memory_bytes", "max_derivative_work", "max_total_tapes"])
@pytest.mark.parametrize("difference", [0, -1])
def test_equal_or_one_below_actual_admission_boundary(compiled, field, difference, monkeypatch):
    node, managed, _ = compiled
    estimated = managed.estimate(request(node))
    key = {"max_total_memory_bytes": "required_memory_bytes", "max_derivative_work": "first_call_work", "max_total_tapes": "logical_evaluations"}[field]
    ledger = UnifiedResourceLedger(UnifiedExecutionLimits(**{field: estimated[key]+difference}))
    if difference:
        monkeypatch.setattr(managed, "_run_graph", lambda *a: pytest.fail("A refused request executed a cached graph"))
    with ResourceScope(ledger):
        if difference:
            with pytest.raises(MemoryError):
                managed.execute(request(node))
        else:
            result = managed.execute(request(node))
            np.testing.assert_allclose(result.value, CASE["outputs"], atol=3e-12, rtol=0)
    receipt = ledger.receipt()
    assert receipt["live_memory_bytes"] == receipt["reserved_derivative_work"] == 0
    assert receipt["consumed_tapes"] == (0 if difference else 1)


def test_multiple_calls_and_multiple_nodes_cannot_overspend_a_parent(compiled):
    node, managed, _ = compiled
    other_node, _ = make_node()
    other = compile_node(other_node)
    first = managed.estimate(request(node))["first_call_work"]
    second = other.estimate(request(other_node))["first_call_work"]
    ledger = UnifiedResourceLedger(UnifiedExecutionLimits(max_derivative_work=first+second-1))
    with ResourceScope(ledger):
        managed.execute(request(node))
        with pytest.raises(MemoryError):
            other.execute(request(other_node))
    assert ledger.receipt()["consumed_tapes"] == 1
    assert ledger.receipt()["live_memory_bytes"] == 0


@pytest.mark.parametrize("failure", [RuntimeError, KeyboardInterrupt])
def test_failed_or_cancelled_execution_is_not_committed_as_success(compiled, failure, monkeypatch):
    node, managed, _ = compiled
    ledger = UnifiedResourceLedger()
    before = managed.cache_info()
    with monkeypatch.context() as patch:
        def failed(*args):
            raise failure("injected after reservation")
        patch.setattr(managed, "_run_graph", failed)
        with ResourceScope(ledger), pytest.raises(failure):
            managed.execute(request(node))
    receipt = ledger.receipt()
    assert receipt["consumed_derivative_work"] > 0
    assert receipt["consumed_tapes"] == receipt["live_memory_bytes"] == receipt["reserved_derivative_work"] == 0
    after = managed.cache_info()
    assert after["successful_calls"] == before["successful_calls"]
    assert after["aborted_calls"] == before["aborted_calls"]+1
    with ResourceScope(ledger):
        result = managed.execute(request(node))
    np.testing.assert_allclose(result.value, CASE["outputs"], atol=3e-12, rtol=0)


def test_raw_concrete_function_is_not_a_managed_python_invocation(compiled):
    _, managed, _ = compiled
    ledger = UnifiedResourceLedger()
    before = managed.cache_info()
    with ResourceScope(ledger):
        raw = managed.concrete_function(tf.constant(CASE["point"], tf.float64))[0]
    np.testing.assert_allclose(raw, CASE["outputs"], atol=3e-12, rtol=0)
    assert ledger.receipt()["consumed_derivative_work"] == 0
    assert managed.cache_info()["attempted_calls"] == before["attempted_calls"]


def test_metadata_edits_and_copy_aliases_cannot_change_budget_numbers(compiled):
    node, managed, _ = compiled
    report = managed.estimate(request(node))
    cost = report["first_call_work"]
    report["planned_work"] = 0
    alias = copy(managed)
    ledger = UnifiedResourceLedger(UnifiedExecutionLimits(max_derivative_work=cost-1))
    with ResourceScope(ledger), pytest.raises(MemoryError):
        alias.execute(request(node))
    assert ledger.receipt()["consumed_tapes"] == 0


def test_owner_expiry_invalidates_the_contract_and_foreign_requests_are_rejected():
    node, _ = make_node()
    managed = compile_node(node)
    owner = weakref.ref(node)
    del node
    gc.collect()
    assert owner() is None
    with pytest.raises(UnsupportedFeature, match="owner"):
        managed.execute(request(managed))
    with pytest.raises(ValueError, match="another compiled owner"):
        managed.execute(replace(request(managed), circuit_or_tape=None))


@pytest.mark.parametrize("attribute,value", [("diff_method", "best"), ("max_diff", 1), ("unified_limits", UnifiedExecutionLimits(max_derivative_work=0))])
def test_owner_method_order_and_resource_changes_invalidate_the_old_contract(attribute, value):
    node, _ = make_node()
    managed = compile_node(node)
    setattr(node, attribute, value)
    with pytest.raises(UnsupportedFeature, match="owner"):
        managed(tf.constant(CASE["point"], tf.float64))


def test_closed_handle_refuses_new_invocations_without_consuming_a_scope():
    node, _ = make_node()
    managed = compile_node(node)
    managed.close()
    ledger = UnifiedResourceLedger()
    with ResourceScope(ledger), pytest.raises(UnsupportedFeature, match="closed"):
        managed.execute(request(node))
    assert ledger.receipt()["consumed_derivative_work"] == 0
    assert managed.cache_info()["closed"]


def test_owner_collection_cannot_erase_a_resource_tightening():
    node, _ = make_node()
    managed = compile_node(node)
    node.unified_limits = UnifiedExecutionLimits(max_derivative_work=0)
    del node
    gc.collect()
    with pytest.raises(UnsupportedFeature, match="owner"):
        managed(tf.constant(CASE["point"], tf.float64))
