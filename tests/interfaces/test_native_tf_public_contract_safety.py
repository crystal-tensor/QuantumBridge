# Copyright 2026 QuantumBridge Contributors. Apache-2.0.
"""Public request shapes and actual executed-plan integrity, not labels alone."""

from dataclasses import replace

import pytest

import quantumbridge as qb
from quantumbridge.core.classical import UnsupportedFeature
from quantumbridge.execution.derivative_request import DerivativeExecutionRequest
from quantumbridge.execution.resource_context import ResourceScope
from quantumbridge.execution.resource_ledger import UnifiedResourceLedger
from test_native_tf_managed_cached_execution import CASE, compile_node, make_node, tf


@pytest.fixture(scope="module")
def compiled():
    node, _ = make_node()
    return node, compile_node(node)


def query(node, kind):
    return DerivativeExecutionRequest(node, tf.constant(CASE["point"], tf.float64),
        derivative_kind=kind, derivative_order=0 if kind == "value" else 2 if kind in {"hvp", "hessian"} else 1,
        tangent=tf.constant([0.4, -0.3], tf.float64) if kind in {"jvp", "hvp"} else None,
        cotangent=tf.constant([0.7, -0.2], tf.float64) if kind == "vjp" else None)


@pytest.mark.parametrize("kind,field", [("jvp", "tangent"), ("hvp", "tangent"), ("vjp", "cotangent")])
def test_missing_required_seed_is_an_early_contract_error(compiled, kind, field, monkeypatch):
    node, handle = compiled
    request = replace(query(node, kind), **{field: None})
    monkeypatch.setattr(handle, "_invoke", lambda *a, **k: pytest.fail("Invalid request executed a tensor graph"))
    ledger = UnifiedResourceLedger()
    with ResourceScope(ledger):
        assert not handle.supports_derivatives(request)
        for entry in (handle.require_derivative_contract, handle.estimate, handle.execute):
            with pytest.raises(ValueError, match=field):
                entry(request)
    assert ledger.receipt()["consumed_derivative_work"] == 0


@pytest.mark.parametrize("kind,field", [("value", "cotangent"), ("value", "tangent"),
    ("jacobian", "cotangent"), ("jacobian", "tangent"), ("hessian", "cotangent"),
    ("hessian", "tangent"), ("jvp", "cotangent"), ("vjp", "tangent")])
def test_irrelevant_seeds_are_not_silently_ignored(compiled, kind, field, monkeypatch):
    node, handle = compiled
    request = replace(query(node, kind), **{field: tf.constant([0.4, -0.3], tf.float64)})
    monkeypatch.setattr(handle, "_invoke", lambda *a, **k: pytest.fail("Ignored seed executed a tensor graph"))
    ledger = UnifiedResourceLedger()
    with ResourceScope(ledger):
        assert not handle.supports_derivatives(request)
        for entry in (handle.require_derivative_contract, handle.estimate, handle.execute):
            with pytest.raises(ValueError, match=field):
                entry(request)
    assert ledger.receipt()["consumed_derivative_work"] == 0


@pytest.mark.parametrize("kind,field", [("jvp", "tangent"), ("vjp", "cotangent"), ("hvp", "tangent")])
def test_empty_direction_batches_are_refused_consistently(compiled, kind, field, monkeypatch):
    node, handle = compiled
    request = replace(query(node, kind), **{field: tf.zeros((0, 2), tf.float64)})
    monkeypatch.setattr(handle, "_invoke", lambda *a, **k: pytest.fail("Empty direction batch executed"))
    assert not handle.supports_derivatives(request)
    for entry in (handle.require_derivative_contract, handle.estimate, handle.execute):
        with pytest.raises(ValueError, match="empty|positive|seed"):
            entry(request)


@pytest.mark.parametrize("part", ["whole_circuit", "local_body", "observable"])
def test_managed_fingerprint_covers_the_actual_executed_snapshot(part, monkeypatch):
    node, _ = make_node()
    handle = compile_node(node)
    if part == "whole_circuit":
        handle._whole._circuit.x(0)
    elif part == "local_body":
        next(iter(handle._whole._local.values()))._body.x(0)
    else:
        handle._whole._requests = (replace(handle._whole._requests[0], observable=qb.PauliX(1)),
            *handle._whole._requests[1:])
    monkeypatch.setattr(handle, "_invoke", lambda *a, **k: pytest.fail("An altered cached plan executed"))
    with pytest.raises(UnsupportedFeature, match="identity|snapshot|plan"):
        handle.execute(query(node, "value"))
