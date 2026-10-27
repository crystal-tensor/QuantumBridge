# Copyright 2026 QuantumBridge Contributors.
# Licensed under the Apache License, Version 2.0.
"""Actual public parameter snapshots, set semantics and native owner isolation."""
from collections.abc import MappingView
from copy import copy, deepcopy
import operator
from types import SimpleNamespace

import numpy as np
import pytest
import quantumbridge as qb
from quantumbridge.core.classical import UnsupportedFeature
from quantumbridge.core.gate_limits import GateCircuitLimits, gate_circuit_scope
from quantumbridge.execution import UnifiedResourceLedger as Ledger
from quantumbridge.execution.resource_context import ResourceScope
from quantumbridge.information import Operator
from quantumbridge.ir.qb_ir import IRProgram
from quantumbridge.serialization import qpy_dumps, qpy_loads
from quantumbridge.compat.qiskit_adapter import circuit_from_ir


def test_public_parameter_snapshot_is_mutable_independent_and_not_native_storage():
    p,q=qb.Parameter("p"),qb.Parameter("q")
    circuit=qb.QuantumCircuit(1);circuit.rx(q,0);circuit.rz(p,0)
    original=circuit.to_ir().to_dict();view=circuit.parameters;snapshot=view.copy()
    assert type(view).__name__=="ParameterView" and isinstance(view,MappingView)
    assert view is not circuit.parameters and view.data is not circuit.parameters.data
    assert view.remove(p) is None and list(view)==[q] and list(snapshot)==[p,q]
    view.data.append(p);view.data.reverse();view.data[:]=[q,p,p]
    assert view==[p,q] and view=={p,q} and view==(q,p,p)
    assert circuit.to_ir().to_dict()==original and list(circuit.parameters)==[p,q]
    circuit.assign_parameters({p:.3},inplace=True)
    assert list(view)==[q,p,p] and list(snapshot)==[p,q] and list(circuit.parameters)==[q]
    assert type(qb.Circuit(1).rx(p,0).parameters) is tuple


def test_public_snapshot_sorting_preserves_vector_order_uuid_and_binding_after_local_mutation():
    vector=qb.ParameterVector("v",12);p=qb.Parameter("angle_10");q=qb.Parameter("angle_2")
    circuit=qb.QuantumCircuit(1);circuit.rx(vector[10],0);circuit.ry(p,0);circuit.rz(vector[2],0);circuit.p(q,0)
    view=circuit.parameters
    assert list(view)==[p,q,vector[2],vector[10]]
    assert view[-1].uuid==vector[10].uuid and type(view[1::2]) is list
    view.remove(vector[2]);view.data[0]=vector[0]
    bound=circuit.assign_parameters([.2,.3,.4,.5])
    assert not bound.parameters and list(circuit.parameters)==[p,q,vector[2],vector[10]]
    assert [item.params for item in bound.data]==[[.5],[.2],[.4],[.3]]
    assert len(vector)==12 and vector[10].vector is vector


OPS={"eq":operator.eq,"ne":operator.ne,"lt":operator.lt,"le":operator.le,
     "gt":operator.gt,"ge":operator.ge,"and":operator.and_,"or":operator.or_,
     "xor":operator.xor,"sub":operator.sub}


def api(public):
    if not public:return SimpleNamespace(QC=qb.QuantumCircuit,P=qb.Parameter,PV=qb.ParameterView)
    qiskit=pytest.importorskip("qiskit")
    from qiskit.circuit import Parameter
    from qiskit.circuit.parametertable import ParameterView
    return SimpleNamespace(QC=qiskit.QuantumCircuit,P=Parameter,PV=ParameterView)


