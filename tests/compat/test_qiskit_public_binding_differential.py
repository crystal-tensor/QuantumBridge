# Copyright 2026 QuantumBridge Contributors.
# Licensed under the Apache License, Version 2.0.
"""Actual public binding/query calls, not upstream implementation inspection."""
from types import SimpleNamespace
import numpy as np
import pytest
import quantumbridge as qb


def apis():
    pytest.importorskip("qiskit")
    from qiskit import QuantumCircuit,QuantumRegister,ClassicalRegister
    from qiskit.circuit import Parameter,ParameterVector,Qubit
    return (SimpleNamespace(QC=qb.QuantumCircuit,P=qb.Parameter,V=qb.ParameterVector,
        QR=qb.QuantumRegister,CR=qb.ClassicalRegister,Qubit=qb.Qubit),
        SimpleNamespace(QC=QuantumCircuit,P=Parameter,V=ParameterVector,QR=QuantumRegister,CR=ClassicalRegister,Qubit=Qubit))


BIND_CASES=("parameter","string","vector","sequence","tuple","array","generator",
    "flat-parameter","flat-string","flat-string-extra","flat-vector","flat-vector-extra","flat-sequence",
    "unknown","unknown-extra","unknown-string","unknown-string-extra","same-name","same-name-extra",
    "vector-length","sequence-length","duplicate","duplicate-reverse","symbolic","phase","nested")


def binding_outcome(a,case,inplace=False):
    p=a.P("p");v=a.V("v",2);unknown=a.P("unknown");other=a.P("p")
    c=a.QC(1,name="source");c.ry(p,0);c.rz(v[0],0);c.global_phase=v[1]/5
    if case=="nested":
        body=a.QC(1,name="inner");body.ry(p,0)
        c=a.QC(1,name="source");c.append(body.to_gate(),[0])
    strict=not case.endswith("-extra");flat=case.startswith("flat-")
    values={"parameter":{p:.2},"string":{"p":.2},"vector":{v:[.3,.4]},
        "sequence":[.2,.3,.4],"tuple":(.2,.3,.4),"array":np.array([.2,.3,.4]),
        "generator":(x for x in [.2,.3,.4]),"flat-parameter":{p:.2},"flat-string":{"p":.2},
        "flat-string-extra":{"p":.2},"flat-vector":{v:[.3,.4]},"flat-vector-extra":{v:[.3,.4]},
        "flat-sequence":[.2,.3,.4],"unknown":{unknown:.2},"unknown-extra":{unknown:.2},
        "unknown-string":{"unknown":.2},"unknown-string-extra":{"unknown":.2},
        "same-name":{other:.2},"same-name-extra":{other:.2},"vector-length":{v:[.3]},
        "sequence-length":[.2],"duplicate":{p:.2,"p":.6},"duplicate-reverse":{"p":.6,p:.2},
        "symbolic":{p:a.P("replacement")},"phase":{v[1]:.4},"nested":{p:.2}}[case]
    try:
        out=c.assign_parameters(values,inplace=inplace,flat_input=flat,strict=strict)
        result=c if inplace else out
        phase=result.global_phase
        return ("value",out is None,type(result).__name__,result.name=="source" if inplace else result.name.startswith("source-"),
            tuple(x.name for x in result.parameters),bool(getattr(phase,"parameters",())),
            None if getattr(phase,"parameters",()) else round(float(phase),12),
            [(x.name,tuple(str(p) for p in x.params)) for x in result.data],
            tuple(x.name for x in c.parameters))
    except Exception as error:return ("error",type(error).__name__)


QUERY_CASES=("get","get-vector","missing","default-none","default-value","default-ellipsis",
    "get-object","get-int","get-list","has-name","has-vector-name","has-object","has-same-name-uuid",
    "has-missing","has-int","has-list")


def query_outcome(a,case):
    p=a.P("p");v=a.V("v",1);c=a.QC(1);c.ry(p,0);c.rz(v[0],0)
    calls={"get":lambda:c.get_parameter("p"),"get-vector":lambda:c.get_parameter("v[0]"),
        "missing":lambda:c.get_parameter("absent"),"default-none":lambda:c.get_parameter("absent",None),
        "default-value":lambda:c.get_parameter("absent",7),"default-ellipsis":lambda:c.get_parameter("absent",...),
        "get-object":lambda:c.get_parameter(p),"get-int":lambda:c.get_parameter(1),"get-list":lambda:c.get_parameter([]),
        "has-name":lambda:c.has_parameter("p"),"has-vector-name":lambda:c.has_parameter("v[0]"),
        "has-object":lambda:c.has_parameter(p),"has-same-name-uuid":lambda:c.has_parameter(a.P("p")),
        "has-missing":lambda:c.has_parameter("absent"),"has-int":lambda:c.has_parameter(1),"has-list":lambda:c.has_parameter([])}
    try:
        result=calls[case]()
        return ("value",result.name if hasattr(result,"name") else result,result is p,result is v[0])
    except Exception as error:return ("error",type(error).__name__)


