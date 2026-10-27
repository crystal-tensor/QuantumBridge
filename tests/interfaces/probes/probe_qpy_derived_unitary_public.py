# Copyright 2026 QuantumBridge Contributors. Apache-2.0.
"""Actual Qiskit versions read standard records with independent NumPy oracles."""

import io
from pathlib import Path
import runpy

import numpy as np
import pytest
import qiskit
from qiskit import QuantumCircuit,qpy
from qiskit.circuit.library import UnitaryGate
from qiskit.quantum_info import Operator as PublicOperator,Statevector as PublicStatevector

import quantumbridge as qb
from quantumbridge.information import Operator,Statevector
from quantumbridge.serialization import qpy_dumps,qpy_loads


CASES=runpy.run_path(str(Path(__file__).parents[2]/"serialization/test_qpy_derived_unitary.py"))


def canonical(array,width):
    order=[int(f"{i:0{width}b}"[::-1],2) for i in range(1<<width)]
    return array[np.ix_(order,order)] if array.ndim==2 else array[order]


def public_math(circuit,expected):
    np.testing.assert_allclose(canonical(PublicOperator(circuit).data,circuit.num_qubits),expected,atol=5e-13,rtol=0)
    size=1<<circuit.num_qubits
    vector=np.arange(1,size+1)+1j*np.arange(size,0,-1)
    vector=vector/np.linalg.norm(vector)
    public_input=canonical(vector,circuit.num_qubits)
    actual=canonical(PublicStatevector(public_input).evolve(circuit).data,circuit.num_qubits)
    np.testing.assert_allclose(actual,expected@vector,atol=5e-13,rtol=0)


@pytest.mark.parametrize("width",[1,2])
@pytest.mark.parametrize("variant",["inverse","double_inverse","copy_inverse","repeat_inverse"])
def test_native_primitive_derived_standard_qpy_is_read_by_actual_public_sdk(width,variant):
    _,source,expected=CASES["primitive_case"](width,variant)
    public=qpy.load(io.BytesIO(qpy_dumps(source)))[0]
    public_math(public,expected)
    stream=io.BytesIO()
    qpy.dump(public,stream,version=13)
    restored=qpy_loads(stream.getvalue())[0]
    np.testing.assert_allclose(Operator(restored).data,expected,atol=5e-13,rtol=0)


@pytest.mark.parametrize("width",[1,2])
@pytest.mark.parametrize("controls,state",[(1,0),(1,1),(2,1),(2,2)])
@pytest.mark.parametrize("variant",["inverse_control","control_inverse","repeat_inverse","integer_power_inverse",
    "fractional_power_inverse","annotated_inverse","annotated_power_inverse"])
def test_native_control_and_modifier_order_execute_in_actual_public_qpy(width,controls,state,variant):
    source,expected=CASES["controlled_case"](width,controls,state,variant)
    public=qpy.load(io.BytesIO(qpy_dumps(source)))[0]
    public_math(public,expected)


@pytest.mark.parametrize("width",[1,2])
@pytest.mark.parametrize("controls,state",[(0,0),(1,0),(1,1),(2,1),(2,2)])
@pytest.mark.parametrize("factory",["raw","circuit"])
def test_actual_public_inverse_standard_record_reaches_native_with_original_input(width,controls,state,factory):
    U=CASES["matrix"](width)
    if factory=="raw": owner=UnitaryGate(np.exp(.17j)*U)
    else:
        body=QuantumCircuit(width,name="public_source")
        body.unitary(U,list(range(width)))
        body.global_phase=.17
        owner=body.to_gate()
    if controls: owner=owner.control(controls,ctrl_state=state,annotated=False)
    owner=owner.inverse(annotated=False)
    circuit=QuantumCircuit(4,global_phase=.23)
    circuit.h(1)
    wires=(3,0,2,1)[:width+controls]
    circuit.append(owner,list(wires))
    local=CASES["reverse_local"]((np.exp(.17j)*U).conj().T,width)
    block=np.eye(1<<(width+controls),dtype=complex)
    index=sum(((state>>wire)&1)<<(controls-1-wire) for wire in range(controls))
    start=index*(1<<width)
    block[start:start+(1<<width),start:start+(1<<width)]=local
    H=np.array([[1,1],[1,-1]],complex)/np.sqrt(2)
    expected=np.exp(.23j)*CASES["embed"](block,wires,4)@CASES["embed"](H,(1,),4)
    public_math(circuit,expected)
    stream=io.BytesIO()
    qpy.dump(circuit,stream,version=13)
    restored=qpy_loads(stream.getvalue())[0]
    np.testing.assert_allclose(Operator(restored).data,expected,atol=5e-13,rtol=0)
    public_math(qpy.load(io.BytesIO(qpy_dumps(restored)))[0],expected)


def test_actual_public_repeat_inverse_construction_difference_stays_separate(record_property):
    from qiskit.circuit.exceptions import CircuitError
    owner=UnitaryGate(CASES["matrix"](2))
    with pytest.raises(CircuitError,match="Invalid param type"):
        owner.repeat(2).inverse()
    record_property("classification","PUBLIC_UNITARY_REPEAT_INVERSE_CONSTRUCTION_DIFFERENCE / OPEN")
    record_property("actual_version",qiskit.__version__)


def test_original_diagonal_inverse_contract_reads_and_reuses_in_actual_public_sdk():
    original=np.diag([1.,1j,-1.,-1j])
    source=qb.Circuit(2).unitary(original,[0,1]).inverse()
    public=qpy.load(io.BytesIO(qpy_dumps(source,version=13)))[0]
    assert float(public.global_phase)==source.global_phase
    public_math(public,original.conj().T)
    stream=io.BytesIO()
    qpy.dump(public,stream,version=13)
    np.testing.assert_array_equal(Operator(qpy_loads(stream.getvalue())[0]).data,original.conj().T)
    reused=QuantumCircuit(2)
    reused.append(public.data[0].operation.copy().inverse(),[0,1])
    public_math(reused,original)
