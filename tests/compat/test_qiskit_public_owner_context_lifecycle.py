# Copyright 2026 QuantumBridge Contributors.
# Licensed under the Apache License, Version 2.0.
"""Live generic/controlled/annotated context observations in installed SDKs."""
from types import SimpleNamespace
import numpy as np
import pytest
import quantumbridge as qb


def apis():
    public=pytest.importorskip("qiskit")
    from qiskit.circuit import AnnotatedOperation,ControlModifier,Parameter
    return (SimpleNamespace(QC=qb.QuantumCircuit,P=qb.Parameter,A=qb.AnnotatedOperation,C=qb.ControlModifier),
        SimpleNamespace(QC=public.QuantumCircuit,P=Parameter,A=AnnotatedOperation,C=ControlModifier))


def build(a,kind,symbolic):
    p=a.P("p");body=a.QC(1,name="body",global_phase=p/5);body.ry(2*p,0)
    base=getattr(body,"to_instruction" if kind=="instruction" else "to_gate")(
        parameter_map=None if symbolic else {p:.25})
    source=base.control(annotated=False,ctrl_state=0) if kind=="controlled" else a.A(base,a.C(1,0)) if kind=="annotated" else base
    return source,base,p


def fields(context):
    owner=context.operation
    return (context.name,tuple(str(x) for x in context.params),owner.name,
        tuple(str(x) for x in owner.params),getattr(owner,"label",None),type(owner).__name__)


@pytest.mark.parametrize("kind",["gate","instruction","controlled","annotated"])
@pytest.mark.parametrize("symbolic",[False,True])
@pytest.mark.parametrize("copy",[False,True])
@pytest.mark.parametrize("mutation",["name","label","params","definition"])
def test_actual_generic_owner_changes_preserve_independent_cached_context(kind,symbolic,copy,mutation):
    native,public=apis()
    def call(a):
        owner,base,p=build(a,kind,symbolic)
        circuit=a.QC(owner.num_qubits);circuit.append(owner,range(owner.num_qubits),copy=copy)
        context=circuit.data[0];target=base if kind=="annotated" else owner
        if mutation=="name":target.name="changed"
        elif mutation=="label":target.label="new"
        elif mutation=="params":target.params=[.7]
        else:
            value=p if symbolic else .25
            body=a.QC(target.num_qubits,global_phase=value/7);body.rz(3*value,target.num_qubits-1)
            target.definition=body
        return fields(context),fields(circuit.data[0]),tuple(x.name for x in circuit.parameters),circuit.data[0].operation is owner
    assert call(native)==call(public)


@pytest.mark.parametrize("mode",[False,None,True,"omitted"])
@pytest.mark.parametrize("symbolic",[False,True])
def test_actual_generic_control_mode_returns_real_control_or_annotation(mode,symbolic):
    native,public=apis()
    def call(a):
        owner,_,_=build(a,"gate",symbolic)
        result=owner.control(ctrl_state=0) if mode=="omitted" else owner.control(annotated=mode,ctrl_state=0)
        return type(result).__name__,result.num_qubits,tuple(str(x) for x in result.params)
    assert call(native)==call(public)


