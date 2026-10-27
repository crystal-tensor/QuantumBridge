# Copyright 2026 QuantumBridge Contributors. Apache-2.0.
"""Request sequences, runtime failure accounting and unchanged default routes."""

from dataclasses import replace

import numpy as np
import pytest

import quantumbridge as qb
from quantumbridge.core.classical import UnsupportedFeature
from quantumbridge.execution.derivative_request import DerivativeExecutionRequest
from quantumbridge.execution.resource_context import ResourceScope
from quantumbridge.execution.resource_ledger import UnifiedResourceLedger
from quantumbridge.qml import QNode
from test_native_tf_managed_cached_execution import CASE, compile_node, make_node, tf


def scalar_handle():
    p, q = qb.ParameterVector("angles", 2)
    node = QNode.from_circuit(qb.Circuit(1).ry(p*p+q, 0), qb.PauliZ(0),
        interface="tensorflow", diff_method="adjoint", max_diff=2)
    return node, compile_node(node)


def scalar_request(node, kind, point=None):
    return DerivativeExecutionRequest(node, tf.constant(CASE["point"], tf.float64) if point is None else point,
        derivative_kind=kind, derivative_order=0 if kind == "value" else 2 if kind == "hvp" else 1,
        tangent=tf.constant([0.4, -0.3], tf.float64) if kind == "hvp" else None)


def test_value_gradient_hvp_value_sequence_charges_only_actual_missing_graphs():
    node, handle = scalar_handle()
    point = np.array(CASE["point"])
    angle, slope = point[0]**2+point[1], np.array([2*point[0], 1.])
    expected = dict(value=np.cos(angle), gradient=-np.sin(angle)*slope,
        hvp=(-np.cos(angle)*np.outer(slope, slope)-np.sin(angle)*np.diag([2., 0.])) @ [0.4, -0.3])
    ledger = UnifiedResourceLedger()
    first_gradient_cost = None
    with ResourceScope(ledger):
        for kind in ("value", "gradient", "hvp", "value", "gradient"):
            request = scalar_request(node, kind)
            bound = handle.estimate(request)
            before = ledger.receipt()["consumed_derivative_work"]
            result = handle.execute(request)
            spent = ledger.receipt()["consumed_derivative_work"]-before
            assert spent == bound["first_call_work"]
            np.testing.assert_allclose(result.value, expected["value"], atol=1e-12, rtol=0)
            if kind != "value":
                np.testing.assert_allclose(result.derivative, expected[kind], atol=1e-11, rtol=0)
            if kind == "gradient":
                if first_gradient_cost is None:
                    first_gradient_cost = spent
                else:
                    assert spent < first_gradient_cost
                    assert spent == bound["planned_work"]
            assert result.metadata["execution_mode"] == "MANAGED_EXPLICIT_QUERY"
            assert result.metadata["physical_shots"] == result.metadata["host_quantum_calls"] == result.metadata["device_updates"] == 0
    assert handle.cache_info()["graphs_built"] == 5
    assert ledger.receipt()["live_memory_bytes"] == ledger.receipt()["reserved_derivative_work"] == 0


def test_invalid_query_does_not_refund_attempted_work_or_count_as_completed():
    node, handle = scalar_handle()
    ledger = UnifiedResourceLedger()
    query = scalar_request(node, "gradient")
    with ResourceScope(ledger):
        first = handle.execute(query)
        before = ledger.receipt()
        bad = replace(query, parameters=tf.constant([float("nan"), 0.82], tf.float64))
        bound = handle.estimate(bad)
        with pytest.raises(tf.errors.InvalidArgumentError):
            handle.execute(bad)
        failed = ledger.receipt()
        assert failed["consumed_derivative_work"] == before["consumed_derivative_work"]+bound["planned_work"]
        assert failed["consumed_tapes"] == before["consumed_tapes"]
        again = handle.execute(query)
    np.testing.assert_array_equal(again.derivative, first.derivative)
    assert failed["live_memory_bytes"] == failed["reserved_derivative_work"] == 0


