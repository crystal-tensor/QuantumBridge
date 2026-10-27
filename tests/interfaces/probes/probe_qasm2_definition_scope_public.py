# Copyright 2026 QuantumBridge Contributors. Apache-2.0.
"""Actual installed public QASM2 parsing, with independent complex math."""

import io
from pathlib import Path
import runpy

import numpy as np
import pytest
import qiskit
from qiskit import qasm2,qpy
from qiskit.quantum_info import Operator as PublicOperator,Statevector as PublicStatevector

import quantumbridge as qb
from quantumbridge.information import Operator
from quantumbridge.serialization import qasm2_loads,qasm2_dumps,qpy_dumps,qpy_loads,SerializationError


CASES = runpy.run_path(str(Path(__file__).parents[2]/"serialization/test_qasm2_definition_scope.py"))
INVALID = CASES["INITIAL_INVALID_BODIES"]+CASES["INVALID_BODIES"]
PUBLIC_SIGNATURE_DIFFERENCES = {8,16}


def canonical(array,width):
    order = [int(f"{i:0{width}b}"[::-1],2) for i in range(1<<width)]
    return array[np.ix_(order,order)] if array.ndim == 2 else array[order]


def assert_math(circuit,expected,public):
    matrix = canonical(PublicOperator(circuit).data,circuit.num_qubits) if public else Operator(circuit).data
    state = canonical(PublicStatevector.from_instruction(circuit).data,circuit.num_qubits) if public else qb.StatevectorDevice().statevector(circuit)
    np.testing.assert_allclose(matrix,expected,atol=8e-15,rtol=0)
    np.testing.assert_allclose(state,expected[:,0],atol=8e-15,rtol=0)


@pytest.mark.parametrize("index",range(len(INVALID)))
def test_actual_public_invalid_definition_admission_observation(index,record_property):
    source = CASES["program"](INVALID[index])
    with pytest.raises(SerializationError): qasm2_loads(source)
    record_property("qiskit_version",qiskit.__version__)
    if index in PUBLIC_SIGNATURE_DIFFERENCES:
        assert not qasm2.loads(source).data
        record_property("classification","PUBLIC_QASM2_SIGNATURE_ACCEPTANCE_DIFFERENCE / OPEN")
    else:
        with pytest.raises(qasm2.QASM2ParseError): qasm2.loads(source)
        record_property("classification","both readers reject")


@pytest.mark.parametrize("name",["h","x","p","cphase","cnot","cu1"])
def test_actual_public_literal_user_declarations_and_native_writer(name):
    source = CASES["program"](f'gate {name} a {{ U(pi,0,pi) a; }} qreg q[1]; {name} q[0];')
    expected = CASES["X"]
    public,native = qasm2.loads(source),qasm2_loads(source)
    assert_math(public,expected,True)
    assert_math(native,expected,False)
    text = qasm2_dumps(native)
    assert_math(qasm2.loads(text),expected,True)
    assert_math(qasm2_loads(text),expected,False)


def test_actual_public_nested_qarg_order_native_writer_and_qpy13_bilateral():
    source,expected = CASES["complex_nested_source_and_oracle"]()
    public,native = qasm2.loads(source),qasm2_loads(source)
    assert_math(public,expected,True)
    assert_math(native,expected,False)
    assert_math(qasm2.loads(qasm2_dumps(native)),expected,True)
    assert_math(qpy.load(io.BytesIO(qpy_dumps(native)))[0],expected,True)
    stream = io.BytesIO()
    qpy.dump(public,stream,version=13)
    restored = qpy_loads(stream.getvalue())[0]
    assert_math(restored,expected,False)
    np.testing.assert_allclose(qb.MatrixProductStateDevice(cutoff=0).statevector(restored),expected[:,0],atol=8e-15,rtol=0)
