# Copyright 2026 QuantumBridge Contributors.
# Licensed under the Apache License, Version 2.0.
"""Real v13 wire records, bilateral public loads and independent execution."""
import io
import struct
from types import SimpleNamespace
import numpy as np
import pytest
import quantumbridge as qb
from quantumbridge.information import Operator
from quantumbridge.serialization import qpy_dumps,qpy_loads,FormatValidationError,SerializationLimits,ResourceLimitError
from quantumbridge.serialization.qpy import FILE_HEADER,CIRCUIT_HEADER,REGISTER


CASES=("normal","loose","aliases","owner-alias","external","external-alias","empty","classical-alias","reordered")


def native_api():return SimpleNamespace(QC=qb.QuantumCircuit,QR=qb.QuantumRegister,CR=qb.ClassicalRegister,Qubit=qb.Qubit,Clbit=qb.Clbit)


def public_api():
    pytest.importorskip("qiskit")
    from qiskit import QuantumCircuit,QuantumRegister,ClassicalRegister
    from qiskit.circuit import Qubit,Clbit
    return SimpleNamespace(QC=QuantumCircuit,QR=QuantumRegister,CR=ClassicalRegister,Qubit=Qubit,Clbit=Clbit)


def build(a,case):
    x,y,z=a.Qubit(),a.Qubit(),a.Clbit();r=a.QR(3,"r")
    if case=="normal":c=a.QC(r,a.CR(1,"c"))
    elif case=="loose":c=a.QC([x,y],[z])
    elif case=="aliases":c=a.QC(a.QR(name="left",bits=[x,y]),a.QR(name="right",bits=[y]))
    elif case=="owner-alias":c=a.QC(r,a.QR(name="alias",bits=[r[2],r[0]]))
    elif case=="external":c=a.QC([r[2],r[0]])
    elif case=="external-alias":c=a.QC(a.QR(name="alias",bits=[r[2],r[0]]))
    elif case=="empty":c=a.QC(a.QR(0,"empty"),a.CR(0,"ce"))
    elif case=="classical-alias":c=a.QC(r,a.CR(name="ca",bits=[z]),a.CR(name="cb",bits=[z]))
    else:c=a.QC([r[2],r[0],r[1]]);c.add_register(r)
    c.global_phase=.23
    if c.num_qubits:c.ry(.4,c.qubits[-1])
    return c


def graph(c):
    return (c.num_qubits,c.num_clbits,
        [(r.name,[c.find_bit(b).index for b in r]) for r in c.qregs+c.cregs],
        [[(r.name,i) for r,i in c.find_bit(b).registers] for b in c.qubits+c.clbits])


def wire_records(data):
    pos=FILE_HEADER.size+1
    ns,pt,ps,nq,nc,ms,nreg,ninst,nvars=CIRCUIT_HEADER.unpack_from(data,pos)
    pos+=CIRCUIT_HEADER.size+ns+ps+ms;result=[]
    for _ in range(nreg):
        start=pos;k,s,n,nm,inside=REGISTER.unpack_from(data,pos);pos+=REGISTER.size
        name=data[pos:pos+nm].decode();pos+=nm
        mapping=struct.unpack_from("!"+"q"*n,data,pos)
        result.append((k,s,name,inside,mapping,start,pos));pos+=8*n
    return result


@pytest.mark.parametrize("case",CASES)
def test_native_standard_records_preserve_alias_membership_without_a_sidecar(case):
    source=build(native_api(),case);payload=qpy_dumps(source);out=qpy_loads(payload)[0]
    assert graph(out)==graph(source)
    assert b'"bit_graph"' not in payload and b'"registers"' not in payload
    np.testing.assert_allclose(Operator(out).data,Operator(source).data,atol=4e-13,rtol=0)


@pytest.mark.parametrize("case",CASES)
@pytest.mark.parametrize("direction",["native_to_public","public_to_native"])
def test_real_public_qpy_register_records_and_full_complex_operator(case,direction):
    a=public_api()
    from qiskit import qpy
    from qiskit.quantum_info import Operator as PublicOperator
    if direction=="native_to_public":
        source=build(native_api(),case);payload=qpy_dumps(source)
        out=qpy.load(io.BytesIO(payload))[0];expected=Operator(source).data;actual=PublicOperator(out).reverse_qargs().data
    else:
        source=build(a,case);f=io.BytesIO();qpy.dump(source,f,version=13);payload=f.getvalue()
        out=qpy_loads(payload)[0];expected=PublicOperator(source).reverse_qargs().data;actual=Operator(out).data
    assert graph(out)==graph(source)
    np.testing.assert_allclose(actual,expected,atol=4e-13,rtol=0)


def test_same_numeric_wires_with_different_alias_graphs_do_not_collapse():
    first=build(native_api(),"aliases");second=qb.QuantumCircuit([qb.Qubit(),qb.Qubit()])
    second.global_phase=.23;second.ry(.4,1)
    assert (first.num_qubits,first.num_clbits)==(second.num_qubits,second.num_clbits)==(2,0)
    assert graph(qpy_loads(qpy_dumps(first))[0])!=graph(qpy_loads(qpy_dumps(second))[0])
    np.testing.assert_allclose(Operator(first).data,Operator(second).data,atol=4e-13,rtol=0)


def test_alias_measurement_uses_the_restored_classical_bit_and_real_device():
    a=native_api();bit=a.Clbit();q=a.QR(2,"data");left=a.CR(name="left",bits=[bit]);right=a.CR(name="right",bits=[bit])
    source=a.QC(q,left,right);source.x(q[1]);source.measure(q[1],right[0])
    restored=qpy_loads(qpy_dumps(source))[0]
    assert graph(restored)==graph(source)
    assert qb.StatevectorDevice().run_shots(restored,shots=3).counts()=={"1":3}


@pytest.mark.parametrize("malformation",["duplicate-name","duplicate-owner","out-of-range","internal-negative","duplicate-map","boolean","truncated"])
def test_forged_register_records_fail_without_silent_bit_replacement(malformation):
    payload=bytearray(qpy_dumps(build(native_api(),"owner-alias")));records=wire_records(payload)
    if malformation=="duplicate-name":
        source=qb.QuantumCircuit(qb.QuantumRegister(1,"a"),qb.QuantumRegister(1,"b"))
        payload=bytearray(qpy_dumps(source));second=wire_records(payload)[1]
        payload[second[5]+REGISTER.size]=ord("a")
    elif malformation=="duplicate-owner":payload[records[1][5]+1]=1
    elif malformation=="out-of-range":struct.pack_into("!q",payload,records[0][6],3)
    elif malformation=="internal-negative":struct.pack_into("!q",payload,records[0][6],-1)
    elif malformation=="duplicate-map":struct.pack_into("!q",payload,records[0][6]+8,0)
    elif malformation=="boolean":payload[records[0][5]+1]=7
    else:payload=payload[:records[0][6]+2]
    with pytest.raises(FormatValidationError):qpy_loads(payload)


def test_aggregate_register_membership_budget_cannot_be_bypassed_by_overlapping_aliases():
    bit=qb.Qubit();source=qb.QuantumCircuit([bit])
    for i in range(8):source.add_register(qb.QuantumRegister(name="alias"+str(i),bits=[bit]))
    with pytest.raises(ResourceLimitError):qpy_dumps(source,limits=SerializationLimits(max_gate_expansion=7))
