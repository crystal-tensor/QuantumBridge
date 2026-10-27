# Copyright 2026 QuantumBridge Contributors.
# Licensed under the Apache License, Version 2.0.
"""Public calls in each installed SDK, never upstream execution for native math."""
from types import SimpleNamespace
import numpy as np
import pytest
import quantumbridge as qb
from quantumbridge.core import standard_gates as native_gates


def apis():
    pytest.importorskip("qiskit")
    from qiskit import QuantumCircuit,QuantumRegister,ClassicalRegister
    from qiskit.circuit import Qubit,Clbit,Instruction,CircuitInstruction,InstructionSet,Parameter
    from qiskit.circuit.library import XGate,ZGate,RYGate,CXGate
    native=SimpleNamespace(QC=qb.QuantumCircuit,QR=qb.QuantumRegister,CR=qb.ClassicalRegister,
        Qubit=qb.Qubit,Clbit=qb.Clbit,Instruction=qb.Instruction,CI=qb.CircuitInstruction,IS=qb.InstructionSet,
        Parameter=qb.Parameter,XGate=native_gates.XGate,ZGate=native_gates.ZGate,RYGate=native_gates.RYGate,CXGate=native_gates.CXGate)
    public=SimpleNamespace(QC=QuantumCircuit,QR=QuantumRegister,CR=ClassicalRegister,Qubit=Qubit,Clbit=Clbit,
        Instruction=Instruction,CI=CircuitInstruction,IS=InstructionSet,Parameter=Parameter,
        XGate=XGate,ZGate=ZGate,RYGate=RYGate,CXGate=CXGate)
    return native,public


def outcome(call):
    try:return ("value",call())
    except Exception as error:return ("error",type(error).__name__)


def describe(c):
    return (type(c).__name__,c.num_qubits,c.num_clbits,[(r.name,len(r)) for r in c.qregs+c.cregs],
        str(c.global_phase),[(x.operation.name,[c.find_bit(b).index for b in x.qubits],
            [c.find_bit(b).index for b in x.clbits],tuple(str(p) for p in x.operation.params)) for x in c.data])


@pytest.mark.parametrize("symbolic",[False,True])
@pytest.mark.parametrize("action",["copy","bind","inverse","handle-inverse","compose","compose-copy"])
def test_actual_public_cached_invocation_and_mutable_display_owner_are_distinct(symbolic,action):
    native,public=apis()
    def call(a):
        p=a.Parameter("p");gate=a.RYGate(p if symbolic else .3)
        circuit=a.QC(1);handle=circuit.append(gate,[0],copy=False);gate.params[0]=.7
        if action=="copy":out=circuit.copy()
        elif action=="bind":out=circuit.assign_parameters({p:.4} if symbolic else {})
        elif action=="inverse":out=circuit.inverse()
        elif action in {"compose","compose-copy"}:out=a.QC(1).compose(circuit,copy=action=="compose-copy")
        else:handle.inverse();out=circuit
        return (type(out).__name__,tuple(str(x) for x in out.data[0].params),
            tuple(str(x) for x in out.data[0].operation.params),out.data[0].operation is gate,
            tuple(x.name for x in out.parameters))
    assert outcome(lambda:call(native))==outcome(lambda:call(public))


@pytest.mark.parametrize("case",["empty","zero","classical","int","ints","regs","three-regs","bits-bare",
    "bits-list","bits-two-lists","mixed-reg-list","mixed-int-reg","negative","float","fractional","three-ints",
    "bool","numpy","name-int","name-empty","negative-phase","metadata","metadata-list","phase-string","duplicate-bits"])
