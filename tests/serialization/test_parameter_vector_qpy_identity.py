# Copyright 2026 QuantumBridge Contributors.
# Licensed under the Apache License, Version 2.0.
"""Native/public binary vector identity and actual bound execution."""

import io
import struct
from uuid import UUID

import numpy as np
import pytest

from quantumbridge import Circuit, ParameterVector, ParameterVectorElement
from quantumbridge.information import Operator
from quantumbridge.serialization import qpy_dumps,qpy_loads
from quantumbridge.serialization.errors import FormatValidationError,ResourceLimitError,UnsupportedFeature
from quantumbridge.serialization.limits import SerializationLimits


def fixture():
    vector=ParameterVector("angles",12)
    circuit=Circuit(2)
    for index,parameter in enumerate(vector):
        getattr(circuit,("rx","ry","rz")[index%3])(parameter,index%2)
    circuit.rx(vector[0]*vector[11],1)
    circuit.global_phase=vector[1]/3
    return vector,circuit


def test_native_qpy_vector_and_expression_identity_roundtrip_is_bindable():
    vector,circuit=fixture()
    restored=qpy_loads(qpy_dumps(circuit))[0]
    assert restored.parameters==tuple(vector)
    assert all(type(parameter) is ParameterVectorElement for parameter in restored.parameters)
    assert all(parameter.vector is restored.parameters[0].vector for parameter in restored.parameters)
    for values in ([.03*(index+1) for index in range(12)],[-.04*(index+1) for index in range(12)]):
        np.testing.assert_allclose(Operator(restored.assign_parameters({vector:values})).data,Operator(circuit.assign_parameters(values)).data,atol=4e-15,rtol=0)


def test_optional_native_binary_loads_as_real_public_vector_elements():
    qiskit=pytest.importorskip("qiskit")
    public_qpy=pytest.importorskip("qiskit.qpy")
    info=pytest.importorskip("qiskit.quantum_info")
    vector,circuit=fixture()
    public=public_qpy.load(io.BytesIO(qpy_dumps(circuit)))[0]
    assert [str(p.uuid) for p in public.parameters]==[p.uuid for p in vector]
    assert all(type(p).__name__=="ParameterVectorElement" for p in public.parameters)
    public_vector=next(iter(public.parameters)).vector
    values=[.03*(index+1) for index in range(12)]
    expected=info.Operator(public.assign_parameters({public_vector:values}).reverse_bits()).data
    np.testing.assert_allclose(Operator(circuit.assign_parameters(values)).data,expected,atol=5e-15,rtol=0)


def test_optional_public_binary_replays_vector_symbols_without_upstream_execution():
    qiskit=pytest.importorskip("qiskit")
    public_qpy=pytest.importorskip("qiskit.qpy")
    info=pytest.importorskip("qiskit.quantum_info")
    from qiskit.circuit import ParameterVector as PublicVector
    vector=PublicVector("angles",12)
    circuit=qiskit.QuantumCircuit(2)
    for index,parameter in enumerate(vector):getattr(circuit,("rx","ry","rz")[index%3])(parameter,index%2)
    circuit.rx(vector[0]*vector[11],1)
    circuit.global_phase=vector[1]/3
    data=io.BytesIO();public_qpy.dump(circuit,data,version=13)
    restored=qpy_loads(data.getvalue())[0]
    assert [p.uuid for p in restored.parameters]==[str(p.uuid) for p in vector]
    native_vector=restored.parameters[0].vector
    values=[-.04*(index+1) for index in range(12)]
    expected=info.Operator(circuit.assign_parameters({vector:values}).reverse_bits()).data
    np.testing.assert_allclose(Operator(restored.assign_parameters({native_vector:values})).data,expected,atol=5e-15,rtol=0)


@pytest.mark.parametrize("length,index,error",[(10**9,0,ResourceLimitError),(4,4,FormatValidationError),(0,0,FormatValidationError)])
def test_qpy_vector_bounds_reject_before_native_container_allocation(monkeypatch,length,index,error):
    vector=ParameterVector("angles",4)
    circuit=Circuit(1).rx(vector[0],0)
    payload=qpy_dumps(circuit)
    # Literal published v13 vector-element record, not a parser private hook.
    original=struct.pack("!HQ16sQ",6,4,UUID(vector[0].uuid).bytes,0)+b"angles"
    replacement=struct.pack("!HQ16sQ",6,length,UUID(vector[0].uuid).bytes,index)+b"angles"
    assert payload.count(original)==1
    malformed=payload.replace(original,replacement)
    resize=ParameterVector.resize
    def reject_positive_allocation(value,length):
        if length:pytest.fail("Malformed/overbudget QPY vector reached allocation")
        return resize(value,length)
    monkeypatch.setattr(ParameterVector,"resize",reject_positive_allocation)
    with pytest.raises(error):qpy_loads(malformed,limits=SerializationLimits(max_parameter_nodes=8))


def test_qpy_writer_rejects_orphaned_vector_element_instead_of_changing_identity():
    vector=ParameterVector("angles",4)
    circuit=Circuit(1).rx(vector[3],0)
    vector.resize(2)
    with pytest.raises(UnsupportedFeature):qpy_dumps(circuit)
    vector.resize(4)
    restored=qpy_loads(qpy_dumps(circuit))[0]
    assert restored.parameters==circuit.parameters
