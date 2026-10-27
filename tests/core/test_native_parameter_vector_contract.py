# Copyright 2026 QuantumBridge Contributors.
# Licensed under the Apache License, Version 2.0.
"""Native vector ownership, public observations and pre-construction budgets."""
from copy import deepcopy
from uuid import UUID
import numpy as np
import pytest
import quantumbridge as qb
from quantumbridge.core.classical import UnsupportedFeature
from quantumbridge.core.gate_limits import GateCircuitLimits,gate_circuit_scope
from quantumbridge.core.symbolic_limits import SymbolicExpressionLimits,symbolic_expression_scope
from quantumbridge.execution import UnifiedResourceLedger as Ledger
from quantumbridge.execution.resource_context import ResourceScope
from quantumbridge.information import Operator
from quantumbridge.serialization import qpy_dumps,qpy_loads
from quantumbridge.ir.qb_ir import IRProgram
from quantumbridge.compat.qiskit_adapter import circuit_from_ir


def test_vector_public_list_slice_readonly_name_and_live_storage_contract():
    vector=qb.ParameterVector("v",3);params=vector.params;old=tuple(vector)
    assert type(params) is list and type(vector[::2]) is list and vector.params is params
    assert vector[::2]==[old[0],old[2]]
    vector.resize(1);assert params==[old[0]] and vector.params is params
    vector.resize(3);assert tuple(vector)==old and vector.params is params
    params.pop();assert len(vector)==2 and vector.params is params
    vector.resize(3);assert tuple(vector)==old
    with pytest.raises(AttributeError):vector.name="changed"
    with pytest.raises(AttributeError):vector.params=[]
    assert vector.name=="v" and [item.index for item in vector]==[0,1,2]
    assert all(item.vector is vector for item in vector)


@pytest.mark.parametrize("length",[True,np.int32(2),np.int64(3)])
def test_vector_accepts_native_integral_lengths_and_indexes(length):
    vector=qb.ParameterVector("",length)
    assert len(vector)==int(length) and vector.name==""
    assert vector[np.int64(0)].name=="[0]"
    from quantumbridge.core.parameters import ParameterVectorElement
    element=ParameterVectorElement(vector,np.int64(3))
    assert element.index==3 and element.vector is vector


@pytest.mark.parametrize("constructor",[True,False])
@pytest.mark.parametrize("budget",["gate","symbolic"])
def test_huge_vector_refuses_before_first_element_and_keeps_existing_state(monkeypatch,constructor,budget):
    from quantumbridge.core.parameters import ParameterVectorElement
    vector=qb.ParameterVector("v",2);old=tuple(vector);params=vector.params;root=vector._root_uuid
    def forbidden(*args,**kwargs):pytest.fail("element constructed before vector budget admission")
    monkeypatch.setattr(ParameterVectorElement,"__init__",forbidden)
    scope=gate_circuit_scope(GateCircuitLimits(max_gate_parameters=2)) if budget=="gate" else symbolic_expression_scope(SymbolicExpressionLimits(max_parameters=2))
    with scope,pytest.raises((MemoryError,ValueError)):
        if constructor:qb.ParameterVector("huge",10**12)
        else:vector.resize(10**12)
    assert tuple(vector)==old and vector.params is params and vector._root_uuid==root


def test_vector_resize_factory_failure_cannot_partially_replace_the_live_list(monkeypatch):
    from quantumbridge.core.parameters import ParameterVectorElement
    vector=qb.ParameterVector("v",2);params=vector.params;old=tuple(vector);original=ParameterVectorElement.__init__
    def factory(self,owner,index,uuid=None):
        if index==3:raise RuntimeError("construction fault")
        original(self,owner,index,uuid)
    monkeypatch.setattr(ParameterVectorElement,"__init__",factory)
    with pytest.raises(RuntimeError,match="construction fault"):vector.resize(5)
    assert tuple(vector)==old and vector.params is params
    monkeypatch.setattr(ParameterVectorElement,"__init__",original)
    vector.resize(5);assert params is vector.params and len(vector)==5


