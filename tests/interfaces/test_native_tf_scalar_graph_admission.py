# Copyright 2026 QuantumBridge Contributors. Apache-2.0.
"""Fail-closed scalar-data import, identities, layouts and construction budgets."""

from concurrent.futures import ThreadPoolExecutor
from dataclasses import replace

import numpy as np
import pytest

import quantumbridge as qb
from quantumbridge.core.classical import UnsupportedFeature
from quantumbridge.core.symbolic_limits import SymbolicExpressionLimits, SymbolicResourceLimitError, symbolic_expression_scope
from quantumbridge.diff import HigherOrderLimits
from quantumbridge.execution.resource_context import ResourceScope
from quantumbridge.execution.resource_ledger import UnifiedResourceLedger
from quantumbridge.execution.resource_limits import UnifiedExecutionLimits
from quantumbridge.interfaces.tensorflow_autodiff import TensorFlowBridgeLimits
from quantumbridge.interfaces.tensorflow_scalar_lowering import lower_scalar_graph
from quantumbridge.qml import QNode
from test_native_tf_scalar_graph_lowering import capture, tf


def lower(graph, root, output, **options):
    return lower_scalar_graph(graph, input_name=root, output_name=output,
        parameters=tuple(qb.ParameterVector("registered", 2)), allow_square=True, **options)


def constant(graph, name, value, dtype=tf.float64):
    node = graph.node.add(name=name, op="Const")
    node.attr["dtype"].type = dtype.as_datatype_enum
    node.attr["value"].tensor.CopyFrom(tf.make_tensor_proto(value, dtype=dtype))
    node.attr["_output_shapes"].list.shape.add().CopyFrom(node.attr["value"].tensor.tensor_shape)
    return node


@pytest.mark.parametrize("mutation", ["unknown_unused", "function", "control", "missing", "bad_port",
    "cycle", "duplicate", "external_input", "root_dtype", "dynamic_shape", "output_shape",
    "unknown_attr", "attr_type", "nan", "inf", "const_dtype", "const_shape", "const_bytes",
    "resource_storage", "remote_device", "gpu", "zero_stride", "new_axis", "ellipsis", "index_dtype"])
def test_whole_source_refuses_even_unused_invalid_nodes(mutation):
    graph, root, output = capture("sin")
    by_op = {n.op: n for n in graph.node}
    identity, placeholder, slicing = by_op["Identity"], by_op["Placeholder"], by_op["StridedSlice"]
    if mutation == "unknown_unused":
        graph.node.add(name="unused", op="RandomUniform")
    elif mutation == "function":
        graph.library.function.add().signature.name = "opaque"
    elif mutation == "control":
        identity.input.append("^"+placeholder.name)
    elif mutation == "missing":
        identity.input[0] = "missing:0"
    elif mutation == "bad_port":
        identity.input[0] = placeholder.name+":4"
    elif mutation == "cycle":
        identity.input[0] = identity.name+":0"
    elif mutation == "duplicate":
        graph.node.add().CopyFrom(identity)
    elif mutation == "external_input":
        extra = graph.node.add()
        extra.CopyFrom(placeholder)
        extra.name = "foreign_input"
    elif mutation == "root_dtype":
        placeholder.attr["dtype"].type = tf.float32.as_datatype_enum
    elif mutation == "dynamic_shape":
        placeholder.attr["shape"].shape.dim[0].size = -1
    elif mutation == "output_shape":
        identity.attr["_output_shapes"].list.shape[0].dim[0].size = 3
    elif mutation == "unknown_attr":
        identity.attr["custom_gradient"].s = b"opaque"
    elif mutation == "attr_type":
        identity.attr["T"].s = b"float64"
    elif mutation in ("nan", "inf"):
        constant(graph, "unused_bad_number", float(mutation))
    elif mutation.startswith("const_") or mutation == "resource_storage":
        bad = constant(graph, "unused_bad_const", [1., 2.])
        if mutation == "const_dtype":
            bad.attr["value"].tensor.dtype = tf.int64.as_datatype_enum
        elif mutation == "const_shape":
            bad.attr["value"].tensor.tensor_shape.dim[0].size = 3
        elif mutation == "const_bytes":
            bad.attr["value"].tensor.tensor_content = b"short"
        else:
            bad.attr["value"].tensor.resource_handle_val.add()
    elif mutation in ("remote_device", "gpu"):
        identity.device = "/job:remote/task:1/device:CPU:0" if mutation == "remote_device" else "/device:GPU:0"
    elif mutation == "zero_stride":
        source = next(n for n in graph.node if n.name == slicing.input[3])
        source.attr["value"].tensor.CopyFrom(tf.make_tensor_proto([0], tf.int32))
    elif mutation in ("new_axis", "ellipsis"):
        slicing.attr[mutation+"_mask"].i = 1
    else:
        slicing.attr["Index"].type = tf.int64.as_datatype_enum
    ledger = UnifiedResourceLedger()
    with pytest.raises(UnsupportedFeature):
        lower(graph, root, output, ledger=ledger)
    assert ledger.receipt()["live_memory_bytes"] == 0
    assert ledger.receipt()["reserved_derivative_work"] == 0


