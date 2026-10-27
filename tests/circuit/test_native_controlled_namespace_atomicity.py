# Copyright 2026 QuantumBridge Contributors.
# Licensed under the Apache License, Version 2.0.
"""Controlled frames keep UUID namespaces and atomic native error boundaries."""
from types import SimpleNamespace
import numpy as np
import pytest
import quantumbridge as qb
from quantumbridge.core.instruction_parameters import definition_signature
from quantumbridge.information import Operator
from quantumbridge.serialization import qpy_dumps,qpy_loads
from quantumbridge.ir.qb_ir import IRProgram
from quantumbridge.compat.qiskit_adapter import circuit_from_ir


def collision(api,action):
    p,q=api.P("shared"),api.P("shared")
    first=api.QC(1);first.rx(p,0)
    owner=first.to_gate().control(2,ctrl_state=1,annotated=False)
    source=api.QC(4);source.append(owner,[0,1,2],copy=False);source.rz(p,3)
    second=api.QC(1);second.ry(q,0)
    replacement=second.to_gate().control(2,ctrl_state=1,annotated=False)
    def apply():
        if action=="append":source.append(replacement,[0,1,2],copy=False)
        elif action=="compose":
            peer=api.QC(3);peer.append(replacement,[0,1,2]);source.compose(peer,[0,1,2],inplace=True,copy=False)
        else:source.data[0]=source.data[0].replace(operation=replacement)
    return source,owner,replacement,p,apply


@pytest.mark.parametrize("action",["append","compose","data"])
def test_native_same_name_distinct_uuid_collision_keeps_entire_controlled_frame_and_owner_unchanged(action):
    source,owner,replacement,p,apply=collision(SimpleNamespace(QC=qb.QuantumCircuit,P=qb.Parameter),action)
    before=source.to_ir().to_dict();definition=owner.definition;plan=owner._parameter_plan
    slots=tuple(source.data[0].params);other=definition_signature(replacement.definition)
    with pytest.raises(ValueError,match="Conflicting identities"):apply()
    assert source.to_ir().to_dict()==before and source.parameters==(p,)
    assert owner.definition is definition and owner._parameter_plan is plan and tuple(source.data[0].params)==slots
    assert definition_signature(replacement.definition)==other
    assert not source.assign_parameters({p:.37}).parameters


@pytest.mark.parametrize("action",["append","compose","data"])
def test_actual_public_collision_error_is_nonatomic_not_a_native_match(action,record_property):
    public=pytest.importorskip("qiskit")
    from qiskit.circuit import Parameter
    from qiskit.circuit.exceptions import CircuitError
    source,owner,_,p,apply=collision(SimpleNamespace(QC=public.QuantumCircuit,P=Parameter),action)
    before=tuple((item.operation.name,tuple(item.operation.params)) for item in source.data)
    with pytest.raises(CircuitError,match="name conflict"):apply()
    assert tuple(source.parameters)==(p,)
    assert tuple((item.operation.name,tuple(item.operation.params)) for item in source.data)!=before
    record_property("contract","INTENTIONAL_DIFFERENCE: native atomic refusal; observed upstream mutated failed operation")


@pytest.mark.parametrize("transport",["direct","ir","qpy"])
def test_vector_parameters_shared_across_controlled_definitions_survive_partial_binding_and_decode(transport):
    vector=qb.ParameterVector("v",2);p,q=vector
    leaf=qb.QuantumCircuit(1,global_phase=q/5);leaf.rx(2*p+3*q,0)
    controlled=leaf.to_gate().control(2,ctrl_state="01")
    source=qb.QuantumCircuit(3);source.append(controlled,[0,1,2],copy=False)
    peer=qb.QuantumCircuit(1);peer.rz(q,0);source.append(peer.to_gate(),[2])
    partial=source.assign_parameters({p:.2})
    assert partial.parameters==(q,) and source.parameters==(p,q)
    exposed=partial.data[0].operation
    changed=qb.QuantumCircuit(1);changed.ry(7*q,0);exposed.base_gate.definition=changed
    if transport=="ir":partial=circuit_from_ir(IRProgram.from_json(partial.to_ir().to_json()))
    elif transport=="qpy":partial=qpy_loads(qpy_dumps(partial))[0]
    assert len(partial.parameters)==1 and partial.parameters[0].uuid==q.uuid
    assert partial.parameters[0].vector._root_uuid==q.vector._root_uuid
    x=.37;angle=.4+3*x
    local=np.exp(1j*x/5)*np.array([[np.cos(angle/2),-1j*np.sin(angle/2)],[-1j*np.sin(angle/2),np.cos(angle/2)]])
    expected=np.eye(8,dtype=complex);expected[4:6,4:6]=local
    rz=np.diag([np.exp(-.5j*x),np.exp(.5j*x)])
    expected=np.kron(np.eye(4),rz)@expected
    bound=partial.assign_parameters({partial.parameters[0]:x})
    assert not bound.parameters
    np.testing.assert_allclose(Operator(bound).data,expected,atol=3e-12,rtol=0)


def test_conflicting_repeated_formal_values_do_not_change_definition_slots_or_binding_plan():
    p=qb.Parameter("p");body=qb.QuantumCircuit(1);body.rx(p,0)
    owner=qb.Gate("repeated",1,[p,p],definition=body)
    source=qb.QuantumCircuit(1);source.append(owner,[0],copy=False)
    before=source.to_ir().to_dict();definition=owner.definition;plan=owner._parameter_plan
    with pytest.raises(ValueError,match="Repeated formal"):owner.params=[.2,.4]
    assert source.to_ir().to_dict()==before and owner.definition is definition and owner._parameter_plan is plan
    assert owner.params==[p,p] and source.parameters==(p,)
