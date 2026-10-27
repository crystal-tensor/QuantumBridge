# Copyright 2026 QuantumBridge Contributors.
# Licensed under the Apache License, Version 2.0.
"""Register aliases, exact validation and executable integer mapping."""
import numpy as np
import pytest
import quantumbridge as qb
from quantumbridge.core.errors import CircuitError
from quantumbridge.core.gate_limits import GateCircuitLimits,gate_circuit_scope


def test_register_size_name_iteration_negative_index_and_slice():
    register=qb.QuantumRegister(3,"not a name")
    assert register.size==3 and register.name=="not a name"
    assert register[-1]==register[2] and register[::-1]==list(reversed(list(register)))
    assert register[0] in register and register[::2]==[register[0],register[2]]


def test_empty_quantum_classical_and_ancilla_registers_are_legal():
    for kind in (qb.QuantumRegister,qb.ClassicalRegister,qb.AncillaRegister):
        register=kind(0,"")
        assert register.name=="" and len(register)==0 and list(register)==[]


def test_ancilla_register_exposes_actual_ancilla_bits():
    register=qb.AncillaRegister(2,"anc")
    circuit=qb.Circuit(register)
    assert all(isinstance(bit,qb.AncillaQubit) for bit in circuit.qubits)
    assert circuit.ancillas==circuit.qubits and circuit.num_ancillas==2


@pytest.mark.parametrize("size,error",[(-1,CircuitError),(1.0,TypeError),(True,None),(np.int64(2),None)])
def test_register_integer_protocol_is_not_float_truncation(size,error):
    if error is not None:
        with pytest.raises(error):qb.QuantumRegister(size,"r")
    else:assert len(qb.QuantumRegister(size,"r"))==int(size)


def test_size_and_bits_are_mutually_exclusive():
    with pytest.raises(CircuitError):qb.QuantumRegister(1,"r",bits=[qb.Qubit()])


def test_duplicate_bits_and_cross_type_registers_are_rejected():
    bit=qb.Qubit()
    with pytest.raises(CircuitError):qb.QuantumRegister(name="r",bits=[bit,bit])
    with pytest.raises(TypeError):qb.QuantumRegister(name="r",bits=[qb.Clbit()])


def test_add_register_is_not_add_bits_and_retains_existing_aliases():
    circuit=qb.Circuit(2);existing=circuit.qubits[:];new=qb.Qubit()
    alias=qb.QuantumRegister(name="alias",bits=[existing[1],new])
    assert circuit.add_register(alias) is None
    assert circuit.qubits==existing+[new] and circuit.num_qubits==3
    assert circuit.find_bit(existing[1]).registers==[(circuit.qregs[0],1),(alias,0)]


def test_add_bits_rejects_existing_members_before_any_partial_mutation():
    circuit=qb.Circuit(1);original=circuit.qubits[:];fresh=qb.Qubit()
    with pytest.raises(CircuitError):circuit.add_bits([fresh,original[0]])
    assert circuit.qubits==original


def test_duplicate_register_names_leave_circuit_unchanged():
    circuit=qb.Circuit(1)
    with pytest.raises(CircuitError):circuit.add_register(qb.QuantumRegister(3,"q"))
    assert circuit.num_qubits==1 and len(circuit.qregs)==1


def test_real_bit_operands_execute_on_noncontiguous_quantum_and_classical_positions():
    q=qb.QuantumRegister(3,"quantum");c=qb.ClassicalRegister(2,"classical")
    circuit=qb.Circuit(q,c).x(q[2]).cx(q[2],q[0]).measure(q[2],c[0]).measure(q[0],c[1])
    assert circuit.operations[0].targets==(2,)
    assert qb.StatevectorDevice().run_shots(circuit,shots=3).counts()=={"11":3}


def test_register_construction_is_admitted_before_allocating_a_huge_bit_graph():
    with gate_circuit_scope(GateCircuitLimits(max_circuit_bits=3)):
        with pytest.raises(MemoryError):qb.QuantumRegister(10**10,"large")


def test_foreign_bit_iterable_is_not_executed_in_managed_scope():
    from quantumbridge.execution.resource_context import ResourceScope
    from quantumbridge.execution import UnifiedResourceLedger,UnifiedExecutionLimits
    class Trap:
        def __iter__(self):pytest.fail("foreign iterable callback")
    with ResourceScope(UnifiedResourceLedger(UnifiedExecutionLimits(max_total_memory_bytes=100000))):
        with pytest.raises(qb.UnsupportedFeature):qb.QuantumRegister(name="r",bits=Trap())
