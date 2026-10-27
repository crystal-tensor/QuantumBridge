# Copyright 2026 QuantumBridge Contributors. Apache-2.0.
"""Snapshot identity and ledger boundaries independent of AD math checks."""

from dataclasses import replace

import numpy as np
import pytest

import quantumbridge as qb
from quantumbridge.core.classical import UnsupportedFeature
from quantumbridge.execution.derivative_request import DerivativeExecutionRequest
from quantumbridge.execution.resource_context import ResourceScope
from quantumbridge.execution.resource_ledger import UnifiedResourceLedger
from quantumbridge.qml import QNode
from test_native_tf_cached_rof_order_contracts import simple
from test_native_tf_managed_cached_execution import tf


@pytest.mark.parametrize("part", ["binding", "measurement_kind", "snapshot_method"])
def test_inline_managed_changed_snapshot_refuses_before_any_tensor_math(part, monkeypatch):
    node, handle = simple()
    if part == "binding":
        handle._frozen_binding = replace(handle._frozen_binding,
            expressions=tuple(expression+0.1 for expression in handle._frozen_binding.expressions))
    elif part == "measurement_kind":
        handle._whole._requests = (replace(handle._whole._requests[0], kind="var"),)
    else:
        handle._plan.node.diff_method = "best"
    monkeypatch.setattr(handle, "_program", lambda *a, **k: pytest.fail("Altered snapshot executed tensor math"))
    ledger = UnifiedResourceLedger()
    with ResourceScope(ledger), pytest.raises(UnsupportedFeature, match="identity|snapshot|plan"):
        handle(tf.constant([.37, .82], tf.float64))
    assert ledger.receipt()["consumed_derivative_work"] == 0


def test_inline_managed_parent_work_is_charged_once_per_synchronous_invocation():
    node, handle = simple()
    parent = UnifiedResourceLedger()
    for point in ([.37, .82], [.41, .91], [.37, .82]):
        before = parent.receipt()["consumed_derivative_work"]
        with ResourceScope(parent):
            actual = handle(tf.constant(point, tf.float64))
        np.testing.assert_allclose(actual, np.cos(point[0]**2+point[1]), atol=2e-12, rtol=0)
        metadata = handle.last_metadata
        work = metadata["tensor_plan_work"]
        spent = parent.receipt()["consumed_derivative_work"]-before
        assert spent == work["planned_work"]+work["construction_work"]
        assert spent == metadata["receipt"]["consumed_derivative_work"]
        assert parent.receipt()["live_memory_bytes"] == 0
        assert metadata["physical_shots"] == metadata["host_quantum_calls"] == metadata["device_updates"] == 0


@pytest.mark.parametrize("preprocessed,extra_gate", [(False, False), (True, False), (False, True)])
def test_lowered_or_mixed_parameter_sources_keep_the_real_cached_query_path(preprocessed, extra_gate, monkeypatch):
    p, q = qb.ParameterVector("input", 2)
    source = qb.QuantumCircuit(1)
    source.ry(p*p+q, 0)
    builder = QNode.from_circuit(source, qb.PauliZ(0)).fn
    def program(tape, point):
        if not preprocessed and not extra_gate:
            tape.ry(tf.sin(point[0])**2+point[1], 0)
            return tape.expval(qb.PauliZ(0))
        result = builder(tape, tf.reverse(point, [0]) if preprocessed else point)
        if extra_gate:
            tape.rx(.2*point[0], 0)
        return result
    node = QNode(program, 1, interface="tensorflow", diff_method="adjoint", max_diff=2)
    handle = node.compile_tensorflow(input_signature=[tf.TensorSpec((2,), tf.float64)])
    assert handle._frozen_binding is not None
    assert handle._scalar_lowering_work["execution"] == "existing native ParameterExpression only"
    functions, complete = [], handle._run_graph
    def actual_cached(function, packet):
        assert hasattr(function, "get_concrete_function")
        functions.append(id(function))
        return complete(function, packet)
    monkeypatch.setattr(handle, "_run_graph", actual_cached)
    for point in ([.37, .82], [.41, .91]):
        value = np.cos(point[1]**2+point[0]) if preprocessed else np.cos(point[0]**2+point[1])*np.cos(.2*point[0]) if extra_gate else np.cos(np.sin(point[0])**2+point[1])
        request = DerivativeExecutionRequest(node, tf.constant(point, tf.float64), derivative_kind="value", derivative_order=0)
        np.testing.assert_allclose(handle.execute(request).value, value, atol=2e-12, rtol=0)
    assert len(set(functions)) == 1


def test_fixed_circuit_zero_parameter_signature_is_a_valid_managed_value():
    source = qb.QuantumCircuit(1)
    source.h(0)
    node = QNode.from_circuit(source, qb.PauliX(0), interface="tensorflow", diff_method="adjoint", max_diff=2)
    handle = node.compile_tensorflow(input_signature=[tf.TensorSpec((0,), tf.float64)])
    np.testing.assert_allclose(handle(tf.constant([], tf.float64)), 1., atol=2e-12, rtol=0)


def test_native_expression_outside_frozen_subset_keeps_its_existing_tf_query_contract():
    p, q = qb.ParameterVector("input", 2)
    source = qb.QuantumCircuit(1)
    source.ry(p**q, 0)
    builder, constructions = QNode.from_circuit(source, qb.PauliZ(0)).fn, []
    def program(tape, point):
        constructions.append("source")
        return builder(tape, point)
    node = QNode(program, 1, interface="tensorflow", diff_method="adjoint", max_diff=2)
    handle = node.compile_tensorflow(input_signature=[tf.TensorSpec((2,), tf.float64)])
    assert handle._frozen_binding is None
    for point in ([.37, .82], [.41, .91]):
        request = DerivativeExecutionRequest(node, tf.constant(point, tf.float64), derivative_kind="value", derivative_order=0)
        np.testing.assert_allclose(handle.execute(request).value, np.cos(point[0]**point[1]), atol=2e-12, rtol=0)
    assert constructions == ["source"]
