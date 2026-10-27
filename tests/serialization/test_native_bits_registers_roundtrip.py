# Copyright 2026 QuantumBridge Contributors.
# Licensed under the Apache License, Version 2.0.
"""Structural identity and scalar definitions, not metadata-only renderings."""
import numpy as np
import pytest
import quantumbridge as qb
from quantumbridge.compat.qiskit_adapter import circuit_from_ir
from quantumbridge.information import Operator
from quantumbridge.ir.qb_ir import IRProgram
from quantumbridge.serialization import qpy_dumps,qpy_loads,qasm2_dumps,qasm3_dumps,UnsupportedFeature


def test_ir_restores_loose_bits_overlapping_registers_and_actual_operands():
    a,b,c=qb.Qubit(),qb.Qubit(),qb.Clbit()
    r=qb.QuantumRegister(name="r",bits=[a,b]);s=qb.QuantumRegister(name="s",bits=[b])
    circuit=qb.Circuit(r,s);circuit.add_bits([c]);circuit.x(b).measure(b,c)
    restored=circuit_from_ir(IRProgram.from_json(circuit.to_ir().to_json()))
    assert restored.qubits==[a,b] and restored.clbits==[c]
    assert [(reg.name,i) for reg,i in restored.find_bit(b).registers]==[("r",1),("s",0)]
    assert qb.StatevectorDevice().run_shots(restored,shots=2).counts()=={"1":2}


def test_ir_rejects_malformed_bit_identity_instead_of_silently_discarding_it():
    payload=qb.Circuit(1).to_ir().to_dict()
    payload["registers"]["bit_graph"]={"version":999,"quantum":[],"classical":[],"groups":[]}
    with pytest.raises(ValueError):IRProgram.from_dict(payload)


def test_ir_roundtrip_zero_width_gate_retains_coherent_scalar_phase():
    source=qb.Circuit(0);source.global_phase=.3
    wrapped=qb.Circuit(0).append(source.to_gate(),[])
    restored=circuit_from_ir(IRProgram.from_json(wrapped.to_ir().to_json()))
    np.testing.assert_allclose(Operator(restored).data,[[np.exp(.3j)]],atol=3e-13,rtol=0)


@pytest.mark.parametrize("num_bits",[0,2])
def test_native_qpy_zero_quantum_width_is_not_rejected_as_a_positive_width_only_circuit(num_bits):
    circuit=qb.Circuit(0,num_bits);circuit.global_phase=.3
    restored=qpy_loads(qpy_dumps(circuit))[0]
    assert restored.num_qubits==0 and restored.num_clbits==num_bits
    np.testing.assert_allclose(Operator(restored).data,[[np.exp(.3j)]],atol=3e-13,rtol=0)


@pytest.mark.parametrize("writer",[qasm2_dumps,qasm3_dumps])
def test_pending_standard_alias_records_are_rejected_instead_of_silently_renaming_them(writer):
    bit=qb.Qubit();register=qb.QuantumRegister(name="alias",bits=[bit])
    circuit=qb.Circuit(register).x(bit)
    with pytest.raises(UnsupportedFeature):writer(circuit)


def test_legacy_measure_all_builds_real_canonical_classical_bits_for_standard_roundtrip():
    circuit=qb.Circuit(2).x(1).measure_all()
    restored=qpy_loads(qpy_dumps(circuit))[0]
    assert circuit.num_clbits==2 and len(circuit.cregs)==1
    assert qb.StatevectorDevice().run_shots(restored,shots=2).counts()=={"01":2}
