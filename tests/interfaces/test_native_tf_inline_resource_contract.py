# Copyright 2026 QuantumBridge Contributors. Apache-2.0.
"""Static inline admission is not cached-query invocation accounting."""

from dataclasses import replace
import gc

import numpy as np
import pytest

import quantumbridge as qb
from quantumbridge.core.classical import UnsupportedFeature
from quantumbridge.diff import HigherOrderLimits
from quantumbridge.diff.compiled_parameters import FrozenParameterBinding
from quantumbridge.execution.resource_context import ResourceScope
from quantumbridge.execution.resource_ledger import UnifiedResourceLedger
from quantumbridge.execution.resource_limits import UnifiedExecutionLimits
from quantumbridge.qml import QNode

from test_native_tf_trace_inline_qnode import CASE, inline_node, make_node, tf


def compile_inline(node, source, **options):
    return node.compile_tensorflow_inline(parameters=tuple(source.parameters),
        input_signature=[tf.TensorSpec((len(source.parameters),), tf.float64)], **options)


def test_scope_refuses_construction_and_invocation_without_spending_or_executing(monkeypatch):
    node, source, handle = inline_node()
    def failed(*a, **k):
        pytest.fail("Inline scope refusal happened after quantum work")
    monkeypatch.setattr(QNode, "_construct", failed)
    monkeypatch.setattr(handle, "_pack_values", failed)
    ledger = UnifiedResourceLedger()
    with ResourceScope(ledger):
        with pytest.raises(UnsupportedFeature, match="scope|ledger"):
            compile_inline(node, source)
        with pytest.raises(UnsupportedFeature, match="scope|ledger"):
            handle(tf.constant(CASE["point"], tf.float64))
    assert ledger.receipt()["consumed_derivative_work"] == 0


def test_expired_owner_is_not_silently_accepted():
    node, _, handle = inline_node()
    del node
    gc.collect()
    with pytest.raises(UnsupportedFeature, match="owner"):
        handle(tf.constant(CASE["point"], tf.float64))


@pytest.mark.parametrize("attribute,value", [("max_diff", 1), ("diff_method", "parameter-shift"),
    ("unified_limits", UnifiedExecutionLimits(max_derivative_work=0))])
def test_live_owner_configuration_tightening_invalidates_python_entry(attribute, value):
    node, _, handle = inline_node()
    setattr(node, attribute, value)
    with pytest.raises(UnsupportedFeature, match="owner"):
        handle(tf.constant(CASE["point"], tf.float64))


def test_zero_work_budget_refuses_before_source_construction(monkeypatch):
    node, source = make_node(unified_limits=UnifiedExecutionLimits(max_derivative_work=0))
    monkeypatch.setattr(node, "_construct", lambda *a, **k: pytest.fail("Zero-budget source was constructed"))
    with pytest.raises(MemoryError):
        compile_inline(node, source)


def test_ast_work_limit_and_malformed_scalar_refuse():
    p, q = qb.ParameterVector("angles", 2)
    with pytest.raises(MemoryError, match="max_parameter_graph_nodes"):
        FrozenParameterBinding.create((p, q), (p*q+q.sin(),), limits=HigherOrderLimits(max_parameter_graph_nodes=1))
    broken = object.__new__(qb.ParameterExpression)
    object.__setattr__(broken, "op", "not_an_operation")
    object.__setattr__(broken, "args", ())
    with pytest.raises((ValueError, UnsupportedFeature)):
        FrozenParameterBinding.create((), (broken,))


def test_native_source_and_parameter_vector_edits_do_not_pollute_snapshot():
    node, source, handle = inline_node()
    point = tf.constant(CASE["point"], tf.float64)
    before = tf.stack(handle(point))
    source.x(1)
    source.parameters[0].vector.resize(4)
    np.testing.assert_array_equal(tf.stack(handle(point)), before)
    assert handle.metadata["snapshot"] is True


def test_frozen_compiled_operation_mutation_is_detected():
    node, _, handle = inline_node()
    handle._whole._circuit.x(0)
    with pytest.raises(UnsupportedFeature, match="identity|store"):
        handle(tf.constant(CASE["point"], tf.float64))
    assert node.max_diff == 2


def test_wrong_shape_or_dtype_refuses_before_scalar_emission(monkeypatch):
    node, _, handle = inline_node()
    monkeypatch.setattr(handle, "_pack_values", lambda *a: pytest.fail("An invalid signature emitted a quantum graph"))
    for point in (tf.constant([0.3], tf.float64), tf.constant(CASE["point"], tf.float32)):
        with pytest.raises(ValueError, match="shape|float64"):
            handle(point)
    assert node.max_diff == 2


