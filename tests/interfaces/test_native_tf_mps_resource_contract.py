# Copyright 2026 QuantumBridge Contributors. Apache-2.0.
"""MPS uses the existing managed request, scope, cache and identity contracts."""

from concurrent.futures import ThreadPoolExecutor
from threading import Event

import numpy as np
import pytest

import quantumbridge as qb
from quantumbridge.core.classical import UnsupportedFeature
from quantumbridge.diff import HigherOrderLimits
from quantumbridge.execution.derivative_request import DerivativeExecutionRequest
from quantumbridge.execution.resource_context import ResourceScope
from quantumbridge.execution.resource_ledger import UnifiedResourceLedger
from quantumbridge.execution.resource_limits import UnifiedExecutionLimits
from quantumbridge.interfaces.tensorflow_mps_execution import TensorFlowMPSPlan
from test_native_tf_mps_tensor_chain import build, no_dense_or_host, POINT, DIRECTION, WEIGHTS, tf


def compile_mps(**options):
    source, node = build(4, interface="tensorflow", **options)
    return source, node, node.compile_tensorflow(input_signature=[tf.TensorSpec((2,), tf.float64)])


def request(node, kind="value", **kwargs):
    return DerivativeExecutionRequest(node, tf.constant(POINT), derivative_kind=kind,
        derivative_order=0 if kind == "value" else 2 if kind in {"hvp", "hessian"} else 1, **kwargs)


def test_managed_mps_queries_same_parent_cache_tiny_hessian_cap(monkeypatch):
    constructor = UnifiedResourceLedger()
    with ResourceScope(constructor):
        _, node, handle = compile_mps(higher_order_limits=HigherOrderLimits(max_hessian_elements=1))
    # Fixed native matrix roots belong to the retained mathematical snapshot.
    # They are not temporary graph-construction reservations or TF allocator RAM.
    assert constructor.receipt()["live_memory_bytes"] == sum(m.nbytes for m in handle._whole._fixed.values())
    assert constructor.receipt()["reserved_derivative_work"] == 0
    assert constructor.receipt()["consumed_derivative_work"] > 0
    _, dense = build(4, device=qb.StatevectorDevice())
    y, j, h = np.array(dense(POINT)), np.array(dense.jacobian(POINT)), np.array(dense.hessian(POINT))
    no_dense_or_host(monkeypatch)
    parent = UnifiedResourceLedger()
    child = UnifiedResourceLedger(parent=parent)
    for direction in (DIRECTION, -DIRECTION, np.zeros(2)):
        query = request(node, "hvp", tangent=tf.constant(direction), cotangent=tf.constant(WEIGHTS))
        with ResourceScope(child):
            bound = handle.estimate(query)
            before = child.receipt()["consumed_derivative_work"]
            actual = handle.execute(query)
        assert child.receipt()["consumed_derivative_work"]-before == bound["first_call_work"]
        np.testing.assert_allclose(actual.value, y, atol=2e-12, rtol=0)
        np.testing.assert_allclose(actual.derivative, np.einsum("i,ijk,k->j", WEIGHTS, h, direction), atol=2e-9, rtol=0)
    with ResourceScope(child), pytest.raises(MemoryError, match="max_hessian_elements"):
        handle.execute(request(node, "hessian"))
    with ResourceScope(child):
        actual = handle.execute(request(node, "vjp", cotangent=tf.constant(WEIGHTS)))
    np.testing.assert_allclose(actual.derivative, j.T @ WEIGHTS, atol=2e-10, rtol=0)
    assert parent.receipt()["consumed_derivative_work"] == child.receipt()["consumed_derivative_work"]
    assert child.receipt()["live_memory_bytes"] == child.receipt()["reserved_derivative_work"] == 0
    assert actual.metadata["direct_concrete_function"] == "OUT_OF_SCOPE"
    assert actual.metadata["allocator_memory"] == "ESTIMATED_ONLY"


@pytest.mark.parametrize("field,value,match", [
    ("max_memory_bytes", 1, "max_memory_bytes"),
    ("max_adjoint_operations", 1, "max_adjoint_operations"),
    ("max_mps_tangent_components", 3, "max_mps_tangent_components"),
])
def test_mps_admission_refuses_before_tensor_allocation(field, value, match, monkeypatch):
    _, node = build(4, interface="tensorflow", higher_order_limits=HigherOrderLimits(**{field: value}))
    monkeypatch.setattr(TensorFlowMPSPlan, "chain", lambda *a: pytest.fail("Rejected MPS allocated its chain"))
    with pytest.raises(MemoryError, match=match):
        node(tf.constant(POINT))


def test_exact_bond_refusal_cannot_truncate_or_fall_back(monkeypatch):
    _, node = build(4, interface="tensorflow", device=qb.MatrixProductStateDevice(max_bond_dim=1, cutoff=0))
    no_dense_or_host(monkeypatch)
    monkeypatch.setattr(TensorFlowMPSPlan, "chain", lambda *a: pytest.fail("Over-bond plan allocated its chain"))
    with pytest.raises(MemoryError, match="bond"):
        node(tf.constant(POINT))


def test_mps_owner_source_and_device_option_identity(monkeypatch):
    source, node, handle = compile_mps()
    original = np.array(handle.execute(request(node)).value)
    source.x(1)
    np.testing.assert_allclose(handle.execute(request(node)).value, original, atol=2e-12, rtol=0)
    with monkeypatch.context() as patch:
        patch.setitem(node.device.state_options, "max_bond_dim", 2)
        with pytest.raises(UnsupportedFeature, match="owner"):
            handle.execute(request(node))
    with monkeypatch.context() as patch:
        patch.setitem(handle._plan.node.device.state_options, "max_bond_dim", 8)
        with pytest.raises(UnsupportedFeature, match="identity"):
            handle.execute(request(node))
    handle.close()
    with pytest.raises(UnsupportedFeature, match="closed"):
        handle.execute(request(node))