def observe_operation(library,action,container,reverse=False,inplace=False):
    p,q,r=(library.P(name) for name in ("p","q","r"))
    view=library.PV([q,p,p]);old_data=view.data
    other={"list":[p,r],"tuple":(p,r),"set":{p,r},"frozenset":frozenset((p,r)),
           "view":library.PV([p,r]),"duplicates":[p,p,q],"empty":[],"integer":3,
           "generator":iter([p,r])}[container]
    try:
        function=getattr(operator,"i"+action) if inplace else OPS[action]
        result=function(other,view) if reverse else function(view,other)
    except Exception as error:return ("error",type(error).__name__,[x.name for x in view],view.data is old_data)
    if isinstance(result,bool):normalized=result
    else:
        normalized=[x.name for x in result]
        if type(result) is set:normalized.sort()
    return ("result",type(result).__name__,normalized,[x.name for x in view],result is view,view.data is old_data)


@pytest.mark.parametrize("action",list(OPS))
@pytest.mark.parametrize("container",["list","tuple","set","frozenset","view","duplicates","empty","integer","generator"])
def test_actual_public_parameter_view_queries_and_algebra_match(action,container):
    public=observe_operation(api(True),action,container)
    assert observe_operation(api(False),action,container)==public


@pytest.mark.parametrize("action",["and","or","xor","sub"])
@pytest.mark.parametrize("mode",["reverse","inplace"])
def test_actual_public_parameter_view_reflected_and_augmented_operators(action,mode):
    def observation(library):return observe_operation(library,action,"set",reverse=mode=="reverse",inplace=mode=="inplace")
    assert observation(api(False))==observation(api(True))


@pytest.mark.parametrize("method",["copy","shallow","deep"])
def test_actual_public_snapshot_copy_method_and_copy_protocol_aliasing(method):
    def observation(library):
        p,q=library.P("p"),library.P("q");view=library.PV([q,p,p])
        other=view.copy() if method=="copy" else copy(view) if method=="shallow" else deepcopy(view)
        old_data=view.data;other.remove(p)
        return (type(other).__name__,[x.name for x in view],[x.name for x in other],other.data is old_data)
    assert observation(api(False))==observation(api(True))


@pytest.mark.parametrize("transport",["direct","ir","qpy"])
@pytest.mark.parametrize("mutation",["remove","replace","intersect","inplace-intersect"])
def test_snapshot_mutation_cannot_change_captured_owner_binding_or_complex_math(transport,mutation):
    p,q=qb.Parameter("p"),qb.Parameter("q")
    body=qb.QuantumCircuit(1,global_phase=q/5);body.rx(2*p+q,0)
    owner=body.to_gate().control(2,ctrl_state="01")
    circuit=qb.QuantumCircuit(3);circuit.append(owner,[0,1,2],copy=False)
    if transport=="ir":circuit=circuit_from_ir(IRProgram.from_json(circuit.to_ir().to_json()))
    elif transport=="qpy":circuit=qpy_loads(qpy_dumps(circuit))[0]
    if transport!="direct":
        restored=circuit;circuit=qb.QuantumCircuit(restored.num_qubits);circuit.compose(restored,inplace=True)
    before=circuit.to_ir().to_dict();view=circuit.parameters;slots=tuple(circuit.data[0].params)
    a,b=view
    if mutation=="remove":view.remove(a)
    elif mutation=="replace":view.data=[b]
    elif mutation=="intersect":view=view&{b}
    else:view&={b}
    assert list(view)==[b] and list(circuit.parameters)==[a,b]
    assert circuit.to_ir().to_dict()==before and tuple(circuit.data[0].params)==slots
    angle=.4+.3;local=np.exp(.06j)*np.array([[np.cos(angle/2),-1j*np.sin(angle/2)],[-1j*np.sin(angle/2),np.cos(angle/2)]])
    expected=np.eye(8,dtype=complex);expected[4:6,4:6]=local
    np.testing.assert_allclose(Operator(circuit.assign_parameters([.2,.3])).data,expected,atol=3e-12,rtol=0)


