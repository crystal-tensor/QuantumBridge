# Copyright 2026 QuantumBridge Contributors. Apache-2.0.
"""Real snapshot QNode graphs invoked through the existing native ledger."""

from dataclasses import replace
import json
from pathlib import Path

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

tf = pytest.importorskip("tensorflow")
CASE = json.loads((Path(__file__).parents[1]/"information/data/tf_whole_qnode_oracles.json").read_text())["cases"][0]


def make_node(**options):
    p, q = qb.ParameterVector("angles", 2)
    source = qb.QuantumCircuit(2)
    source.append(qb.Circuit(1).ry(-p, 0).rz(q*q+0.4, 0).rx(p, 0).to_gate().power(0.5, annotated=True), (1,))
    builder = QNode.from_circuit(source, qb.PauliZ(1)).fn
    def program(tape, point):
        return builder(tape, point), tape.expval(qb.PauliX(1))
    node = QNode(program, 2, interface="tensorflow", max_diff=2, diff_method="adjoint", **options)
    return node, source


def compile_node(node, **options):
    return node.compile_tensorflow(input_signature=[tf.TensorSpec((2,), tf.float64)], **options)


def forbid_quantum_hosts(monkeypatch):
    from quantumbridge.interfaces.native_host import NativeHostKernel
    from quantumbridge.interfaces.tensorflow_graph import TensorFlowGraphKernel
    from quantumbridge.core.gates import Gate
    def forbidden(*a, **k):
        pytest.fail("A managed tensor graph used a host quantum or dense Gate fallback")
    for owner, name in [(NativeHostKernel, "run"), (NativeHostKernel, "run_second"),
            (TensorFlowGraphKernel, "evaluate"), (Gate, "to_matrix"),
            (qb.StatevectorDevice, "statevector"), (tf, "numpy_function"), (tf, "py_function")]:
        monkeypatch.setattr(owner, name, forbidden)


def test_repeated_managed_calls_reuse_a_real_graph_and_charge_the_active_ledger(monkeypatch):
    node, source = make_node()
    before = source.to_ir().to_json()
    forbid_quantum_hosts(monkeypatch)
    managed = compile_node(node)
    ledger = UnifiedResourceLedger()
    costs = []
    with ResourceScope(ledger):
        for _ in range(3):
            np.testing.assert_allclose(managed(tf.constant(CASE["point"], tf.float64)), CASE["outputs"], atol=3e-12, rtol=0)
            costs.append(ledger.receipt()["consumed_derivative_work"])
    assert 0 < costs[0] < costs[1] < costs[2]
    info = managed.cache_info()
    assert info["graphs_built"] == 3
    assert info["successful_calls"] == 3
    assert info["aborted_calls"] == 0
    assert ledger.receipt()["live_memory_bytes"] == 0
    assert source.to_ir().to_json() == before


@pytest.mark.parametrize("kind", ["value", "jacobian", "vjp", "jvp", "hvp", "hessian"])
def test_existing_derivative_requests_execute_cached_native_tensor_graphs(kind, monkeypatch):
    node, _ = make_node()
    forbid_quantum_hosts(monkeypatch)
    managed = compile_node(node)
    point = tf.constant(CASE["point"], tf.float64)
    direction = tf.constant([0.4, -0.3], tf.float64)
    cotangent = tf.constant([0.7, -0.2], tf.float64)
    request = DerivativeExecutionRequest(node, point, derivative_kind=kind,
        derivative_order=0 if kind == "value" else 2 if kind in {"hvp", "hessian"} else 1,
        tangent=direction if kind in {"hvp", "jvp"} else None,
        cotangent=cotangent if kind == "vjp" else None)
    result = managed.execute(request)
    j, h = np.array(CASE["jacobian"]), np.array(CASE["hessians"])
    expected = {"value": CASE["outputs"], "jacobian": j, "vjp": j.T @ [0.7, -0.2],
        "jvp": j @ [0.4, -0.3], "hvp": h @ [0.4, -0.3], "hessian": h}[kind]
    np.testing.assert_allclose(result.value, CASE["outputs"], atol=3e-12, rtol=0)
    if kind != "value":
        np.testing.assert_allclose(result.derivative, expected, atol=2e-9, rtol=0)
    assert result.code == 0
    assert result.receipt["consumed_derivative_work"] > 0
    assert result.receipt["live_memory_bytes"] == 0
    assert result.metadata["controlled_execution"] == "LEDGER_ACCOUNTED"