@pytest.mark.parametrize("budget", ["bytes", "nodes", "elements", "rank", "memory", "work", "scope"])
def test_resource_refusal_propagates_and_releases_reservations(budget):
    graph, root, output = capture("layout")
    bridge, higher, ledger = TensorFlowBridgeLimits(), HigherOrderLimits(), UnifiedResourceLedger()
    if budget == "bytes":
        bridge = replace(bridge, max_scalar_graph_bytes=graph.ByteSize()-1)
    elif budget == "nodes":
        higher = replace(higher, max_parameter_graph_nodes=len(graph.node)-1)
    elif budget in ("elements", "rank"):
        bridge = replace(bridge, **{"max_scalar_"+budget: 1})
    elif budget == "memory":
        higher = replace(higher, max_memory_bytes=1)
    elif budget == "work":
        higher = replace(higher, max_adjoint_operations=1)
    else:
        ledger = UnifiedResourceLedger(UnifiedExecutionLimits(max_total_memory_bytes=1))
    with pytest.raises((MemoryError, RuntimeError)):
        lower(graph, root, output, bridge_limits=bridge, limits=higher, ledger=ledger)
    assert ledger.receipt()["live_memory_bytes"] == ledger.receipt()["reserved_derivative_work"] == 0


def test_exponential_dag_expansion_is_rejected_before_creating_any_native_ast(monkeypatch):
    import quantumbridge.interfaces.tensorflow_scalar_lowering as module
    graph, root, output = capture("reverse")
    previous = output
    template = next(n for n in graph.node if n.op == "Identity")
    for index in range(16):
        node = graph.node.add()
        node.CopyFrom(template)
        node.name, node.op = "doubling_"+str(index), "AddV2"
        del node.input[:]
        node.input.extend([previous, previous])
        previous = node.name+":0"
    monkeypatch.setattr(module, "ParameterExpression", lambda *a, **k: pytest.fail("Unbounded AST allocated before admission"))
    with pytest.raises(MemoryError, match="max_parameter_graph_nodes"):
        lower(graph, root, previous, limits=replace(HigherOrderLimits(), max_parameter_graph_nodes=500))


@pytest.mark.parametrize("exponent", [-1., .5, 0., 1., 3.])
def test_only_fixed_square_is_admitted(exponent):
    graph, root, output = capture("square")
    power = next(n for n in graph.node if n.op == "Pow")
    literal = next(n for n in graph.node if n.name == power.input[1])
    literal.attr["value"].tensor.CopyFrom(tf.make_tensor_proto(exponent, tf.float64))
    with pytest.raises(UnsupportedFeature, match="square"):
        lower(graph, root, output)


