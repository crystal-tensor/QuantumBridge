# Copyright 2026 QuantumBridge Contributors. Apache-2.0.
"""Actual lowered-source quantum math without rebuilding or cached inner calls."""

from contextlib import contextmanager

import numpy as np
import pytest

import quantumbridge as qb
from quantumbridge.execution.resource_context import ResourceScope
from quantumbridge.execution.resource_ledger import UnifiedResourceLedger
from quantumbridge.qml import QNode
from test_native_tf_managed_cached_execution import tf
from test_native_tf_trace_inline_qnode import forbid_rebuild


def fixture(kind, **options):
    p, q = qb.ParameterVector("source", 2)
    source = qb.Circuit(1).ry(p*p+q, 0)
    builder = QNode.from_circuit(source, qb.PauliZ(0)).fn
    calls = []
    def program(tape, point):
        calls.append("construct")
        if kind == "direct_tf":
            tape.ry(tf.sin(point[0])**2+point[1], 0)
            return tape.expval(qb.PauliZ(0))
        result = builder(tape, tf.reverse(point, [0]) if kind == "remapped_native" else point)
        if kind == "mixed_native":
            tape.rx(.2*point[0], 0)
        return result
    node = QNode(program, 1, interface="tensorflow", diff_method="adjoint", max_diff=2, **options)
    handle = node.compile_tensorflow(input_signature=[tf.TensorSpec((2,), tf.float64)])
    assert calls == ["construct"] and handle._scalar_lowering_work is not None
    return node, handle, calls


def reference(kind, point):
    p, q = point
    if kind == "direct_tf":
        a, da, ha = np.sin(p)**2+q, np.array([np.sin(2*p), 1.]), np.diag([2*np.cos(2*p), 0.])
    elif kind == "remapped_native":
        a, da, ha = q*q+p, np.array([1., 2*q]), np.diag([0., 2.])
    else:
        a, da, ha = p*p+q, np.array([2*p, 1.]), np.diag([2., 0.])
    y, j, h = np.cos(a), -np.sin(a)*da, -np.cos(a)*np.outer(da, da)-np.sin(a)*ha
    b = .2*p if kind == "mixed_native" else 0.
    if kind == "mixed_native":
        db = np.array([.2, 0.])
        j = j*np.cos(b)-y*np.sin(b)*db
        h = h*np.cos(b)-y*np.cos(b)*np.outer(db, db)+np.sin(a)*np.sin(b)*(np.outer(da, db)+np.outer(db, da))
        y *= np.cos(b)
    state = np.array([np.cos(b/2)*np.cos(a/2)-1j*np.sin(b/2)*np.sin(a/2),
        np.cos(b/2)*np.sin(a/2)-1j*np.sin(b/2)*np.cos(a/2)])
    return state, y, j, h


@pytest.mark.parametrize("kind", ["direct_tf", "remapped_native", "mixed_native"])
@pytest.mark.parametrize("mode", ["for", "rof", "tape"])
@pytest.mark.parametrize("loss_kind", ["square", "exponential_cubic"])
def test_lowered_mapping_uses_full_native_state_and_loss_curvature(kind, mode, loss_kind, monkeypatch):
    node, handle, calls = fixture(kind)
    forbid_rebuild(monkeypatch)
    complete = handle._run_graph
    def no_inner_quantum(function, packet):
        assert not hasattr(function, "get_concrete_function")
        return complete(function, packet)
    monkeypatch.setattr(handle, "_run_graph", no_inner_quantum)
    function_type, pack = type(handle._pack), handle._pack
    original = function_type.__call__
    def no_inner_scalar(function, *args, **kwargs):
        assert function is not pack
        return original(function, *args, **kwargs)
    monkeypatch.setattr(function_type, "__call__", no_inner_scalar)
    admitted, admission = [], handle._inline_admission
    @contextmanager
    def record_admission(*args):
        with admission(*args):
            yield
        admitted.append(handle.last_metadata["tensor_plan_work"])
    monkeypatch.setattr(handle, "_inline_admission", record_admission)
    direction = tf.constant([.4, -.3], tf.float64)
    parent = UnifiedResourceLedger()
    for raw in ([.37, .82], [.41, .91], [.37, .82]):
        point = tf.constant(raw, tf.float64)
        state, y, j, h = reference(kind, raw)
        packed = tf.stack(handle._frozen_binding.evaluate(tuple(tf.unstack(point))))
        np.testing.assert_allclose(handle._whole.state(packed), state, atol=2e-12, rtol=0)
        def loss():
            value = handle(point)
            return (value-.3)**2 if loss_kind == "square" else tf.exp(value)+.2*value**3
        before = parent.receipt()["consumed_derivative_work"]
        admitted.clear()
        with ResourceScope(parent):
            if mode == "for":
                with tf.autodiff.ForwardAccumulator(point, direction) as fw:
                    with tf.GradientTape() as reverse:
                        reverse.watch(point)
                        result = loss()
                    gradient = reverse.gradient(result, point)
                actual = fw.jvp(gradient)
            elif mode == "rof":
                with tf.GradientTape() as reverse:
                    reverse.watch(point)
                    with tf.autodiff.ForwardAccumulator(point, direction) as fw:
                        result = loss()
                    tangent = fw.jvp(result)
                actual = reverse.gradient(tangent, point)
            else:
                with tf.GradientTape() as outer:
                    outer.watch(point)
                    with tf.GradientTape() as inner:
                        inner.watch(point)
                        result = loss()
                    gradient = inner.gradient(result, point)
                    tangent = tf.reduce_sum(gradient*direction)
                actual = outer.gradient(tangent, point)
        first, second = (2*(y-.3), 2.) if loss_kind == "square" else (np.exp(y)+.6*y*y, np.exp(y)+1.2*y)
        np.testing.assert_allclose(actual, (second*np.outer(j, j)+first*h) @ [.4, -.3], atol=2e-9, rtol=0)
        metadata = handle.last_metadata
        spent = parent.receipt()["consumed_derivative_work"]-before
        assert admitted and spent == sum(w["planned_work"]+w["construction_work"] for w in admitted)
        assert spent == metadata["receipt"]["consumed_derivative_work"]
        assert parent.receipt()["live_memory_bytes"] == 0
    assert calls == ["construct"]
    assert node.max_diff == 2