@pytest.mark.parametrize("kind",["gate","instruction","controlled","annotated"])
@pytest.mark.parametrize("symbolic",[False,True])
@pytest.mark.parametrize("copy",[False,True])
@pytest.mark.parametrize("mutation",["name","label","params"])
def test_actual_defined_owner_binding_matches_full_operator_or_explicit_public_phase_error(kind,symbolic,copy,mutation,record_property):
    native,public=apis()
    from qiskit.quantum_info import Operator as PublicOperator
    from quantumbridge.information import Operator
    results=[]
    for a,operator in ((native,Operator),(public,PublicOperator)):
        owner,base,p=build(a,kind,symbolic)
        circuit=a.QC(owner.num_qubits);circuit.append(owner,range(owner.num_qubits),copy=copy)
        target=base if kind=="annotated" else owner
        if mutation=="name":target.name="changed"
        elif mutation=="label":target.label="new"
        else:target.params=[.7]
        try:results.append(operator(circuit.assign_parameters({p:.3} if symbolic else {})).data)
        except Exception as error:results.append(type(error).__name__)
    x=.3 if symbolic else .25
    u=np.exp(1j*x/5)*np.array([[np.cos(x),-np.sin(x)],[np.sin(x),np.cos(x)]])
    expected=np.eye(4,dtype=complex) if kind in {"controlled","annotated"} else u
    if kind in {"controlled","annotated"}:expected[:2,:2]=u
    np.testing.assert_allclose(results[0],expected,atol=2e-12,rtol=0)
    import qiskit
    if kind=="instruction" and not symbolic and qiskit.__version__.startswith("2.4."):
        assert results[1]=="TypeError"
        record_property("contract","INTENTIONAL_SAFETY_DIFFERENCE")
        record_property("public_result","UPSTREAM_ERROR")
    else:
        record_property("contract","MATCH")
        order=[0,2,1,3] if len(expected)==4 else [0,1]
        np.testing.assert_allclose(results[0],results[1][np.ix_(order,order)],atol=2e-12,rtol=0)


@pytest.mark.parametrize("kind",["gate","instruction","controlled","annotated"])
@pytest.mark.parametrize("symbolic",[False,True])
@pytest.mark.parametrize("copy",[False,True])
@pytest.mark.parametrize("inverse",[False,True])
def test_actual_definition_replacement_operator_and_inverse_distinguish_stale_public_control(kind,symbolic,copy,inverse,record_property):
    native,public=apis()
    from qiskit.quantum_info import Operator as PublicOperator
    from quantumbridge.information import Operator
    results=[]
    for a,operator in ((native,Operator),(public,PublicOperator)):
        source,base,p=build(a,kind,symbolic)
        circuit=a.QC(source.num_qubits);circuit.append(source,range(source.num_qubits),copy=copy)
        value=p if symbolic else .25;target=base if kind=="annotated" else source
        replacement=a.QC(target.num_qubits,global_phase=value/7);replacement.rz(3*value,target.num_qubits-1)
        target.definition=replacement
        try:
            out=circuit.assign_parameters({p:.3} if symbolic else {})
            if inverse:out=out.inverse()
            matrix=operator(out).data
            if a is public and len(matrix)==4:matrix=matrix[np.ix_([0,2,1,3],[0,2,1,3])]
            results.append(matrix)
        except Exception as error:results.append(type(error).__name__)
    x=.3 if symbolic else .25;changed=not (symbolic and copy)
    local=np.exp(1j*x/(7 if changed else 5))*(np.diag([np.exp(-1.5j*x),np.exp(1.5j*x)]) if changed else
        np.array([[np.cos(x),-np.sin(x)],[np.sin(x),np.cos(x)]]))
    if kind=="controlled" and changed:expected=np.kron(np.eye(2),local)
    elif kind in {"controlled","annotated"}:expected=np.eye(4,dtype=complex);expected[:2,:2]=local
    else:expected=local
    if inverse:expected=expected.conj().T
    np.testing.assert_allclose(results[0],expected,atol=2e-12,rtol=0)
    if kind=="controlled" and inverse:
        record_property("contract","INTENTIONAL_SAFETY_DIFFERENCE")
        if symbolic:
            assert results[1]=="TypeError";record_property("public_result","UPSTREAM_ERROR")
        else:
            old=np.eye(4,dtype=complex)
            old[:2,:2]=np.exp(-1j*x/5)*np.array([[np.cos(x),np.sin(x)],[-np.sin(x),np.cos(x)]])
            np.testing.assert_allclose(results[1],old,atol=2e-12,rtol=0)
            assert not np.allclose(results[1],expected,atol=1e-5,rtol=0)
            record_property("public_result","STALE_BASE_INVERSE_IGNORES_REPLACED_DEFINITION")
    else:
        np.testing.assert_allclose(results[1],expected,atol=2e-12,rtol=0)
        record_property("contract","MATCH")