def test_symbolic_depth_failure_never_becomes_unsupported_fallback():
    graph, root, output = capture("nonlinear")
    with symbolic_expression_scope(replace(SymbolicExpressionLimits(), max_depth=2)):
        with pytest.raises(SymbolicResourceLimitError):
            lower(graph, root, output)


def test_frozen_snapshot_and_native_uuid_order_do_not_follow_mutated_source():
    graph, root, output = capture("reverse")
    parameters = tuple(reversed(tuple(qb.ParameterVector("input", 2))))
    binding, work = lower_scalar_graph(graph, input_name=root, output_name=output, parameters=parameters)
    graph.Clear()
    assert binding.parameters == parameters
    assert binding.parameter_uuids == tuple(str(p.uuid) for p in parameters)
    np.testing.assert_array_equal(binding.evaluate((.3, .8)), [.8, .3])
    with pytest.raises(TypeError):
        work["graph_bytes"] = 0
    fake = qb.Parameter(parameters[0].name)
    assert fake.uuid != parameters[0].uuid and fake not in binding.parameters
    with pytest.raises(ValueError):
        lower_scalar_graph(capture("reverse")[0], input_name=root, output_name=output,
            parameters=(parameters[0], fake))


def test_unused_registered_input_is_not_silently_pruned():
    function = tf.function(lambda x: tf.stack([tf.sin(x[0])]),
        input_signature=[tf.TensorSpec((2,), tf.float64)], autograph=False)
    concrete = function.get_concrete_function()
    with pytest.raises(UnsupportedFeature, match="provenance"):
        lower(concrete.graph.as_graph_def(add_shapes=True), concrete.inputs[0].name, concrete.outputs[0].name)


def test_active_scope_is_charged_once_and_cannot_be_bypassed():
    graph, root, output = capture("nonlinear")
    parent = UnifiedResourceLedger()
    child = UnifiedResourceLedger(parent=parent)
    with ResourceScope(parent):
        _, work = lower(graph, root, output, ledger=child)
        with pytest.raises(UnsupportedFeature, match="unrelated"):
            lower(graph, root, output, ledger=UnifiedResourceLedger())
    assert parent.receipt()["consumed_derivative_work"] == child.receipt()["consumed_derivative_work"] == work["construction_work"]
    assert parent.receipt()["live_memory_bytes"] == child.receipt()["live_memory_bytes"] == 0


def test_concurrent_compilation_keeps_native_identity_and_accounts_separate():
    graph, root, output = capture("reverse")
    def build(index):
        ledger = UnifiedResourceLedger()
        parameters = tuple(qb.ParameterVector("input_"+str(index), 2))
        binding, work = lower_scalar_graph(graph, input_name=root, output_name=output,
            parameters=parameters, ledger=ledger)
        return binding, work, ledger.receipt()
    with ThreadPoolExecutor(max_workers=3) as pool:
        results = list(pool.map(build, range(6)))
    assert len({p.uuid for b, _, _ in results for p in b.parameters}) == 12
    assert len({w["source_sha256"] for _, w, _ in results}) == 1
    for binding, work, receipt in results:
        np.testing.assert_array_equal(binding.evaluate((.3, .8)), [.8, .3])
        assert receipt["consumed_derivative_work"] == work["construction_work"]
        assert receipt["live_memory_bytes"] == 0


def test_managed_resource_failure_does_not_select_old_cached_pack(monkeypatch):
    import quantumbridge.interfaces.tensorflow_scalar_lowering as module
    def program(tape, point):
        tape.ry(tf.sin(point[0])**2+point[1], 0)
        return tape.expval(qb.PauliZ(0))
    node = QNode(program, 1, interface="tensorflow", max_diff=2)
    def refuse(*a, **k):
        raise MemoryError("scalar construction budget exhausted")
    monkeypatch.setattr(module, "lower_scalar_graph", refuse)
    with pytest.raises(MemoryError, match="scalar construction budget"):
        node.compile_tensorflow(input_signature=[tf.TensorSpec((2,), tf.float64)])