def test_actual_public_constructor_types_and_errors(case):
    native,public=apis()
    def call(a):
        q=a.QR(2,"q");c=a.CR(2,"c");q0,q1=a.Qubit(),a.Qubit();bit=a.Clbit()
        choices={"empty":lambda:a.QC(),"zero":lambda:a.QC(0),"classical":lambda:a.QC(0,2),"int":lambda:a.QC(2),
            "ints":lambda:a.QC(2,1),"regs":lambda:a.QC(q,c),"three-regs":lambda:a.QC(q,c,a.QR(1,"extra")),
            "bits-bare":lambda:a.QC(q0,q1),"bits-list":lambda:a.QC([q0,q1]),"bits-two-lists":lambda:a.QC([q0,q1],[bit]),
            "mixed-reg-list":lambda:a.QC(q,[bit]),"mixed-int-reg":lambda:a.QC(2,q),"negative":lambda:a.QC(-1),
            "float":lambda:a.QC(1.0),"fractional":lambda:a.QC(1.5),"three-ints":lambda:a.QC(1,2,3),"bool":lambda:a.QC(True),
            "numpy":lambda:a.QC(np.int64(2)),"name-int":lambda:a.QC(1,name=7),"name-empty":lambda:a.QC(1,name=""),
            "negative-phase":lambda:a.QC(1,global_phase=-.2),"metadata":lambda:a.QC(1,metadata={"test":True}),
            "metadata-list":lambda:a.QC(1,metadata=[]),"phase-string":lambda:a.QC(1,global_phase="x"),
            "duplicate-bits":lambda:a.QC([q0,q0])}
        circuit=choices[case]()
        return describe(circuit),circuit.name if case=="name-empty" else None
    assert outcome(lambda:call(native))==outcome(lambda:call(public))


@pytest.mark.parametrize("case",["properties","copy","replace","replace-none","set-operation","set-qubits","bad-width",
    "integer-operands","none-operands","sequence"])
def test_actual_public_circuitinstruction_context_is_read_only_not_a_store_pointer(case):
    native,public=apis()
    def call(a):
        q=a.Qubit();ci=a.CI(a.RYGate(.3),[q],[])
        if case=="properties":return ci.name,tuple(ci.params),ci.is_control_flow(),ci.is_standard_gate()
        if case=="copy":
            peer=ci.copy();return peer is ci,peer.operation is ci.operation,peer==ci
        if case=="replace":
            peer=ci.replace(operation=a.XGate());return ci.name,peer.name,peer is ci
        if case=="replace-none":return ci.replace(operation=None).operation is ci.operation
        if case=="set-operation":ci.operation=a.XGate();return None
        if case=="set-qubits":ci.qubits=();return None
        if case=="bad-width":return len(a.CI(a.CXGate(),[q],[]).qubits)
        if case=="integer-operands":return a.CI(a.XGate(),[0],[]).qubits
        if case=="none-operands":return a.CI(a.XGate()).qubits,a.CI(a.XGate()).clbits
        return len(ci),ci[0].name,type(ci[1]).__name__,type(ci[2]).__name__
    assert outcome(lambda:call(native))==outcome(lambda:call(public))


@pytest.mark.parametrize("case",["context-not-live","setitem","tuple-setitem","append","insert","pop","clear",
    "slice-replace","delitem","assign","foreign-bit","wrong-width","integer-bit","mutable-operation"])
def test_actual_public_data_mutation_contract(case):
    native,public=apis()
    def call(a):
        c=a.QC(2,1);c.x(0);c.h(1);snapshot=c.data[0];replacement=snapshot.replace(operation=a.ZGate())
        if case=="context-not-live":return snapshot.name,replacement.name,c.data[0].name
        if case=="setitem":c.data[0]=replacement
        elif case=="tuple-setitem":c.data[0]=(a.ZGate(),[c.qubits[0]],[])
        elif case=="append":c.data.append(a.CI(a.XGate(),[c.qubits[1]],[]))
        elif case=="insert":c.data.insert(0,replacement)
        elif case=="pop":return c.data.pop().name,describe(c)
        elif case=="clear":c.data.clear()
        elif case=="slice-replace":c.data[0:2]=[replacement]
        elif case=="delitem":del c.data[0]
        elif case=="assign":c.data=[replacement]
        elif case=="foreign-bit":c.data[0]=a.CI(a.XGate(),[a.Qubit()],[])
        elif case=="wrong-width":c.data[0]=a.CI(a.CXGate(),[c.qubits[0]],[])
        elif case=="integer-bit":c.data[0]=a.CI(a.XGate(),[1],[])
        elif case=="mutable-operation":
            c=a.QC(1);g=a.RYGate(.3);c.append(g,[0]);c.data[0].operation.params[0]=.7
            return c.data[0].operation is g,tuple(c.data[0].params)
        return describe(c)
    assert outcome(lambda:call(native))==outcome(lambda:call(public))


