# Copyright 2026 QuantumBridge Contributors.
# Licensed under the Apache License, Version 2.0.
"""Structural QPY export of bounded native doubly controlled primitives."""
import io
import numpy as np
import pytest
import quantumbridge as qb
from quantumbridge.information import Operator
from quantumbridge.serialization import qpy_dumps,qpy_loads
from quantumbridge.serialization.errors import ResourceLimitError,UnsupportedFeature
from quantumbridge.serialization.limits import SerializationLimits


def circuit(name,theta=None):
    return qb.Circuit(3).append("native_controlled",(1,2),controls=(0,),
        params=() if theta is None else (theta,),
        metadata={"controlled_base":{"name":name,"metadata":{},"controls":1}})


def oracle(name,theta=None):
    result=np.eye(8,dtype=complex)
    if name=="cx":result[[6,7]]=result[[7,6]]
    elif name=="cz":result[-1,-1]=-1
    elif name=="swap":result[[5,6]]=result[[6,5]]
    elif name=="crx":result[-2:,-2:]=[[np.cos(theta/2),-1j*np.sin(theta/2)],[-1j*np.sin(theta/2),np.cos(theta/2)]]
    elif name=="cry":result[-2:,-2:]=[[np.cos(theta/2),-np.sin(theta/2)],[np.sin(theta/2),np.cos(theta/2)]]
    elif name=="crz":result[-2:,-2:]=np.diag([np.exp(-.5j*theta),np.exp(.5j*theta)])
    else:result[-1,-1]=np.exp(1j*theta)
    return result


def actual(payload,transport,parameter=None):
    if transport=="native":
        restored=qpy_loads(payload)[0]
        if parameter is not None:restored=restored.assign_parameters({restored.parameters[0]:.3})
        return Operator(restored).data
    pytest.importorskip("qiskit")
    from qiskit import qpy
    from qiskit.quantum_info import Operator as PublicOperator
    restored=qpy.load(io.BytesIO(payload))[0]
    if parameter is not None:restored=restored.assign_parameters({next(iter(restored.parameters)):.3})
    width=restored.num_qubits
    order=[int(format(i,"0"+str(width)+"b")[::-1],2) for i in range(1<<width)]
    return PublicOperator(restored).data[np.ix_(order,order)]


@pytest.mark.parametrize("transport",["native","public"])
@pytest.mark.parametrize("name",["cx","cz","swap"])
def test_canonical_controlled_involutions_use_actual_standard_qpy_records(name,transport):
    np.testing.assert_allclose(actual(qpy_dumps(circuit(name)),transport),oracle(name),atol=6e-13,rtol=0)


@pytest.mark.parametrize("transport",["native","public"])
@pytest.mark.parametrize("symbolic",[False,True])
@pytest.mark.parametrize("name",["crx","cry","crz","cp"])
def test_double_controlled_rotations_keep_symbolic_phase_without_dense_export(name,symbolic,transport,monkeypatch):
    p=qb.Parameter("p");theta=2*p+p.sin() if symbolic else .4
    def forbidden(*a,**kw):pytest.fail("structural QPY rotation used dense Gate export")
    monkeypatch.setattr(qb.Gate,"to_matrix",forbidden)
    payload=qpy_dumps(circuit(name,theta));monkeypatch.undo()
    value=2*.3+np.sin(.3) if symbolic else .4
    np.testing.assert_allclose(actual(payload,transport,p if symbolic else None),oracle(name,value),atol=1e-12,rtol=0)


def test_qpy_rotation_expansion_budget_is_checked_before_constructing_a_gate(monkeypatch):
    source=circuit("crx",.4)
    monkeypatch.setattr(qb.Gate,"__init__",lambda *a,**kw:pytest.fail("QPY gate allocated before expansion admission"))
    with pytest.raises(ResourceLimitError):qpy_dumps(source,limits=SerializationLimits(max_gate_expansion=4))


def test_numeric_rotation_does_not_require_unused_symbolic_depth_budget():
    payload=qpy_dumps(circuit("crx",.4),limits=SerializationLimits(max_symbolic_expression_depth=1))
    np.testing.assert_allclose(Operator(qpy_loads(payload)[0]).data,oracle("crx",.4),atol=1e-12,rtol=0)


def test_opaque_controlled_metadata_cannot_execute_foreign_equality_callbacks():
    class Foreign:
        def __eq__(self,other):pytest.fail("foreign equality callback")
        def __deepcopy__(self,memo):pytest.fail("foreign copy callback")
    source=circuit("cx")
    source.operations[0].metadata["controlled_base"]["metadata"]=Foreign()
    with pytest.raises(UnsupportedFeature):qpy_dumps(source)