def test_mps_graph_build_failure_releases_parent_and_recovers(monkeypatch):
    _, node, handle = compile_mps()
    query = request(node, "jvp", tangent=tf.constant(DIRECTION))
    ledger = UnifiedResourceLedger()
    with monkeypatch.context() as patch:
        def fail(*args):
            raise RuntimeError("injected MPS graph construction")
        patch.setattr(handle, "_build", fail)
        with ResourceScope(ledger), pytest.raises(RuntimeError, match="injected"):
            handle.execute(query)
    assert ledger.receipt()["live_memory_bytes"] == ledger.receipt()["reserved_derivative_work"] == 0
    assert ledger.receipt()["consumed_tapes"] == 0
    with ResourceScope(ledger):
        value = handle.execute(query)
    assert np.isfinite(value.derivative).all()
    assert ledger.receipt()["live_memory_bytes"] == 0


def test_concurrent_mps_entries_compete_in_the_shared_ledger(monkeypatch):
    _, node, handle = compile_mps()
    query = request(node)
    bound = handle.estimate(query)
    ledger = UnifiedResourceLedger(UnifiedExecutionLimits(max_total_memory_bytes=bound["required_memory_bytes"]*3//2))
    entered, release = Event(), Event()
    execute = handle._run_graph
    def held(function, packet):
        entered.set()
        assert release.wait(30)
        return execute(function, packet)
    monkeypatch.setattr(handle, "_run_graph", held)
    def invoke():
        with ResourceScope(ledger):
            return handle.execute(query)
    with ThreadPoolExecutor(max_workers=2) as workers:
        first = workers.submit(invoke)
        try:
            assert entered.wait(30)
            with pytest.raises(MemoryError):
                workers.submit(invoke).result(timeout=20)
        finally:
            release.set()
        assert np.isfinite(first.result(timeout=30).value).all()
    assert ledger.receipt()["live_memory_bytes"] == ledger.receipt()["reserved_derivative_work"] == 0
    assert ledger.receipt()["consumed_tapes"] == 1


@pytest.mark.parametrize("point", [[np.nan, -0.41], [np.inf, -0.41], [2*np.pi, 0.]])
def test_mps_runtime_domain_refusal_releases_scope_and_cache_recovers(point):
    _, node, handle = compile_mps()
    ledger = UnifiedResourceLedger()
    invalid = DerivativeExecutionRequest(node, tf.constant(point, tf.float64),
        derivative_kind="value", derivative_order=0)
    with ResourceScope(ledger), pytest.raises(tf.errors.OpError):
        handle.execute(invalid)
    receipt = ledger.receipt()
    assert receipt["live_memory_bytes"] == receipt["reserved_derivative_work"] == 0
    assert receipt["consumed_tapes"] == 0
    with ResourceScope(ledger):
        result = handle.execute(request(node))
    assert np.isfinite(result.value).all()
    assert ledger.receipt()["consumed_tapes"] == 1


def test_mps_full_second_order_and_first_only_boundaries_remain_real():
    from quantumbridge.qml import QNode
    _, dense = build(4, device=qb.StatevectorDevice())
    _, node = build(4, interface="tensorflow")
    point = tf.constant(POINT)
    node.max_diff = 1
    with tf.GradientTape() as tape:
        tape.watch(point)
        value = tf.stack(node(point))
    gradient = tape.gradient(value, point, output_gradients=tf.constant(WEIGHTS))
    np.testing.assert_allclose(gradient, np.array(dense.jacobian(POINT)).T @ WEIGHTS, atol=2e-10, rtol=0)
    with pytest.raises(UnsupportedFeature, match="second"):
        with tf.GradientTape() as outer:
            outer.watch(point)
            with tf.GradientTape() as inner:
                inner.watch(point)
                value = tf.reduce_sum(tf.stack(node(point)))
            first = inner.gradient(value, point)
            first_sum = tf.reduce_sum(first)
        outer.gradient(first_sum, point)
    node.max_diff = 2
    with pytest.raises(UnsupportedFeature, match="third"):
        with tf.GradientTape() as third:
            third.watch(point)
            with tf.GradientTape() as second:
                second.watch(point)
                with tf.GradientTape() as first:
                    first.watch(point)
                    value = tf.reduce_sum(tf.stack(node(point)))
                g = first.gradient(value, point)
                g_sum = tf.reduce_sum(g)
            h = second.gradient(g_sum, point)
            h_sum = tf.reduce_sum(h)
        third.gradient(h_sum, point)
    assert isinstance(node, QNode)


def test_mps_multidirection_multicotangent_streams_without_full_hessian(monkeypatch):
    _, node, handle = compile_mps(higher_order_limits=HigherOrderLimits(max_hessian_elements=1))
    _, dense = build(4, device=qb.StatevectorDevice())
    hessian = np.array(dense.hessian(POINT))
    no_dense_or_host(monkeypatch)
    monkeypatch.setattr(tf.GradientTape, "jacobian", lambda *a, **k: pytest.fail("Streamed MPS HVP materialized a Hessian"))
    vectors = np.array([DIRECTION, -DIRECTION, np.zeros(2)])
    weights = np.array([WEIGHTS, -WEIGHTS])
    actual = handle.execute(request(node, "hvp", tangent=tf.constant(vectors), cotangent=tf.constant(weights)))
    np.testing.assert_allclose(actual.derivative, np.einsum("ci,ijk,dk->cdj", weights, hessian, vectors), atol=2e-9, rtol=0)
    assert actual.metadata["tensor_plan_work"]["logical_evaluations"] == 6