@pytest.mark.parametrize("mode", ["for", "rof", "tape"])
@pytest.mark.parametrize("loss_kind", ["square", "exponential_cubic"])
def test_external_nonlinear_loss_second_chain_rule_uses_managed_cached_calls(mode, loss_kind, monkeypatch):
    node, _ = make_node()
    forbid_quantum_hosts(monkeypatch)
    managed = compile_node(node)
    point = tf.constant(CASE["point"], tf.float64)
    d = tf.constant([0.4, -0.3], tf.float64)
    weights = np.array([0.7, -0.2])
    def loss():
        y = tf.stack(managed(point))
        return tf.reduce_sum(tf.constant(weights, tf.float64)*((y-0.3)**2 if loss_kind == "square" else tf.exp(y)+0.2*y**3))
    ledger = UnifiedResourceLedger()
    with ResourceScope(ledger):
        if mode == "for":
            with tf.autodiff.ForwardAccumulator(point, d) as forward:
                with tf.GradientTape() as reverse:
                    reverse.watch(point)
                    value = loss()
                gradient = reverse.gradient(value, point)
            actual = forward.jvp(gradient)
        elif mode == "rof":
            with tf.GradientTape() as reverse:
                reverse.watch(point)
                with tf.autodiff.ForwardAccumulator(point, d) as forward:
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
                contracted = tf.reduce_sum(gradient*d)
            actual = outer.gradient(contracted, point)
    y, j, h = np.array(CASE["outputs"]), np.array(CASE["jacobian"]), np.array(CASE["hessians"])
    first, second = (2*(y-0.3), np.full(2, 2.)) if loss_kind == "square" else (np.exp(y)+0.6*y*y, np.exp(y)+1.2*y)
    expected = j.T @ (weights*second*(j @ [0.4, -0.3]))+np.einsum("i,ijk,k->j", weights*first, h, [0.4, -0.3])
    assert actual is not None
    np.testing.assert_allclose(actual, expected, atol=2e-9, rtol=0)
    assert ledger.receipt()["consumed_tapes"] > 0


def test_cached_graph_assertions_recover_after_bad_inputs_without_retrace():
    import math
    node, _ = make_node()
    managed = compile_node(node)
    good = tf.constant(CASE["point"], tf.float64)
    ledger = UnifiedResourceLedger()
    with ResourceScope(ledger):
        first = tf.stack(managed(good))
        for bad in ([float("nan"), 0.82], [float("inf"), 0.82], [0., math.sqrt(2*math.pi-0.4)]):
            with pytest.raises(tf.errors.InvalidArgumentError):
                managed(tf.constant(bad, tf.float64))
        np.testing.assert_array_equal(tf.stack(managed(good)), first)
    info = managed.cache_info()
    assert info["graphs_built"] == 3
    assert info["successful_calls"] == 2
    assert info["aborted_calls"] == 3
    assert ledger.receipt()["live_memory_bytes"] == 0


def test_full_hessian_limit_is_not_imposed_on_a_streamed_hvp(monkeypatch):
    node, _ = make_node(higher_order_limits=HigherOrderLimits(max_hessian_elements=1))
    managed = compile_node(node)
    request = DerivativeExecutionRequest(node, tf.constant(CASE["point"], tf.float64), derivative_kind="hvp",
        derivative_order=2, tangent=tf.constant([0.4, -0.3], tf.float64))
    with pytest.raises(MemoryError, match="max_hessian_elements"):
        managed.execute(replace(request, derivative_kind="hessian", tangent=None))
    def forbidden(*a, **k):
        pytest.fail("A streamed HVP built a full Hessian/Jacobian")
    monkeypatch.setattr(tf.GradientTape, "jacobian", forbidden)
    monkeypatch.setattr(QNode, "compute_hessian", forbidden)
    result = managed.execute(request)
    np.testing.assert_allclose(result.derivative, np.array(CASE["hessians"]) @ [0.4, -0.3], atol=2e-9, rtol=0)


def test_source_mutation_is_a_snapshot_but_owner_budget_tightening_cannot_be_bypassed():
    node, source = make_node()
    managed = compile_node(node)
    point = tf.constant(CASE["point"], tf.float64)
    expected = tf.stack(managed(point))
    source.x(1)
    np.testing.assert_array_equal(tf.stack(managed(point)), expected)
    node.unified_limits = UnifiedExecutionLimits(max_derivative_work=0)
    with pytest.raises((UnsupportedFeature, MemoryError), match="(owner|budget|resource|limit)"):
        managed(point)


def test_managed_handle_cannot_be_silently_traced_into_an_unmanaged_outer_function():
    node, _ = make_node()
    managed = compile_node(node)
    with pytest.raises(UnsupportedFeature, match="(controlled|eager|graph)"):
        tf.function(managed, autograph=False)(tf.constant(CASE["point"], tf.float64))