def test_runtime_bad_inputs_recover_in_one_cached_outer_graph():
    import math
    node, _, handle = inline_node()
    function = tf.function(handle, input_signature=[tf.TensorSpec((2,), tf.float64)], autograph=False, jit_compile=False)
    expected = function(tf.constant(CASE["point"], tf.float64))
    for bad in ([float("nan"), 0.82], [float("inf"), 0.82], [0., math.sqrt(2*math.pi-0.4)]):
        with pytest.raises(tf.errors.InvalidArgumentError):
            function(tf.constant(bad, tf.float64))
    np.testing.assert_array_equal(function(tf.constant(CASE["point"], tf.float64)), expected)
    assert function.experimental_get_tracing_count() == 1
    assert node.max_diff == 2


def test_external_cached_graph_is_explicitly_outside_python_owner_and_ledger_checks():
    node, _, handle = inline_node()
    function = tf.function(handle, input_signature=[tf.TensorSpec((2,), tf.float64)], autograph=False, jit_compile=False)
    expected = function(tf.constant(CASE["point"], tf.float64))
    node.unified_limits = UnifiedExecutionLimits(max_derivative_work=0)
    ledger = UnifiedResourceLedger()
    with ResourceScope(ledger):
        np.testing.assert_array_equal(function(tf.constant(CASE["point"], tf.float64)), expected)
    assert ledger.receipt()["consumed_derivative_work"] == 0
    assert handle.metadata["external_graph_execution"] == "OUT_OF_SCOPE"
    with pytest.raises(UnsupportedFeature, match="owner"):
        handle(tf.constant(CASE["point"], tf.float64))


def test_input_parameter_order_is_explicit_and_partial_bind_retains_correct_math():
    p, q = qb.ParameterVector("angles", 2)
    source = qb.Circuit(1).ry(p*p+q, 0).assign_parameters({p: 0.37})
    node = QNode.from_circuit(source, qb.PauliZ(0), interface="tensorflow", max_diff=2, diff_method="adjoint")
    handle = compile_inline(node, source)
    x = tf.constant([0.82], tf.float64)
    with tf.GradientTape() as reverse:
        reverse.watch(x)
        value = handle(x)
    np.testing.assert_allclose(value, np.cos(0.37**2+0.82), atol=1e-12, rtol=0)
    np.testing.assert_allclose(reverse.gradient(value, x), [-np.sin(0.37**2+0.82)], atol=1e-12, rtol=0)
    assert handle.metadata["parameter_uuids"] == (str(q.uuid),)


def test_inline_workspace_limit_is_not_waived_by_an_admitted_local_kernel():
    node, source, handle = inline_node()
    need = handle.metadata["budget"]["workspace_bytes"]
    other, other_source = make_node(higher_order_limits=replace(HigherOrderLimits(), max_memory_bytes=need-1))
    with pytest.raises(MemoryError, match="max_memory"):
        compile_inline(other, other_source)
    assert len(source.parameters) == 2 and node.max_diff == 2


def test_mutable_definition_and_observable_selection_do_not_rebind_snapshot():
    p, = qb.ParameterVector("angles", 1)
    source = qb.QuantumCircuit(1)
    source.append(qb.Circuit(1).ry(p, 0).to_gate(), (0,))
    observables = [qb.PauliZ(0)]
    builder = QNode.from_circuit(source, observables[0]).fn
    def program(tape, point):
        builder(tape, point)
        return tape.expval(observables[0])
    node = QNode(program, 1, interface="tensorflow", diff_method="adjoint", max_diff=2)
    handle = compile_inline(node, source)
    point = tf.constant([0.37], tf.float64)
    value = handle(point)
    source.data[0].operation.definition.x(0)
    observables[0] = qb.PauliX(0)
    np.testing.assert_array_equal(handle(point), value)


def test_foreign_tensor_scalar_mapping_is_explicitly_unsupported():
    p, = qb.ParameterVector("angles", 1)
    def program(tape, point):
        tape.ry(tf.sin(point[0]), 0)
        return tape.expval(qb.PauliZ(0))
    node = QNode(program, 1, interface="tensorflow", diff_method="adjoint", max_diff=2)
    with pytest.raises(UnsupportedFeature, match="native parameter syntax"):
        node.compile_tensorflow_inline(parameters=(p,), input_signature=[tf.TensorSpec((1,), tf.float64)])


def test_true_third_derivative_and_unapproved_second_order_are_refused():
    node, source, handle = inline_node()
    first_only = compile_inline(node, source, max_derivative_order=1)
    point = tf.constant(CASE["point"], tf.float64)
    for target, levels in ((first_only, 2), (handle, 3)):
        with pytest.raises(UnsupportedFeature, match="approval|third"):
            with tf.GradientTape() as third:
                third.watch(point)
                with tf.GradientTape() as second:
                    second.watch(point)
                    with tf.GradientTape() as first:
                        first.watch(point)
                        value = tf.reduce_sum(tf.stack(target(point)))
                    gradient = first.gradient(value, point)
                    projected = tf.reduce_sum(gradient)
                product = second.gradient(projected, point)
                contracted = tf.reduce_sum(product)
            if levels == 3:
                third.gradient(contracted, point)