@pytest.mark.parametrize("case",BIND_CASES)
@pytest.mark.parametrize("inplace",[False,True])
def test_actual_public_parameter_binding_inputs_errors_and_real_return(case,inplace):
    native,public=apis()
    assert binding_outcome(native,case,inplace)==binding_outcome(public,case,inplace)


@pytest.mark.parametrize("case",QUERY_CASES)
def test_actual_public_parameter_queries_use_names_and_parameter_identity(case):
    native,public=apis()
    assert query_outcome(native,case)==query_outcome(public,case)


@pytest.mark.parametrize("kind",["gate","instruction"])
@pytest.mark.parametrize("graph",["named","alias","loose","zero","classical","measured"])
@pytest.mark.parametrize("mapping_kind",["none","full","partial"])
def test_actual_public_conversion_register_formal_phase_contract_metadata_is_separate(kind,graph,mapping_kind,record_property):
    native,public=apis()
    def call(a):
        p=a.P("p");q=a.P("q");r=a.QR(3,"data")
        c=a.QC([a.Qubit() for _ in range(3)],name="source") if graph=="loose" else a.QC(r,name="source")
        if graph=="alias":c.add_register(a.QR(name="alias",bits=[r[1]]))
        if graph=="zero":c=a.QC(name="source")
        if graph=="classical":c=a.QC(a.CR(2,"readout"),name="source")
        if c.num_qubits:c.ry(p,c.qubits[-1])
        if graph=="measured":c.add_register(a.CR(2,"readout"));c.measure(2,1)
        c.global_phase=q/5
        params=tuple(c.parameters)
        mapping=None if mapping_kind=="none" else {param:.2+.1*i for i,param in enumerate(params)}
        if mapping_kind=="partial":mapping={}
        try:
            owner=getattr(c,"to_"+kind)(parameter_map=mapping,label="shown");body=owner.definition
            phase=body.global_phase
            return ("value",type(owner).__name__,owner.name,owner.label,tuple(str(p) for p in owner.params),
                type(body).__name__,body.name,[(r.name,len(r)) for r in body.qregs+body.cregs],
                tuple(p.name for p in body.parameters),bool(getattr(phase,"parameters",())),
                None if getattr(phase,"parameters",()) else round(float(phase),12),
                [(item.name,tuple(body.find_bit(bit).index for bit in item.qubits),
                    tuple(body.find_bit(bit).index for bit in item.clbits)) for item in body.data],
                bool(body.qubits and c.qubits and body.qubits[0]==c.qubits[0]),
                [(r.name,len(r)) for r in c.qregs+c.cregs])
        except Exception as error:return ("error",type(error).__name__)
    actual,reference=call(native),call(public)
    if kind=="instruction" and mapping_kind=="full" and reference[0]=="value" and reference[8]==("q",):
        # Public2.4 leaves a mapped phase symbolic; public2.6 fixes it. Preserve
        # native executable binding rather than imitating this upstream error.
        record_property("compatibility","INTENTIONAL_SAFETY_DIFFERENCE")
        assert reference[8:11]==(("q",),True,None)
        assert actual[:8]==reference[:8] and actual[11:]==reference[11:]
        assert actual[8:11]==((),False,.04 if graph in {"zero","classical"} else .06)
    else:
        record_property("compatibility","MATCH")
        assert actual==reference


def test_public_instruction_map_phase_inconsistency_is_observed_not_copied(record_property):
    native,public=apis()
    from qiskit.quantum_info import Operator as PublicOperator
    from quantumbridge.information import Operator
    expected=np.exp(.06j)*np.array([[np.cos(.1),-np.sin(.1)],[np.sin(.1),np.cos(.1)]])
    for a,operator in ((native,Operator),(public,PublicOperator)):
        p=a.P("p");q=a.P("q");source=a.QC(1,name="source",global_phase=q/5);source.ry(p,0)
        owner=source.to_instruction(parameter_map={p:.2,q:.3})
        if a is public and owner.definition.parameters:
            record_property("public_result","UPSTREAM_ERROR")
            assert tuple(x.name for x in owner.definition.parameters)==("q",)
            with pytest.raises(TypeError):operator(owner)
        else:
            record_property("native_result" if a is native else "public_result","MATCH")
            assert not owner.definition.parameters
            np.testing.assert_allclose(operator(owner).data,expected,atol=5e-13,rtol=0)