def test_snapshot_standalone_errors_and_duplicate_intersection_without_an_sdk():
    p,q,r=(qb.Parameter(n) for n in ("p","q","r"));view=qb.ParameterView([q,p,p])
    assert view&{p}==[p] and list(view&{p})==[p,p] and list(view)==[q,p,p]
    old=view;view&={p};assert view is old and list(view)==[p,p]
    assert view.isdisjoint([q,r]) and not view.isdisjoint([p])
    assert [] not in view and p in view
    assert not qb.ParameterView() and not qb.ParameterView(None)
    with pytest.raises(ValueError):view.remove(r)
    with pytest.raises(TypeError):hash(view)
    with pytest.raises(TypeError):qb.ParameterView(0)
    assert type(view[::-1]) is list


def test_snapshot_limits_before_iteration_and_bounded_generator_consumption():
    p=qb.Parameter("p");visited=[]
    def values():
        for index in range(100):visited.append(index);yield p
    with gate_circuit_scope(GateCircuitLimits(max_gate_parameters=2)):
        with pytest.raises(MemoryError):qb.ParameterView(values())
    assert visited==[0,1,2]
    with gate_circuit_scope(GateCircuitLimits(max_gate_parameters=2)):
        with pytest.raises(MemoryError):qb.ParameterView([p,p,p])
    assert list(qb.ParameterView([p]))==[p]


@pytest.mark.parametrize("action",["le","lt","ge","gt","and","iand","isdisjoint"])
def test_unbounded_query_operands_are_bounded_without_changing_snapshot(action):
    p=qb.Parameter("p");q=qb.Parameter("q");view=qb.ParameterView([p]);data=view.data;visited=[]
    def values():
        for index in range(100):visited.append(index);yield q
    with gate_circuit_scope(GateCircuitLimits(max_gate_parameters=2)):
        if action in ("ge","gt"):
            # A matching prefix makes the whole operand relevant to this query.
            def values():
                for index in range(100):visited.append(index);yield p
        with pytest.raises(MemoryError):
            if action=="isdisjoint":view.isdisjoint(values())
            else:(operator.iand if action=="iand" else OPS[action])(view,values())
    assert visited==[0,1,2] and view.data is data and list(view)==[p]


@pytest.mark.parametrize("action",["construct","eq","and","iand","remove","contains","copy","index"])
def test_managed_view_rejects_foreign_callbacks_before_any_mutation(action):
    class Foreign:
        def __iter__(self):pytest.fail("foreign iteration")
        def __len__(self):pytest.fail("foreign length")
        def __eq__(self,other):pytest.fail("foreign equality")
        def __hash__(self):pytest.fail("foreign hash")
        def __index__(self):pytest.fail("foreign index")
        def __deepcopy__(self,memo):pytest.fail("foreign deep copy")
    p=qb.Parameter("p");view=qb.ParameterView([p]);data=view.data;foreign=Foreign()
    with ResourceScope(Ledger()),pytest.raises(UnsupportedFeature):
        if action=="construct":qb.ParameterView(foreign)
        elif action=="eq":view==foreign
        elif action=="and":view&foreign
        elif action=="iand":view&=foreign
        elif action=="remove":view.remove(foreign)
        elif action=="contains":foreign in view
        elif action=="index":view[foreign]
        else:
            view.data.append(foreign)
            try:deepcopy(view)
            finally:view.data.pop()
    assert view.data is data and list(view)==[p]


def test_managed_public_snapshot_remains_native_and_bindable():
    p=qb.Parameter("p");circuit=qb.QuantumCircuit(1);circuit.rx(p,0)
    with ResourceScope(Ledger()):
        view=circuit.parameters
        assert view==[p] and view.isdisjoint(set())
        view&={p};view.remove(p)
        copied=circuit.copy();bound=copied.assign_parameters([.3])
    assert list(circuit.parameters)==[p] and not bound.parameters


