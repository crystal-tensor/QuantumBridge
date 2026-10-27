# Copyright 2026 QuantumBridge Contributors.
# Licensed under the Apache License, Version 2.0.
"""Builders must expose genuine native standard classes and exact inverses."""
import numpy as np
import pytest
import quantumbridge as qb
import quantumbridge.circuit_library as library
from quantumbridge.information import Operator
from quantumbridge.serialization import qpy_dumps,qpy_loads


CASES=[("id","IGate"),("s","SGate"),("sdg","SdgGate"),("t","TGate"),("tdg","TdgGate"),
    ("sx","SXGate"),("sxdg","SXdgGate"),("rxx","RXXGate"),("ryy","RYYGate"),("rzz","RZZGate")]


def expected(name):
    if name=="id":return np.eye(2)
    if name in {"s","sdg","t","tdg"}:
        angle={"s":np.pi/2,"sdg":-np.pi/2,"t":np.pi/4,"tdg":-np.pi/4}[name]
        return np.diag([1,np.exp(1j*angle)])
    if name in {"sx","sxdg"}:
        result=np.array([[1+1j,1-1j],[1-1j,1+1j]])/2
        return result if name=="sx" else result.conj().T
    pauli={"rxx":np.array([[0,1],[1,0]]),"ryy":np.array([[0,-1j],[1j,0]]),"rzz":np.diag([1,-1])}[name]
    return np.cos(.2)*np.eye(4)-1j*np.sin(.2)*np.kron(pauli,pauli)


@pytest.mark.parametrize("name,kind",CASES)
def test_public_builder_has_its_genuine_native_standard_type_and_independent_math(name,kind):
    pair=name.startswith("r");circuit=qb.QuantumCircuit(2 if pair else 1)
    handle=getattr(circuit,name)(.4,0,1) if pair else getattr(circuit,name)(0)
    assert type(handle.instructions[0]) is getattr(library,kind)
    assert circuit.data[0].is_standard_gate()
    np.testing.assert_allclose(Operator(circuit).data,expected(name),atol=5e-13,rtol=0)
    inverse=circuit.inverse();handle.inverse()
    for out in (circuit,inverse):np.testing.assert_allclose(Operator(out).data,expected(name).conj().T,atol=5e-13,rtol=0)


@pytest.mark.parametrize("name,kind",CASES)
def test_standard_builder_class_and_numeric_matrix_survive_standard_qpy(name,kind):
    pair=name.startswith("r");circuit=qb.QuantumCircuit(2 if pair else 1)
    getattr(circuit,name)(.4,0,1) if pair else getattr(circuit,name)(0)
    out=qpy_loads(qpy_dumps(circuit))[0]
    assert type(out.operations[0].metadata["gate"]) is getattr(library,kind)
    np.testing.assert_allclose(Operator(out).data,expected(name),atol=5e-13,rtol=0)


@pytest.mark.parametrize("name,kind",CASES)
def test_actual_public_builder_standard_class_name_and_inverse_class(name,kind):
    pytest.importorskip("qiskit")
    from qiskit import QuantumCircuit
    pair=name.startswith("r");native=qb.QuantumCircuit(2 if pair else 1);public=QuantumCircuit(2 if pair else 1)
    for circuit in (native,public):getattr(circuit,name)(.4,0,1) if pair else getattr(circuit,name)(0)
    assert native.data[0].operation.base_class.__name__==public.data[0].operation.base_class.__name__==kind
    assert native.inverse().data[0].operation.base_class.__name__==public.inverse().data[0].operation.base_class.__name__
