# Copyright 2026 QuantumBridge Contributors. Apache-2.0.
"""Public construction failures must not publish a fallback or poison an owner."""

import numpy as np
import pytest

import quantumbridge as qb
from quantumbridge.core.classical import UnsupportedFeature
from quantumbridge.execution.resource_context import ResourceScope
from quantumbridge.execution.resource_ledger import UnifiedResourceLedger
from quantumbridge.qml import QNode
from test_native_tf_scalar_graph_lowering import tf


def node_for(kind="smooth"):
    calls = []
    def program(tape, point):
        calls.append("construct")
        a, b = point[0], point[1]
        if kind == "nan":
            angle = tf.sin(a)+b+tf.constant(float("nan"), tf.float64)
        elif kind == "infinity":
            angle = tf.sin(a)+b+tf.constant(float("inf"), tf.float64)
        elif kind == "power":
            angle = a**b
        elif kind == "tan":
            angle = tf.tan(a)+b
        elif kind == "divide":
            angle = a/b
        elif kind == "unused":
            angle = tf.sin(a)
        elif kind == "new_axis":
            angle = tf.reshape(point[tf.newaxis, :], (2,))[0]+b
        elif kind == "ellipsis":
            angle = tf.reshape(point, (1, 2))[..., 0][0]+b
        else:
            angle = tf.sin(a)**2+b
        tape.ry(angle, 0)
        return tape.expval(qb.PauliZ(0))
    return QNode(program, 1, interface="tensorflow", diff_method="adjoint", max_diff=2), calls


def compile_node(node):
    return node.compile_tensorflow(input_signature=[tf.TensorSpec((2,), tf.float64)])


def legacy_reference(kind, point):
    a, b = point
    if kind == "power":
        angle = a**b
        slope = np.array([b*a**(b-1), angle*np.log(a)])
        cross = a**(b-1)*(1+b*np.log(a))
        second = np.array([[b*(b-1)*a**(b-2), cross], [cross, angle*np.log(a)**2]])
    elif kind == "tan":
        angle, slope = np.tan(a)+b, np.array([1/np.cos(a)**2, 1.])
        second = np.diag([2*np.tan(a)/np.cos(a)**2, 0.])
    elif kind == "divide":
        angle, slope = a/b, np.array([1/b, -a/b**2])
        second = np.array([[0., -1/b**2], [-1/b**2, 2*a/b**3]])
    elif kind == "unused":
        angle, slope = np.sin(a), np.array([np.cos(a), 0.])
        second = np.diag([-np.sin(a), 0.])
    else:
        angle, slope, second = a+b, np.ones(2), np.zeros((2, 2))
    return np.cos(angle), -np.sin(angle)*slope, -np.cos(angle)*np.outer(slope, slope)-np.sin(angle)*second


@pytest.mark.parametrize("kind", ["nan", "infinity"])
def test_nonfinite_source_is_a_fatal_public_construction_refusal(kind):
    node, calls = node_for(kind)
    parent = UnifiedResourceLedger()
    with ResourceScope(parent), pytest.raises(UnsupportedFeature, match="Nonfinite"):
        compile_node(node)
    assert calls == ["construct"]
    receipt = parent.receipt()
    assert receipt["live_memory_bytes"] == receipt["reserved_derivative_work"] == 0


def test_unclassified_lowering_error_must_not_publish_an_old_query_handle(monkeypatch):
    import quantumbridge.interfaces.tensorflow_scalar_lowering as module
    node, calls = node_for()
    def reject(*a, **k):
        raise UnsupportedFeature("scalar_identity_rejected", "injected identity rejection")
    monkeypatch.setattr(module, "lower_scalar_graph", reject)
    with pytest.raises(UnsupportedFeature, match="identity rejection"):
        compile_node(node)
    assert calls == ["construct"]