@pytest.mark.parametrize("action",["construct","resize","getitem","index","element"])
def test_managed_vector_foreign_integer_or_equality_protocols_do_not_execute(action):
    from quantumbridge.core.parameters import ParameterVectorElement
    class Foreign:
        def __index__(self):pytest.fail("foreign index callback")
        def __eq__(self,other):pytest.fail("foreign equality callback")
        def __hash__(self):pytest.fail("foreign hash callback")
        def __iter__(self):pytest.fail("foreign iterator callback")
    vector=qb.ParameterVector("v",2);old=tuple(vector);params=vector.params
    with ResourceScope(Ledger()),pytest.raises(UnsupportedFeature):
        if action=="construct":qb.ParameterVector("v",Foreign())
        elif action=="resize":vector.resize(Foreign())
        elif action=="getitem":vector[Foreign()]
        elif action=="index":vector.index(Foreign())
        else:ParameterVectorElement(vector,Foreign())
    assert tuple(vector)==old and vector.params is params


def test_managed_scalar_parameter_name_cannot_invoke_a_foreign_truth_protocol():
    class Name(str):
        def __len__(self):pytest.fail("foreign string truth callback")
    with ResourceScope(Ledger()),pytest.raises(UnsupportedFeature):qb.Parameter(Name("p"))


def test_managed_native_explicit_uuid_and_vector_growth_stay_callable():
    with ResourceScope(Ledger()):
        parameter=qb.Parameter("p",UUID("01234567-89ab-cdef-0123-456789abcdef"))
        vector=qb.ParameterVector("v",2);vector.resize(4)
        assert vector.index(vector[3])==3 and list(vector[1:3])==[vector[1],vector[2]]
        assert parameter==qb.Parameter("p",str(parameter.uuid))


def _bound_vector_chain(transport):
    vector=qb.ParameterVector("v",3);p,q=vector[0],vector[2]
    body=qb.QuantumCircuit(1,global_phase=q/5);body.rx(2*p+q,0)
    nested=qb.QuantumCircuit(1);nested.append(body.to_gate(),[0])
    controlled=nested.to_gate().control(2,ctrl_state="01")
    annotated=qb.AnnotatedOperation(controlled,[qb.InverseModifier(),qb.PowerModifier(2)])
    circuit=qb.QuantumCircuit(3);circuit.h(0);circuit.append(annotated,[0,1,2],copy=False)
    old_view=circuit.parameters;old_params=tuple(old_view);root=vector._root_uuid
    vector.resize(1);vector.resize(3)
    assert vector[2]==q and vector[2].uuid==q.uuid
    if transport=="ir":restored=circuit_from_ir(IRProgram.from_json(circuit.to_ir().to_json()))
    elif transport=="qpy":restored=qpy_loads(qpy_dumps(circuit))[0]
    else:restored=circuit
    if transport!="direct":
        circuit=qb.QuantumCircuit(3);circuit.compose(restored,inplace=True)
    circuit.assign_parameters({vector[0]:.2},inplace=True)
    assert tuple(old_view)==old_params and circuit.parameters==[q]
    actual=circuit.parameters[0]
    assert actual.vector._root_uuid==root and actual.index==2 and actual.uuid==q.uuid
    return circuit,vector


def _vector_chain_reference(x):
    angle=.4+x;k=.4
    value=np.cos(angle)*np.cos(k*x)
    first=-np.sin(angle)*np.cos(k*x)-k*np.cos(angle)*np.sin(k*x)
    second=-(1+k*k)*np.cos(angle)*np.cos(k*x)+2*k*np.sin(angle)*np.sin(k*x)
    return value,first,second