@pytest.mark.parametrize("name",["id","x","y","z","h","s","sdg","t","tdg","sx","sxdg","rx","ry","rz","p","u",
    "cx","cy","cz","swap","crx","cry","crz","cp","ccx","ccz","rxx","ryy","rzz","measure","reset","barrier","delay"])
@pytest.mark.parametrize("mode",["scalar","broadcast"])
def test_actual_public_builder_return_contexts_and_broadcasting(name,mode):
    native,public=apis()
    def call(a):
        c=a.QC(3,3)
        params={"rx":[.3],"ry":[.3],"rz":[.3],"p":[.3],"u":[.3,.2,.1],"crx":[.3],"cry":[.3],
            "crz":[.3],"cp":[.3],"rxx":[.3],"ryy":[.3],"rzz":[.3]}.get(name,[])
        if name=="measure":args=([0,1],[1,0]) if mode=="broadcast" else (0,1)
        elif name=="barrier":args=([0,2],) if mode=="broadcast" else (0,)
        elif name=="delay":args=(3,[0,1]) if mode=="broadcast" else (3,0)
        elif name in ("cx","cy","cz","swap","crx","cry","crz","cp","rxx","ryy","rzz"):
            args=(*params,[0,1],2) if mode=="broadcast" else (*params,0,2)
        elif name in ("ccx","ccz"):args=(0,1,2)
        else:args=(*params,[0,2]) if mode=="broadcast" else (*params,0)
        handle=getattr(c,name)(*args)
        return type(handle).__name__,len(handle),describe(c)
    assert outcome(lambda:call(native))==outcome(lambda:call(public))


@pytest.mark.parametrize("case",["empty","plain","tuple1","tuple2","tuple3","ci"])
def test_actual_public_from_instructions_staging_and_ownership(case):
    native,public=apis()
    def call(a):
        bit=a.Qubit();gate=a.RYGate(.3)
        choices={"empty":[],"plain":[gate],"tuple1":[(gate,)],"tuple2":[(gate,[bit])],"tuple3":[(gate,[bit],[])],
            "ci":[a.CI(gate,[bit],[])]}
        c=a.QC.from_instructions(choices[case])
        return describe(c),bool(c.data) and c.data[0].operation is gate
    assert outcome(lambda:call(native))==outcome(lambda:call(public))


@pytest.mark.parametrize("symbolic",[False,True])
@pytest.mark.parametrize("copy",[False,True])
def test_actual_direct_append_copy_only_copies_parameterized_owners(symbolic,copy):
    native,public=apis()
    def call(a):
        c=a.QC(1);gate=a.RYGate(a.Parameter("p") if symbolic else .3)
        handle=c.append(gate,[0],copy=copy);before=c.data[0].operation is gate;gate.params[0]=.7
        return before,tuple(str(p) for p in c.data[0].params),tuple(str(p) for p in handle.instructions[0].params)
    assert outcome(lambda:call(native))==outcome(lambda:call(public))


@pytest.mark.parametrize("case",["inverse","replace-current-slot","clear","copy","empty","add-context","add-operation"])
def test_actual_instructionset_current_slot_modification_and_lifetimes(case):
    native,public=apis()
    def call(a):
        c=a.QC(2);handle=c.ry(.3,[0,1])
        if case=="inverse":return handle.inverse() is handle,[tuple(ctx.params) for ctx in c.data]
        if case=="replace-current-slot":c.data[0]=c.data[0].replace(operation=a.XGate());handle.inverse();return describe(c)
        if case=="clear":c.data.clear();handle.inverse();return None
        if case=="copy":
            copied=c.copy();handle.inverse();return describe(c),describe(copied)
        if case=="empty":
            handle=a.IS();return len(handle),handle.instructions,handle.qargs,handle.cargs,handle.inverse() is handle
        if case=="add-context":
            handle=a.IS();ci=a.CI(a.RYGate(.3),[a.Qubit()],[]);answer=handle.add(ci)
            return answer is None,len(handle),handle[0]==ci
        handle=a.IS();answer=handle.add(a.RYGate(.3),[0],[]);return answer is None,len(handle),handle.qargs
    assert outcome(lambda:call(native))==outcome(lambda:call(public))
