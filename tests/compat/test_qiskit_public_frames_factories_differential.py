# Copyright 2026 QuantumBridge Contributors.
# Licensed under the Apache License, Version 2.0.
"""Actual public owner/context fields, independent of SDK implementation code."""
from types import SimpleNamespace
import numpy as np
import pytest
import quantumbridge as qb


def apis():
    pytest.importorskip("qiskit")
    from qiskit import QuantumCircuit
    from qiskit.circuit import Gate,Instruction,Parameter,CircuitInstruction,Qubit
    from qiskit.circuit.library import UnitaryGate
    from quantumbridge.circuit_library import UnitaryGate as NativeUnitary
    return (SimpleNamespace(QC=qb.QuantumCircuit,Gate=qb.Gate,Instruction=qb.Instruction,
        Parameter=qb.Parameter,CI=qb.CircuitInstruction,Qubit=qb.Qubit,Unitary=NativeUnitary),
        SimpleNamespace(QC=QuantumCircuit,Gate=Gate,Instruction=Instruction,Parameter=Parameter,CI=CircuitInstruction,Qubit=Qubit,Unitary=UnitaryGate))


def fields(context):
    owner=context.operation
    return (context.name,tuple(str(x) for x in context.params),owner.name,
        tuple(str(x) for x in owner.params),owner.label,owner.base_class.__name__,owner.mutable)


def operation(a,kind,value):
    return a.Gate("custom",1,[value],"old") if kind=="gate" else a.Instruction("custom_i",1,0,[value],"old")


@pytest.mark.parametrize("kind",["gate","instruction"])
@pytest.mark.parametrize("symbolic",[False,True])
@pytest.mark.parametrize("copy",[False,True])
@pytest.mark.parametrize("action",["identity","copy","bind","context-copy","context-replace","context-assign"])
def test_generic_cached_context_and_exposed_owner_have_measured_independent_fields(kind,symbolic,copy,action):
    native,public=apis()
    def call(a):
        p=a.Parameter("p");g=operation(a,kind,p if symbolic else .25)
        c=a.QC(1);handle=c.append(g,[0],copy=copy);before=c.data[0]
        g.name="changed";g.params[0]=.7;g.label="new"
        if action=="copy":c=c.copy()
        elif action=="bind":c=c.assign_parameters({p:.4} if symbolic else {})
        elif action=="context-copy":return fields(before.copy()),fields(c.data[0])
        elif action=="context-replace":return fields(before.replace()),fields(c.data[0])
        elif action=="context-assign":c.data[0]=before.replace()
        return (fields(c.data[0]),tuple(x.name for x in c.parameters),fields(before),
            c.data[0].operation is g,type(handle).__name__,len(handle))
    assert call(native)==call(public)


@pytest.mark.parametrize("kind",["gate","instruction"])
@pytest.mark.parametrize("mutation",["params","name","label"])
def test_standalone_context_equality_compares_captured_fields_not_only_operation_identity(kind,mutation):
    native,public=apis()
    def call(a):
        q=a.Qubit();g=operation(a,kind,.25);ci=a.CI(g,[q],[])
        if mutation=="params":g.params[0]=.7
        elif mutation=="name":g.name="changed"
        else:g.label="new"
        peer=a.CI(g,[q],[])
        return ci==peer,ci==ci.copy(),ci==ci.replace(),fields(ci),fields(peer)
    assert call(native)==call(public)


@pytest.mark.parametrize("width",[0,1,2])
@pytest.mark.parametrize("action",["standalone","append","copy","replace","reinsert"])
def test_actual_public_matrix_owner_is_not_a_scalar_standard_context(width,action):
    native,public=apis()
    def call(a):
        bits=[a.Qubit() for _ in range(width)]
        gate=a.Unitary(np.exp(.2j)*np.eye(1<<width));context=a.CI(gate,bits,[])
        if action in {"append","reinsert"}:
            c=a.QC(bits);c.append(gate,bits,copy=False)
            if action=="reinsert":c.data[0]=c.data[0].replace()
            context=c.data[0]
        elif action=="copy":context=context.copy()
        elif action=="replace":context=context.replace()
        return (context.name,context.params,context.is_standard_gate(),
            context.operation is gate,context.operation.num_qubits,len(context.operation.params))
    assert call(native)==call(public)


@pytest.mark.parametrize("width",[0,1,2])
@pytest.mark.parametrize("peer",["equal","label","phase","same-owner"])
def test_actual_public_matrix_context_equality_uses_the_owned_numeric_matrix(width,peer):
    native,public=apis()
    def call(a):
        bits=[a.Qubit() for _ in range(width)];gate=a.Unitary(np.eye(1<<width))
        other=gate if peer=="same-owner" else a.Unitary(
            np.exp(.2j)*np.eye(1<<width) if peer=="phase" else np.eye(1<<width),
            label="different" if peer=="label" else None)
        first=a.CI(gate,bits,[]);second=a.CI(other,bits,[])
        return first==second,first==first.copy(),first==first.replace()
    assert call(native)==call(public)


@pytest.mark.parametrize("kind",["gate","instruction"])
@pytest.mark.parametrize("reps",[0,1,2])
@pytest.mark.parametrize("selection",["all","name","label","pattern","type","mixed","unselected"])
def test_actual_public_decomposition_layers_selectors_and_stored_contexts(kind,reps,selection):
    native,public=apis()
    def call(a):
        p=a.Parameter("p");leaf=a.QC(1,name="leaf",global_phase=.1);leaf.ry(p,0)
        middle=a.QC(1,name="outer",global_phase=.3)
        middle.append(getattr(leaf,"to_"+kind)(label="inner"),[0])
        c=a.QC(3,global_phase=.2);c.append(getattr(middle,"to_"+kind)(label="chosen"),[2])
        selector={"all":None,"name":"outer","label":"chosen","pattern":"out*",
            "type":a.Gate if kind=="gate" else a.Instruction,"mixed":["chosen","leaf"],"unselected":"absent"}[selection]
        out=c.decompose(selector,reps=reps)
        return (type(out).__name__,round(float(out.global_phase),12),tuple(p.name for p in out.parameters),
            [(x.name,x.operation.base_class.__name__,x.operation.label,tuple(str(p) for p in x.params),
                tuple(out.find_bit(bit).index for bit in x.qubits)) for x in out.data],
            out.data[0].operation is c.data[0].operation,c.data[0].name,round(float(c.global_phase),12))
    assert call(native)==call(public)