@pytest.mark.parametrize("kind", ["negative_axes", "negative_strides", "unpack_pack", "infer_reshape"])
def test_static_layouts_preserve_exact_native_parameter_columns(kind):
    def mapping(x):
        matrix = tf.reshape(x, (2, 2))
        if kind == "negative_axes":
            return tf.reshape(tf.reverse(matrix, [-1]), (4,))
        if kind == "negative_strides":
            return tf.reshape(matrix[::-1, ::-1], (4,))
        if kind == "unpack_pack":
            a, b = tf.unstack(matrix, axis=-1)
            return tf.reshape(tf.stack([b, a], axis=-1), (4,))
        return tf.reshape(tf.reshape(x, (2, -1)), (-1,))
    concrete = tf.function(mapping, input_signature=[tf.TensorSpec((4,), tf.float64)], autograph=False).get_concrete_function()
    parameters = tuple(qb.ParameterVector("columns", 4))
    binding, _ = lower_scalar_graph(concrete.graph.as_graph_def(add_shapes=True),
        input_name=concrete.inputs[0].name, output_name=concrete.outputs[0].name, parameters=parameters)
    permutation = [3, 2, 1, 0] if kind == "negative_strides" else list(range(4)) if kind == "infer_reshape" else [1, 0, 3, 2]
    point = tf.constant([-.7, 0., .4, .9], tf.float64)
    with tf.GradientTape() as tape:
        tape.watch(point)
        actual = tf.stack(binding.evaluate(tuple(tf.unstack(point))))
    np.testing.assert_array_equal(actual, point.numpy()[permutation])
    np.testing.assert_array_equal(tape.jacobian(actual, point), np.eye(4)[permutation])
    assert [e.args[0].uuid for e in binding.expressions] == [parameters[i].uuid for i in permutation]


def test_mutation_of_the_callers_graph_during_decode_does_not_change_snapshot(monkeypatch):
    import hashlib
    graph, root, output = capture("nonlinear")
    digest = hashlib.sha256(graph.SerializeToString(deterministic=True)).hexdigest()
    original = tf.make_ndarray
    def decode(tensor):
        graph.Clear()
        return original(tensor)
    monkeypatch.setattr(tf, "make_ndarray", decode)
    binding, work = lower(graph, root, output)
    np.testing.assert_allclose(binding.evaluate((.3, .8)), [np.sin(.3*.8+.4), np.exp(1.1)], atol=2e-15, rtol=0)
    assert work["source_sha256"] == digest


@pytest.mark.parametrize("kind", ["integer_arithmetic", "duplicate_axis", "dynamic_exponent"])
def test_unvalidated_semantics_do_not_become_a_native_binding(kind):
    graph, root, output = capture("reverse" if kind == "duplicate_axis" else "square")
    if kind == "integer_arithmetic":
        literal = constant(graph, "metadata", [1], tf.int64)
        bad = graph.node.add(name="unused_integer_math", op="AddV2", input=[literal.name, literal.name])
        bad.attr["T"].type = tf.int64.as_datatype_enum
        bad.attr["_output_shapes"].CopyFrom(literal.attr["_output_shapes"])
    elif kind == "duplicate_axis":
        reverse = next(n for n in graph.node if n.op == "ReverseV2")
        axes = next(n for n in graph.node if n.name == reverse.input[1])
        axes.attr["value"].tensor.CopyFrom(tf.make_tensor_proto([0, -1], tf.int32))
        axes.attr["_output_shapes"].list.shape[0].dim[0].size = 2
    else:
        power = next(n for n in graph.node if n.op == "Pow")
        power.input[1] = power.input[0]
    with pytest.raises(UnsupportedFeature):
        lower(graph, root, output)