@pytest.mark.parametrize("transport",["direct","ir","qpy"])
@pytest.mark.parametrize("method",["parameter-shift","adjoint"])
def test_vector_resize_nested_control_annotation_view_binding_and_real_hvp(transport,method):
    from quantumbridge.qml import QNode
    circuit,vector=_bound_vector_chain(transport)
    x=.31;angle=.4+x;k=.4
    block=np.eye(8,dtype=complex)
    block[4:6,4:6]=np.exp(-1j*k*x)*np.array([[np.cos(angle),1j*np.sin(angle)],[1j*np.sin(angle),np.cos(angle)]])
    expected=block@np.kron(np.array([[1,1],[1,-1]])/np.sqrt(2),np.eye(4))
    np.testing.assert_allclose(Operator(circuit.assign_parameters({vector[2]:x})).data,expected,atol=3e-12,rtol=0)
    node=QNode.from_circuit(circuit,qb.PauliX(0),max_diff=2,diff_method=method)
    value,first,second=_vector_chain_reference(x)
    np.testing.assert_allclose(node(x),value,atol=3e-12,rtol=0)
    np.testing.assert_allclose(node.compute_jacobian(x),first,atol=7e-10,rtol=0)
    np.testing.assert_allclose(node.compute_hessian(x),second,atol=9e-10,rtol=0)
    np.testing.assert_allclose(node.compute_hvp(.7,x),.7*second,atol=9e-10,rtol=0)


@pytest.mark.parametrize("interface",["torch","autograd","jax","tensorflow"])
@pytest.mark.parametrize("transport",["ir","qpy"])
@pytest.mark.parametrize("method",["parameter-shift","adjoint"])
def test_vector_transport_framework_actual_graph_first_second_and_hvp(interface,transport,method):
    from quantumbridge.qml import QNode
    pytest.importorskip(interface)
    circuit,_=_bound_vector_chain(transport)
    node=QNode.from_circuit(circuit,qb.PauliX(0),max_diff=2,interface=interface,diff_method=method)
    x=.31;value,first,second=_vector_chain_reference(x)
    if interface=="torch":
        import torch
        point=torch.tensor(x,dtype=torch.float64,requires_grad=True)
        actual=node(point)
        gradient=torch.autograd.grad(actual,point,create_graph=True)[0]
        hessian=torch.autograd.grad(gradient,point,retain_graph=True)[0]
        hvp=torch.autograd.grad(gradient,point,grad_outputs=torch.tensor(.7,dtype=torch.float64))[0]
        received=[item.detach().numpy() for item in (actual,gradient,hessian,hvp)]
    elif interface=="autograd":
        import autograd
        received=[node(x),autograd.grad(node)(x),autograd.grad(autograd.grad(node))(x),
                  autograd.grad(lambda point:.7*autograd.grad(node)(point))(x)]
    elif interface=="jax":
        import jax
        import jax.numpy as jnp
        point=jnp.asarray(x,dtype=jnp.float64)
        actual,gradient=jax.jit(jax.value_and_grad(node))(point)
        hessian=jax.jit(jax.grad(jax.grad(node)))(point)
        _,hvp=jax.jit(lambda p:jax.jvp(jax.grad(node),(p,),(jnp.asarray(.7),)))(point)
        received=[np.asarray(item) for item in (actual,gradient,hessian,hvp)]
    else:
        import tensorflow as tf
        def evaluate(point):
            with tf.GradientTape(persistent=True) as outer:
                outer.watch(point)
                with tf.GradientTape() as inner:
                    inner.watch(point)
                    actual=node(point)
                gradient=inner.gradient(actual,point)
                directional=.7*gradient
            return actual,gradient,outer.gradient(gradient,point),outer.gradient(directional,point)
        received=[item.numpy() for item in tf.function(evaluate,autograph=False)(tf.constant(x,dtype=tf.float64))]
    np.testing.assert_allclose(received,[value,first,second,.7*second],atol=9e-10,rtol=0)


@pytest.mark.parametrize("transport",["ir","qpy"])
def test_empty_vector_name_has_actual_native_identity_roundtrip(transport):
    vector=qb.ParameterVector("",2);source=qb.QuantumCircuit(1);source.rx(vector[1],0)
    restored=circuit_from_ir(IRProgram.from_json(source.to_ir().to_json())) if transport=="ir" else qpy_loads(qpy_dumps(source))[0]
    parameter=restored.parameters[0]
    assert parameter==vector[1] and parameter.vector.name=="" and parameter.index==1
    assert not restored.assign_parameters({vector[1]:.3}).parameters