def test_public_snapshot_aggregate_parameter_limit_precedes_sort_and_snapshot_allocation(monkeypatch):
    import quantumbridge.core.parameter_view as module
    p,q=qb.Parameter("p"),qb.Parameter("q")
    circuit=qb.QuantumCircuit(1);circuit.rx(p,0);circuit.rz(q,0)
    def forbidden(*args,**kwargs):pytest.fail("snapshot allocation before aggregate parameter admission")
    monkeypatch.setattr(module.ParameterView,"__init__",forbidden)
    with gate_circuit_scope(GateCircuitLimits(max_gate_parameters=1)),pytest.raises(MemoryError):
        circuit.parameters


def test_managed_public_snapshot_admits_raw_execution_keys_before_lookup_callbacks():
    class ForeignKey:
        def __hash__(self):return hash("control_node")
        def __eq__(self,other):pytest.fail("foreign execution-key equality before admission")
    p=qb.Parameter("p");circuit=qb.QuantumCircuit(1);circuit.rx(p,0)
    key=ForeignKey();circuit.operations[0].metadata[key]=None
    with ResourceScope(Ledger()),pytest.raises(UnsupportedFeature):circuit.parameters
    del circuit.operations[0].metadata[key]
    assert list(circuit.parameters)==[p]


def test_sdkfree_public_snapshot_algebra_and_formal_binding_plan_are_independent():
    p,q,r=(qb.Parameter(name) for name in ("p","q","r"))
    view=qb.ParameterView([q,p,p])
    assert view==[p,q] and view<={p,q,r} and view<{p,q,r}
    assert view>={p} and view>{p} and view!={p,r}
    assert type(view|{r}) is set and view|{r}=={p,q,r}
    assert view^{p,r}=={q,r} and view-{p}=={q}
    assert list(view)==[q,p,p]
    circuit=qb.QuantumCircuit(1);circuit.rx(p,0)
    snapshot=circuit.parameters
    instruction=circuit.to_instruction(parameter_map={p:q})
    assert type(instruction._parameter_plan.formals) is tuple
    snapshot.remove(p)
    instruction.params=[.4];instruction.params=[.7]
    np.testing.assert_allclose(Operator(instruction.definition).data,
        np.array([[np.cos(.35),-1j*np.sin(.35)],[-1j*np.sin(.35),np.cos(.35)]]),atol=2e-13,rtol=0)
    assert list(circuit.parameters)==[p]


@pytest.mark.parametrize("method",["parameter-shift","adjoint"])
@pytest.mark.parametrize("transport",["direct","ir","qpy"])
def test_snapshot_local_mutation_does_not_change_real_derivative_parameter_order(method,transport):
    from quantumbridge.qml import QNode
    p=qb.Parameter("p");body=qb.QuantumCircuit(1,global_phase=p/5);body.rx(2*p,0)
    circuit=qb.QuantumCircuit(3);circuit.h(0);circuit.append(body.to_gate().control(2,ctrl_state="01"),[0,1,2])
    if transport=="ir":restored=circuit_from_ir(IRProgram.from_json(circuit.to_ir().to_json()))
    elif transport=="qpy":restored=qpy_loads(qpy_dumps(circuit))[0]
    else:restored=circuit
    if transport!="direct":
        circuit=qb.QuantumCircuit(3);circuit.compose(restored,inplace=True)
    view=circuit.parameters;view.remove(view[0]);view.data.append(qb.Parameter("unrelated"))
    node=QNode.from_circuit(circuit,qb.PauliX(0),diff_method=method,max_diff=2)
    x=.31;second=-1.04*np.cos(x)*np.cos(x/5)+.4*np.sin(x)*np.sin(x/5)
    np.testing.assert_allclose(node(x),np.cos(x)*np.cos(x/5),atol=3e-12,rtol=0)
    np.testing.assert_allclose(node.compute_jacobian(x),-np.sin(x)*np.cos(x/5)-.2*np.cos(x)*np.sin(x/5),atol=5e-10,rtol=0)
    np.testing.assert_allclose(node.compute_hessian(x),second,atol=8e-10,rtol=0)
    np.testing.assert_allclose(node.compute_hvp(.7,x),.7*second,atol=8e-10,rtol=0)