@pytest.mark.parametrize("kind", ["power", "tan", "divide", "unused", "new_axis", "ellipsis"])
def test_existing_legal_queries_remain_real_cached_math_for_capability_misses(kind):
    from quantumbridge.execution.derivative_request import DerivativeExecutionRequest
    node, calls = node_for(kind)
    handle = compile_node(node)
    assert handle._frozen_binding is None
    for raw in ([.37, .82], [.41, .91]):
        x = tf.constant(raw, tf.float64)
        reference, gradient, hessian = legacy_reference(kind, raw)
        for derivative in ("value", "gradient", "hvp"):
            query = DerivativeExecutionRequest(node, x, derivative_kind=derivative,
                derivative_order=0 if derivative == "value" else 2 if derivative == "hvp" else 1,
                tangent=tf.constant([.4, -.3], tf.float64) if derivative == "hvp" else None)
            result = handle.execute(query)
            np.testing.assert_allclose(result.value, reference, atol=2e-12, rtol=0)
            if derivative != "value":
                expected = gradient if derivative == "gradient" else hessian @ [.4, -.3]
                np.testing.assert_allclose(result.derivative, expected, atol=2e-10, rtol=0)
    assert calls == ["construct"]


@pytest.mark.parametrize("kind", ["unused_nan", "callback", "control", "custom_gradient"])
def test_capability_miss_cannot_hide_an_unsafe_original_source(kind):
    invoked = []
    def program(tape, point):
        a = tf.tan(point[0])+point[1]
        if kind == "unused_nan":
            tf.constant(float("nan"), tf.float64)
        elif kind == "callback":
            def callback(x):
                invoked.append("callback")
                return x
            extra = tf.numpy_function(callback, [point[0]], tf.float64, stateful=False)
            extra.set_shape(())
        elif kind == "control":
            barrier = tf.no_op()
            with tf.control_dependencies([barrier]):
                a = tf.identity(a)
        else:
            @tf.custom_gradient
            def hidden(x):
                return x, lambda g: g
            a = hidden(a)
        tape.ry(a, 0)
        return tape.expval(qb.PauliZ(0))
    node = QNode(program, 1, interface="tensorflow", diff_method="adjoint", max_diff=2)
    parent = UnifiedResourceLedger()
    with ResourceScope(parent), pytest.raises(UnsupportedFeature):
        compile_node(node)
    assert not invoked
    assert parent.receipt()["live_memory_bytes"] == parent.receipt()["reserved_derivative_work"] == 0


def test_capability_miss_on_mutated_graph_cannot_select_original_cached_query(monkeypatch):
    import quantumbridge.interfaces.tensorflow_scalar_lowering as module
    original = module.lower_scalar_graph
    def mutate(graph, **options):
        graph.node.add(name="unknown_unused", op="UnregisteredUnknownOperation")
        return original(graph, **options)
    node, calls = node_for()
    monkeypatch.setattr(module, "lower_scalar_graph", mutate)
    with pytest.raises(UnsupportedFeature, match="identity changed"):
        compile_node(node)
    assert calls == ["construct"]


@pytest.mark.parametrize("value", [float("nan"), float("inf")])
def test_nonfinite_eager_capture_cannot_bypass_scalar_source_admission(value):
    fixed = tf.constant(value, tf.float64)
    def program(tape, point):
        tape.ry(tf.sin(point[0])+point[1]+fixed, 0)
        return tape.expval(qb.PauliZ(0))
    node = QNode(program, 1, interface="tensorflow", max_diff=2)
    with pytest.raises(UnsupportedFeature, match="Nonfinite captured"):
        compile_node(node)