def test_actual_public_parameter_identity_agrees_without_collapsing_scalar_and_vector_names():
    pytest.importorskip("qiskit")
    from qiskit.circuit import Parameter,ParameterVector
    def observation(P,PV):
        p=P("p",uuid=UUID("01234567-89ab-cdef-0123-456789abcdef"));same=P("p",uuid=p.uuid);other=P("other",uuid=p.uuid)
        vector=PV("v",2);scalar=P(vector[1].name,uuid=vector[1].uuid)
        return p==same,p==other,hash(p)==hash(same),vector[1]==scalar,len({vector[1],scalar})
    assert observation(qb.Parameter,qb.ParameterVector)==observation(Parameter,ParameterVector)


def test_actual_public_vector_live_list_difference_is_explicit(record_property):
    public=pytest.importorskip("qiskit")
    from qiskit.circuit import ParameterVector
    vector=ParameterVector("v",3);params=vector.params;params.pop()
    native=qb.ParameterVector("v",3);native.params.pop()
    assert len(native)==len(native.params)==2
    if public.__version__.startswith("2.4."):
        assert len(vector)==len(params)==2
        record_property("contract","MATCH: mutable public list is the vector sequence")
    else:
        assert len(vector)==3 and len(vector.params)==2
        record_property("contract","INTENTIONAL_SAFETY_DIFFERENCE: observed public2.6 vector length/cache divergence; native one coherent list")


@pytest.mark.parametrize("direction",["native_to_public","public_to_native"])
def test_actual_bilateral_empty_vector_name_qpy_retains_root_index_uuid_and_real_binding(direction):
    import io
    public=pytest.importorskip("qiskit")
    from qiskit import qpy
    from qiskit.circuit import ParameterVector
    from qiskit.quantum_info import Operator as PublicOperator
    if direction=="native_to_public":
        vector=qb.ParameterVector("",2);source=qb.QuantumCircuit(1);source.rx(vector[1],0)
        restored=qpy.load(io.BytesIO(qpy_dumps(source)))[0];parameter=next(iter(restored.parameters))
        actual=PublicOperator(restored.assign_parameters({parameter:.3})).data
    else:
        vector=ParameterVector("",2);source=public.QuantumCircuit(1);source.rx(vector[1],0)
        stream=io.BytesIO();qpy.dump(source,stream,version=13)
        restored=qpy_loads(stream.getvalue())[0];parameter=restored.parameters[0]
        actual=Operator(restored.assign_parameters({parameter:.3})).data
    assert str(parameter.uuid)==str(vector[1].uuid) and parameter.vector.name=="" and parameter.index==1
    assert len(parameter.vector)==2
    np.testing.assert_allclose(actual,np.array([[np.cos(.15),-1j*np.sin(.15)],[-1j*np.sin(.15),np.cos(.15)]]),atol=3e-13,rtol=0)


@pytest.mark.parametrize("operation",["params-pop","resize-down-up","source-definition"])
def test_old_parameter_snapshot_survives_inplace_binding_after_external_vector_or_owner_changes(operation):
    vector=qb.ParameterVector("v",12);p,q=vector[2],vector[10]
    body=qb.QuantumCircuit(1,global_phase=q/5);body.rx(2*p+q,0)
    gate=body.to_gate();source=qb.QuantumCircuit(1);source.append(gate,[0],copy=True)
    old_view=source.parameters;old_params=tuple(old_view)
    if operation=="params-pop":vector.params.pop()
    elif operation=="resize-down-up":vector.resize(1);vector.resize(12)
    else:
        changed=qb.QuantumCircuit(1);changed.ry(7*p,0);gate.definition=changed
    source.assign_parameters({p:.2},inplace=True)
    new_view=source.parameters
    assert tuple(old_view)==old_params==(p,q) and list(new_view)==[q]
    assert list(source.lowered().parameters)==[q]
    np.testing.assert_allclose(Operator(source.assign_parameters({q:.3})).data,
        np.exp(.06j)*np.array([[np.cos(.35),-1j*np.sin(.35)],[-1j*np.sin(.35),np.cos(.35)]]),atol=3e-13,rtol=0)
