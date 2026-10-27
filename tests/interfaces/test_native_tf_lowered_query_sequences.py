# Copyright 2026 QuantumBridge Contributors. Apache-2.0.
"""Constructor scalar work is separate from real controlled quantum requests."""

import numpy as np
import pytest

from quantumbridge.diff import HigherOrderLimits
from quantumbridge.execution.derivative_request import DerivativeExecutionRequest
from quantumbridge.execution.resource_context import ResourceScope
from quantumbridge.execution.resource_ledger import UnifiedResourceLedger
from test_native_tf_lowered_scalar_execution import fixture, reference
from test_native_tf_managed_cached_execution import tf
from test_native_tf_trace_inline_qnode import forbid_rebuild


@pytest.mark.parametrize("kind", ["direct_tf", "remapped_native", "mixed_native"])
@pytest.mark.parametrize("direction_only", [False, True])
def test_actual_lowered_query_chain_charges_constructor_and_runtime_separately(kind, direction_only, monkeypatch):
    constructor = UnifiedResourceLedger()
    limits = HigherOrderLimits(max_hessian_elements=1) if direction_only else HigherOrderLimits()
    with ResourceScope(constructor):
        node, handle, calls = fixture(kind, higher_order_limits=limits)
    receipt = constructor.receipt()
    assert receipt["consumed_derivative_work"] == handle._construction_receipt["consumed_derivative_work"]
    source_work = sum(e["derivative_work"] for e in receipt["events"]
        if e["action"] == "consume" and e["category"] in {"tensorflow_scalar_source_scan", "tensorflow_scalar_native_binding"})
    assert source_work == handle._scalar_lowering_work["construction_work"] > 0
    assert receipt["live_memory_bytes"] == receipt["reserved_derivative_work"] == 0
    forbid_rebuild(monkeypatch)
    point, d1, d2 = np.array([.37, .82]), np.array([.4, -.3]), np.array([-.1, .8])
    _, value, gradient, hessian = reference(kind, point)
    parent = UnifiedResourceLedger()
    child = UnifiedResourceLedger(parent=parent)
    steps = [("value", None), ("gradient", None), ("jvp", d1), ("vjp", None),
        ("hvp", d1), ("hvp", d2), ("hessian", None), ("value", None)]
    for operation, tangent in steps:
        request = DerivativeExecutionRequest(node, tf.constant(point, tf.float64), derivative_kind=operation,
            derivative_order=0 if operation == "value" else 2 if operation in {"hvp", "hessian"} else 1,
            tangent=None if tangent is None else tf.constant(tangent, tf.float64),
            cotangent=tf.constant([.7], tf.float64) if operation == "vjp" else None)
        before = child.receipt()
        if direction_only and operation == "hessian":
            with ResourceScope(child), pytest.raises(MemoryError, match="max_hessian_elements"):
                handle.execute(request)
            assert child.receipt()["consumed_derivative_work"] == before["consumed_derivative_work"]
            continue
        with ResourceScope(child):
            bound = handle.estimate(request)
            actual = handle.execute(request)
        after = child.receipt()
        assert after["consumed_derivative_work"]-before["consumed_derivative_work"] == bound["first_call_work"]
        assert actual.receipt["consumed_derivative_work"] == bound["first_call_work"]
        assert parent.receipt()["consumed_derivative_work"] == after["consumed_derivative_work"]
        assert after["live_memory_bytes"] == after["reserved_derivative_work"] == 0
        assert not any(e["category"].startswith("tensorflow_scalar_") for e in actual.receipt["events"])
        assert actual.metadata["physical_shots"] == actual.metadata["host_quantum_calls"] == actual.metadata["device_updates"] == 0
        np.testing.assert_allclose(actual.value, value, atol=2e-12, rtol=0)
        if operation != "value":
            expected = gradient if operation == "gradient" else gradient @ d1 if operation == "jvp" else .7*gradient if operation == "vjp" else hessian @ tangent if operation == "hvp" else hessian
            np.testing.assert_allclose(actual.derivative, expected, atol=2e-10, rtol=0)
    assert calls == ["construct"]