def test_fixed_eager_captures_keep_correct_queries_and_distinct_mathematical_identity():
    from quantumbridge.execution.derivative_request import DerivativeExecutionRequest
    def make(value):
        fixed = tf.constant(value, tf.float64)
        def program(tape, point):
            tape.ry(tf.sin(point[0])+point[1]+fixed, 0)
            return tape.expval(qb.PauliZ(0))
        node = QNode(program, 1, interface="tensorflow", max_diff=2, diff_method="adjoint")
        return node, compile_node(node)
    first_node, first = make(.2)
    second_node, second = make(.4)
    assert first._identity != second._identity
    assert first._legacy_scalar_work["captured_constant_sha256"] != second._legacy_scalar_work["captured_constant_sha256"]
    for node, handle, fixed in ((first_node, first, .2), (second_node, second, .4)):
        point = tf.constant([.37, .82], tf.float64)
        request = DerivativeExecutionRequest(node, point, derivative_kind="gradient", derivative_order=1)
        result = handle.execute(request)
        a = np.sin(.37)+.82+fixed
        np.testing.assert_allclose(result.value, np.cos(a), atol=2e-12, rtol=0)
        np.testing.assert_allclose(result.derivative, -np.sin(a)*np.array([np.cos(.37), 1.]), atol=2e-11, rtol=0)


def test_native_ast_capture_does_not_retry_an_unclassified_identity_rejection(monkeypatch):
    from quantumbridge.diff.compiled_parameters import FrozenParameterBinding
    p, q = qb.ParameterVector("input", 2)
    node = QNode.from_circuit(qb.Circuit(1).ry(p*p+q, 0), qb.PauliZ(0),
        interface="tensorflow", diff_method="adjoint", max_diff=2)
    calls = []
    def reject(*a, **k):
        calls.append("binding")
        raise UnsupportedFeature("native_binding_identity", "native binding identity rejected")
    monkeypatch.setattr(FrozenParameterBinding, "create", classmethod(reject))
    with pytest.raises(UnsupportedFeature, match="identity rejected"):
        compile_node(node)
    assert calls == ["binding"]


@pytest.mark.parametrize("dtype", [tf.float16, tf.bfloat16, tf.float32, tf.float64, tf.complex64, tf.complex128])
@pytest.mark.parametrize("value", [float("nan"), float("inf")], ids=["nan", "infinity"])
@pytest.mark.parametrize("storage", ["captured", "graph_const"])
def test_all_floating_source_dtypes_reject_nonfinite_data(dtype, value, storage):
    fixed = tf.constant(value, dtype)
    def program(tape, point):
        # Tan deliberately misses native lowering before the later constant.
        a = tf.tan(point[0])+point[1]
        data = fixed if storage == "captured" else tf.constant(value, dtype)
        tape.ry(a+tf.cast(data, tf.float64), 0)
        return tape.expval(qb.PauliZ(0))
    node = QNode(program, 1, interface="tensorflow", max_diff=2)
    parent = UnifiedResourceLedger()
    with ResourceScope(parent), pytest.raises(UnsupportedFeature, match="Nonfinite"):
        compile_node(node)
    assert parent.receipt()["live_memory_bytes"] == parent.receipt()["reserved_derivative_work"] == 0


@pytest.mark.parametrize("storage", ["captured", "graph_const"])
def test_finite_bfloat_source_remains_a_valid_previous_query(storage):
    from quantumbridge.execution.derivative_request import DerivativeExecutionRequest
    fixed = tf.constant(.2, tf.bfloat16)
    def program(tape, point):
        a = tf.tan(point[0])+point[1]
        data = fixed if storage == "captured" else tf.constant(.2, tf.bfloat16)
        tape.ry(a+tf.cast(data, tf.float64), 0)
        return tape.expval(qb.PauliZ(0))
    node = QNode(program, 1, interface="tensorflow", max_diff=2)
    handle = compile_node(node)
    point = tf.constant([.37, .82], tf.float64)
    result = handle.execute(DerivativeExecutionRequest(node, point, derivative_kind="gradient", derivative_order=1))
    a = np.tan(.37)+.82+float(fixed.numpy())
    np.testing.assert_allclose(result.value, np.cos(a), atol=2e-12, rtol=0)
    np.testing.assert_allclose(result.derivative, -np.sin(a)*np.array([1/np.cos(.37)**2, 1.]), atol=2e-11, rtol=0)
