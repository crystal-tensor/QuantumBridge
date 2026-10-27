# Copyright 2026 QuantumBridge Contributors. Apache-2.0.
"""Actual concurrent controlled invocations compete in one native account."""

from concurrent.futures import ThreadPoolExecutor
from threading import Event

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
    node, _ = make_node()
    return node, compile_node(node)


@pytest.mark.parametrize("threads", [2, 3, 4])
@pytest.mark.parametrize("field", ["max_total_memory_bytes", "max_derivative_work", "max_total_tapes"])
def test_concurrent_native_requests_cannot_sell_the_same_remaining_budget(compiled, threads, field, monkeypatch):
    node, managed = compiled
    point = tf.constant(CASE["point"], tf.float64)
    request = DerivativeExecutionRequest(node, point, derivative_kind="value", derivative_order=0)
    work = managed.estimate(request)
    limit = work["required_memory_bytes"]*3//2 if field == "max_total_memory_bytes" else work["first_call_work"]*3//2 if field == "max_derivative_work" else 1
    ledger = UnifiedResourceLedger(UnifiedExecutionLimits(**{field: limit}))
    entered, release = Event(), Event()
    evaluate = managed._run_graph
    def held(function, packet):
        entered.set()
        assert release.wait(30), "Release the admitted real graph invocation"
        return evaluate(function, packet)
    monkeypatch.setattr(managed, "_run_graph", held)
    def invoke():
        with ResourceScope(ledger):
            return managed.execute(request)
    def refused():
        with pytest.raises(MemoryError):
            invoke()
    with ThreadPoolExecutor(max_workers=threads) as workers:
        first = workers.submit(invoke)
        try:
            assert entered.wait(30)
            others = [workers.submit(refused) for _ in range(threads-1)]
            for other in others:
                other.result(timeout=20)
        finally:
            release.set()
        np.testing.assert_allclose(first.result(timeout=30).value, CASE["outputs"], atol=3e-12, rtol=0)
    receipt = ledger.receipt()
    assert receipt["live_memory_bytes"] == receipt["reserved_derivative_work"] == 0
    assert receipt["consumed_tapes"] == 1
    if field == "max_total_memory_bytes":
        assert receipt["peak_memory_bytes"] <= limit
    elif field == "max_derivative_work":
        assert receipt["consumed_derivative_work"] <= limit


def test_close_invalidates_new_calls_but_does_not_erase_an_admitted_execution(monkeypatch):
    node, _ = make_node()
    managed = compile_node(node)
    point = tf.constant(CASE["point"], tf.float64)
    entered, release = Event(), Event()
    evaluate = managed._run_graph
    ledger = UnifiedResourceLedger()
    def held(function, packet):
        entered.set()
        assert release.wait(30)
        return evaluate(function, packet)
    monkeypatch.setattr(managed, "_run_graph", held)
    def invoke():
        with ResourceScope(ledger):
            return managed(point)
    with ThreadPoolExecutor(max_workers=1) as workers:
        first = workers.submit(invoke)
        try:
            assert entered.wait(30)
            managed.close()
            with ResourceScope(ledger), pytest.raises(UnsupportedFeature, match="closed"):
                managed(point)
        finally:
            release.set()
        np.testing.assert_allclose(first.result(timeout=30), CASE["outputs"], atol=3e-12, rtol=0)
    assert ledger.receipt()["consumed_tapes"] == 1
    assert ledger.receipt()["live_memory_bytes"] == 0