@pytest.mark.parametrize("failure", [RuntimeError, KeyboardInterrupt])
def test_failed_graph_construction_has_no_cached_success_and_preserves_spent_work(failure, monkeypatch):
    node, _ = make_node()
    handle = compile_node(node)
    query = DerivativeExecutionRequest(node, tf.constant(CASE["point"], tf.float64), derivative_kind="hessian", derivative_order=2)
    before = handle.cache_info()
    ledger = UnifiedResourceLedger()
    with monkeypatch.context() as patch:
        def failed(*args):
            raise failure("injected graph construction failure")
        patch.setattr(handle, "_build", failed)
        with ResourceScope(ledger), pytest.raises(failure):
            handle.execute(query)
    receipt = ledger.receipt()
    assert receipt["consumed_derivative_work"] > 0
    assert receipt["consumed_tapes"] == receipt["live_memory_bytes"] == receipt["reserved_derivative_work"] == 0
    assert handle.cache_info()["graphs_built"] == before["graphs_built"]
    with ResourceScope(ledger):
        result = handle.execute(query)
    np.testing.assert_allclose(result.derivative, CASE["hessians"], atol=2e-9, rtol=0)


def test_parameter_vector_shrink_regrow_keeps_both_snapshot_modes_mathematically_frozen():
    node, source = make_node()
    parameters = tuple(source.parameters)
    managed = compile_node(node)
    inline = node.compile_tensorflow_inline(parameters=parameters, input_signature=[tf.TensorSpec((2,), tf.float64)])
    parameters[0].vector.resize(0)
    parameters[0].vector.resize(2)
    point = tf.constant(CASE["point"], tf.float64)
    for handle in (managed, inline):
        np.testing.assert_allclose(handle(point), CASE["outputs"], atol=3e-12, rtol=0)


@pytest.mark.parametrize("method", ["best", "adjoint", "parameter-shift"])
def test_ordinary_default_qnode_dispatch_is_not_changed_by_optional_handle_capabilities(method, monkeypatch):
    import quantumbridge.interfaces.tensorflow_managed as managed_module
    import quantumbridge.interfaces.tensorflow_inline as inline_module
    def forbidden(*a, **k):
        pytest.fail("A default QNode automatically selected an explicit/experimental handle")
    monkeypatch.setattr(managed_module.ManagedTensorFlowQNode, "__init__", forbidden)
    monkeypatch.setattr(inline_module.TraceInlineTensorFlowQNode, "__init__", forbidden)
    def program(tape, x):
        tape.ry(x, 0)
        return tape.expval(qb.PauliZ(0))
    node = QNode(program, 1, interface="tensorflow", diff_method=method, max_diff=2)
    point = tf.constant(0.37, tf.float64)
    with tf.GradientTape() as reverse:
        reverse.watch(point)
        value = node(point)
    derivative = reverse.gradient(value, point)
    assert tf.is_tensor(value) and value.shape == () and value.dtype == tf.float64
    np.testing.assert_allclose([value, derivative], [np.cos(0.37), -np.sin(0.37)], atol=1e-12, rtol=0)
    assert node.last_metadata["gradient_method"] == ("adjoint" if method == "best" else method)
    assert "execution_capability" not in node.last_metadata


def test_trainable_hamiltonian_coefficients_are_not_silently_frozen():
    p, q = qb.ParameterVector("angles", 2)
    def program(tape, point):
        tape.ry(point[0], 0)
        return tape.expval(qb.Hamiltonian([(point[1], qb.PauliZ(0))]))
    node = QNode(program, 1, interface="tensorflow", diff_method="adjoint", max_diff=2)
    with pytest.raises((UnsupportedFeature, ValueError, TypeError)):
        node.compile_tensorflow(input_signature=[tf.TensorSpec((2,), tf.float64)])
    with pytest.raises((UnsupportedFeature, ValueError, TypeError)):
        node.compile_tensorflow_inline(parameters=(p, q), input_signature=[tf.TensorSpec((2,), tf.float64)])


def test_general_two_wire_power_does_not_receive_a_one_wire_inline_capability():
    p, q = qb.ParameterVector("angles", 2)
    body = qb.Circuit(2).rx(p, 0).cx(0, 1).ry(q, 1)
    source = qb.QuantumCircuit(2)
    source.append(body.to_gate().power(0.5, annotated=True), (0, 1))
    node = QNode.from_circuit(source, qb.PauliZ(0), interface="tensorflow", diff_method="adjoint", max_diff=2)
    with pytest.raises(UnsupportedFeature, match="width|multi-qubit|local"):
        node.compile_tensorflow_inline(parameters=(p, q), input_signature=[tf.TensorSpec((2,), tf.float64)])
