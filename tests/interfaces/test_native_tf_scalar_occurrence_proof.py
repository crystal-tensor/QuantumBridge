# Copyright 2026 QuantumBridge Contributors. Apache-2.0.
"""Read-only ordered provenance checks are not a second scalar evaluator."""

import math

import pytest

import quantumbridge as qb
from quantumbridge.diff import HigherOrderLimits
from quantumbridge.diff.compiled_parameters import FrozenParameterBinding
from quantumbridge.execution.resource_context import ResourceScope
from quantumbridge.execution.resource_ledger import UnifiedResourceLedger
from quantumbridge.interfaces.tensorflow_scalar_lowering import lower_scalar_graph,ScalarGraphCapabilityMiss

tf = pytest.importorskip("tensorflow")


def capture(function,size):
    concrete = tf.function(function,input_signature=[tf.TensorSpec((size,),tf.float64)],
        autograph=False).get_concrete_function()
    return concrete.graph.as_graph_def(add_shapes=True),concrete.inputs[0].name,concrete.outputs[0].name


def verify(graph,names,binding,**options):
    return lower_scalar_graph(graph,input_name=names[0],output_name=names[1],
        parameters=binding.parameters,verify_occurrence_only=binding,**options)


@pytest.mark.parametrize("case", ["identity","sum","square","sin","native_chain","reverse",
    "retained","partial","constant","repeat","identity_layout"])
def test_readonly_proof_preserves_position_order_bits_and_existing_owned_context(case,monkeypatch):
    vector = qb.ParameterVector("angles",12)
    p,q = vector[2],vector[10]
    parameters = (p,q)
    if case == "identity":
        function,expressions = lambda x:tf.stack([x[0],x[1]]),(p,q)
    elif case == "sum":
        function,expressions = lambda x:tf.stack([x[0]+x[1]]),(p+q,)
    elif case == "square":
        function,expressions = lambda x:tf.stack([x[0],x[1]*x[1]+.4]),(p,q*q+.4)
    elif case == "sin":
        function,expressions = lambda x:tf.stack([tf.sin(x[0]),x[1]]),(p.sin(),q)
    elif case == "native_chain":
        function,expressions = lambda x:tf.stack([-x[0],x[1]*x[1]+.4,x[0]]),(-p,q*q+.4,p)
    elif case == "reverse":
        function,expressions = lambda x:tf.reverse(x,[0]),(q,p)
    elif case == "retained":
        function,expressions = lambda x:tf.stack([tf.cos(x[1])]),((q.sin()+p*p).gradient(q),)
    elif case == "partial":
        parameters = (p,)
        function,expressions = lambda x:tf.constant([math.cos(.31)],tf.float64),((q.sin()+p*p).gradient(q).assign(q,.31),)
    elif case == "constant":
        parameters = ()
        function,expressions = lambda x:tf.constant([2.],tf.float64),(2.,)
    elif case == "repeat":
        parameters = (p,)
        function,expressions = lambda x:tf.stack([x[0],x[0]]),(p,p)
    else:
        function,expressions = lambda x:tf.identity(tf.reshape(x,(2,))),(p,q)
    graph,input_name,output_name = capture(function,len(parameters))
    binding = FrozenParameterBinding.create(parameters,expressions)
    original = graph.SerializeToString(deterministic=True)
    def forbidden(*a,**k):
        pytest.fail("Readonly occurrence verification executed or emitted a scalar graph")
    monkeypatch.setattr(tf,"import_graph_def",forbidden)
    monkeypatch.setattr(FrozenParameterBinding,"evaluate",forbidden)
    monkeypatch.setattr(qb.ParameterExpression,"__post_init__",forbidden)
    ledger = UnifiedResourceLedger()
    with ResourceScope(ledger):
        result,work = verify(graph,(input_name,output_name),binding,ledger=ledger)
    assert result is binding
    assert work["input_uuids"] == binding.parameter_uuids
    assert work["output_occurrences"] == len(expressions)
    assert graph.SerializeToString(deterministic=True) == original
    assert ledger.receipt()["consumed_derivative_work"] == work["construction_work"] > 0
    assert ledger.receipt()["live_memory_bytes"] == 0


@pytest.mark.parametrize("case", ["scaled","other_position","reversed_operands","signed_zero",
    "missing_output","extra_output"])
def test_different_ordered_occurrences_are_refused_without_numeric_sampling(case):
    p,q = qb.Parameter("p"),qb.Parameter("q")
    parameters = (p,q)
    if case == "scaled":
        function,expressions = lambda x:tf.stack([x[0],x[1]]),(p*2,q)
    elif case == "other_position":
        function,expressions = lambda x:tf.stack([x[0],x[1]]),(q,p)
    elif case == "reversed_operands":
        function,expressions = lambda x:tf.stack([x[0]+x[1]]),(q+p,)
    elif case == "signed_zero":
        parameters = (p,)
        function = lambda x:tf.stack([x[0]+tf.constant(0.,tf.float64)])
        expressions = (qb.ParameterExpression("+",(p.expression(),qb.ParameterExpression("const",(-0.,)))),)
    elif case == "missing_output":
        function,expressions = lambda x:tf.stack([x[0],x[1]]),(p+q,)
    else:
        function,expressions = lambda x:tf.stack([x[0]+x[1]]),(p,q)
    graph,input_name,output_name = capture(function,len(parameters))
    binding = FrozenParameterBinding.create(parameters,expressions)
    ledger = UnifiedResourceLedger()
    with ResourceScope(ledger),pytest.raises(qb.UnsupportedFeature,match="occurrences"):
        verify(graph,(input_name,output_name),binding,ledger=ledger)
    assert ledger.receipt()["live_memory_bytes"] == ledger.receipt()["reserved_derivative_work"] == 0


def test_proof_specific_ops_do_not_expand_normal_scalar_lowering():
    p = qb.Parameter("p")
    graph,input_name,output_name = capture(lambda x:tf.stack([-x[0]]),1)
    binding = FrozenParameterBinding.create((p,),(-p,))
    with pytest.raises(ScalarGraphCapabilityMiss):
        lower_scalar_graph(graph,input_name=input_name,output_name=output_name,parameters=(p,))
    assert verify(graph,(input_name,output_name),binding)[0] is binding
    with pytest.raises(MemoryError):
        verify(graph,(input_name,output_name),binding,limits=HigherOrderLimits(max_memory_bytes=1))


def test_changed_graph_literal_cannot_reuse_a_successful_source_receipt():
    p = qb.Parameter("p")
    graph,input_name,output_name = capture(lambda x:tf.stack([x[0]+.4]),1)
    binding = FrozenParameterBinding.create((p,),(p+.4,))
    _,work = verify(graph,(input_name,output_name),binding)
    for node in graph.node:
        if node.op == "Const" and node.attr["dtype"].type == tf.float64.as_datatype_enum:
            node.attr["value"].tensor.CopyFrom(tf.make_tensor_proto(.5,dtype=tf.float64))
    ledger = UnifiedResourceLedger()
    with ResourceScope(ledger),pytest.raises(qb.UnsupportedFeature,match="occurrences"):
        verify(graph,(input_name,output_name),binding,ledger=ledger)
    assert work["source_sha256"]
    assert ledger.receipt()["live_memory_bytes"] == 0
