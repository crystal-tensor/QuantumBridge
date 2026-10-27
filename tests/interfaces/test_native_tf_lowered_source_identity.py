# Copyright 2026 QuantumBridge Contributors. Apache-2.0.
"""Scalar-source UUID columns, controlled native bodies and owner lifecycle."""

from dataclasses import replace
import gc

import numpy as np
import pytest

import quantumbridge as qb
from quantumbridge.core.classical import UnsupportedFeature
from quantumbridge.execution.resource_context import ResourceScope
from quantumbridge.execution.resource_ledger import UnifiedResourceLedger
from quantumbridge.execution.resource_limits import UnifiedExecutionLimits
from quantumbridge.interfaces.tensorflow_autodiff import TensorFlowBridgeLimits
from quantumbridge.qml import QNode
from test_native_tf_scalar_graph_lowering import tf
from test_native_tf_scalar_lowering_atomicity import compile_node, node_for
from test_native_tf_trace_inline_qnode import forbid_rebuild


@pytest.mark.parametrize("change", ["method", "max_diff", "higher", "unified", "bridge", "function", "expired", "binding", "observable"])
def test_lowered_source_checks_live_owner_and_snapshot_before_quantum_math(change, monkeypatch):
    node, _ = node_for()
    handle = compile_node(node)
    assert handle._scalar_lowering_work is not None
    if change == "method":
        node.diff_method = "parameter-shift"
    elif change == "max_diff":
        node.max_diff = 1
    elif change == "higher":
        from quantumbridge.diff import HigherOrderLimits
        node.higher_order_limits = HigherOrderLimits(max_memory_bytes=1000000)
    elif change == "unified":
        node.unified_limits = UnifiedExecutionLimits(max_derivative_work=1)
    elif change == "bridge":
        node.tensorflow_limits = TensorFlowBridgeLimits(max_input_elements=1)
    elif change == "function":
        node.fn = lambda *args: None
    elif change == "expired":
        del node
        gc.collect()
    elif change == "binding":
        handle._frozen_binding = replace(handle._frozen_binding,
            expressions=tuple(e+.1 for e in handle._frozen_binding.expressions))
    else:
        handle._whole._requests = (replace(handle._whole._requests[0], kind="var"),)
    def forbidden(*args, **kwargs):
        pytest.fail("Rejected live owner/snapshot executed quantum math")
    monkeypatch.setattr(handle, "_program", forbidden)
    parent = UnifiedResourceLedger()
    with ResourceScope(parent), pytest.raises(UnsupportedFeature):
        handle(tf.constant([.37, .82], tf.float64))
    assert parent.receipt()["consumed_derivative_work"] == parent.receipt()["live_memory_bytes"] == 0


def controlled_fixture(control):
    vector = qb.ParameterVector("angles", 2)
    p, q = vector
    gate = qb.Circuit(1).ry(p*p+q, 0).rz(.2*p, 0).to_gate().control(1, ctrl_state=control)
    source = qb.Circuit(2).h(0)
    source.global_phase = .17*p*q
    source.append(gate, (0, 1))
    builder = QNode.from_circuit(source, qb.PauliX(1)).fn
    calls = []
    def program(tape, point):
        calls.append("construct")
        result = builder(tape, tf.reverse(point, [0]))
        tape.rx(.2*point[0], 1)
        return result
    node = QNode(program, 2, interface="tensorflow", max_diff=2, diff_method="adjoint")
    handle = compile_node(node)
    return node, source, gate, vector, handle, calls


def expected_state(point, control):
    p, q = point
    a = q*q+p
    branch = np.array([np.exp(-.1j*q)*np.cos(a/2), np.exp(.1j*q)*np.sin(a/2)])
    inactive = np.array([1., 0.])
    state = np.concatenate([branch, inactive] if control == 0 else [inactive, branch])/np.sqrt(2)
    rx = np.array([[np.cos(.1*p), -1j*np.sin(.1*p)], [-1j*np.sin(.1*p), np.cos(.1*p)]])
    return np.exp(.17j*p*q)*np.kron(np.eye(2), rx) @ state


@pytest.mark.parametrize("control", [0, 1])
def test_complete_lowered_controlled_state_survives_vector_and_original_gate_changes(control, monkeypatch):
    node, source, gate, vector, handle, calls = controlled_fixture(control)
    assert handle._scalar_lowering_work is not None
    binding = handle._frozen_binding
    identities = binding.parameter_uuids
    # Each logical identity occurs in multiple independently compiled angles.
    assert all(sum(p in e.parameters for e in binding.expressions) >= 2 for p in binding.parameters)
    source_ids = tuple(p.uuid for p in source.parameters)
    for v in (vector, binding.parameters[0].vector):
        v.resize(0)
        v.resize(2)
    assert binding.parameter_uuids == identities
    assert tuple(p.uuid for p in source.parameters) == source_ids
    gate.base_gate.definition.rz(.37, 0)
    with monkeypatch.context() as patch:
        forbid_rebuild(patch)
        for raw in ([.37, .82], [.41, .91]):
            point = tf.constant(raw, tf.float64)
            packed = tf.stack(binding.evaluate(tuple(tf.unstack(point))))
            state = handle._whole.state(packed)
            expected = expected_state(raw, control)
            np.testing.assert_allclose(state, expected, atol=3e-12, rtol=0)
            x1 = np.kron(np.eye(2), np.array([[0., 1.], [1., 0.]]))
            np.testing.assert_allclose(handle(point), np.vdot(expected, x1 @ expected).real, atol=3e-12, rtol=0)
    assert calls == ["construct"] and node.fn is not None