@pytest.mark.parametrize("count",[2,3,4])
@pytest.mark.parametrize("name,symbolic",[(name,symbolic) for name in ("rx","ry","rz","phase") for symbolic in (False,True)]
    +[(name,False) for name in ("sx","sxdg","x","y","z","h")])
@pytest.mark.parametrize("transport",["native","public"])
def test_flat_multicontrol_axis_and_phase_conjugated_primitives_use_structural_qpy(count,name,symbolic,transport,monkeypatch):
    p=qb.Parameter("p");theta=2*p+p.sin() if symbolic else .4
    angle=2*.3+np.sin(.3) if symbolic else .4
    constants={"sx":np.array([[1+1j,1-1j],[1-1j,1+1j]])/2,
        "sxdg":np.array([[1-1j,1+1j],[1+1j,1-1j]])/2,
        "x":np.array([[0,1],[1,0]]),"y":np.array([[0,-1j],[1j,0]]),
        "z":np.diag([1,-1]),"h":np.array([[1,1],[1,-1]])/np.sqrt(2)}
    rotations={"rx":np.array([[np.cos(angle/2),-1j*np.sin(angle/2)],[-1j*np.sin(angle/2),np.cos(angle/2)]]),
        "ry":np.array([[np.cos(angle/2),-np.sin(angle/2)],[np.sin(angle/2),np.cos(angle/2)]]),
        "rz":np.diag([np.exp(-.5j*angle),np.exp(.5j*angle)]),"phase":np.diag([1,np.exp(1j*angle)])}
    local=constants[name] if name in constants else rotations[name]
    expected=np.eye(1<<(count+1),dtype=complex);expected[-2:,-2:]=local
    source=qb.Circuit(count+1).append("native_controlled",(count,),controls=tuple(range(count)),
        params=(theta,) if name in rotations else (),
        metadata={"controlled_base":{"name":name,"metadata":{},"controls":count}})
    monkeypatch.setattr(qb.Gate,"to_matrix",lambda *a,**kw:pytest.fail("multicontrol QPY used dense export"))
    payload=qpy_dumps(source);monkeypatch.undo()
    np.testing.assert_allclose(actual(payload,transport,p if symbolic else None),expected,atol=3e-12,rtol=0)
    if transport=="public":
        from qiskit.circuit import library
        from qiskit.quantum_info import Operator as PublicOperator
        classes={"rx":"RXGate","ry":"RYGate","rz":"RZGate","phase":"PhaseGate",
            "sx":"SXGate","sxdg":"SXdgGate","x":"XGate","y":"YGate","z":"ZGate","h":"HGate"}
        owner=getattr(library,classes[name])(*((angle,) if name in rotations else ()))
        matrix=PublicOperator(owner.control(count,annotated=False)).data
        order=[int(format(i,"0"+str(count+1)+"b")[::-1],2) for i in range(len(matrix))]
        np.testing.assert_allclose(matrix[np.ix_(order,order)],expected,atol=3e-12,rtol=0)


def test_multicontrol_parity_work_is_admitted_before_constructing_any_gate(monkeypatch):
    source=qb.Circuit(4).append("native_controlled",(3,),controls=(0,1,2),params=(.4,),
        metadata={"controlled_base":{"name":"rz","metadata":{},"controls":3}})
    monkeypatch.setattr(qb.Gate,"__init__",lambda *a,**kw:pytest.fail("parity expansion allocated before admission"))
    with pytest.raises(ResourceLimitError):qpy_dumps(source,limits=SerializationLimits(max_gate_expansion=16))


@pytest.mark.parametrize("kind",["cycle","arity","opaque"])
def test_nested_control_descriptor_errors_do_not_copy_opaque_values_or_allocate_gates(kind,monkeypatch):
    class Foreign:
        def __eq__(self,other):pytest.fail("opaque descriptor equality callback")
        def __deepcopy__(self,memo):pytest.fail("opaque descriptor copy callback")
    child={"name":"rz","metadata":{},"controls":2}
    parent={"name":"native_controlled","metadata":{"controlled_base":child},"controls":1}
    if kind=="cycle":parent["metadata"]["controlled_base"]=parent
    elif kind=="arity":child["controls"]=3
    else:child["metadata"]={"foreign":Foreign()}
    source=qb.Circuit(4).append("native_controlled",(1,2,3),controls=(0,),params=(.4,),metadata={"controlled_base":parent})
    monkeypatch.setattr(qb.Gate,"__init__",lambda *a,**kw:pytest.fail("invalid nested control allocated a gate"))
    from quantumbridge.serialization.errors import FormatValidationError
    with pytest.raises((UnsupportedFeature,FormatValidationError)):qpy_dumps(source)
