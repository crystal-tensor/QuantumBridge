# Copyright 2026 QuantumBridge Contributors.
# Licensed under the Apache License, Version 2.0.
"""Admission precedes bit graph callbacks, allocation and partial mutation."""
import pytest
import quantumbridge as qb
from quantumbridge.core.errors import CircuitError
from quantumbridge.core.gate_limits import GateCircuitLimits,gate_circuit_scope
from quantumbridge.execution import UnifiedResourceLedger,UnifiedExecutionLimits
from quantumbridge.execution.resource_context import ResourceScope


def scope():return ResourceScope(UnifiedResourceLedger(UnifiedExecutionLimits(max_total_memory_bytes=100000)))


@pytest.mark.parametrize("action",["bind","assign","conditional-tape"])
def test_inconsistent_width_cannot_be_silently_trimmed_during_binding_or_tape_capture(action):
    from quantumbridge.qml.tape import Tape
    from quantumbridge.core.classical import bit
    tape=Tape(1);circuit=tape.circuit;circuit.x(0);circuit.num_bits=1
    with pytest.raises(CircuitError,match="widths disagree"):
        if action=="bind":circuit.bind({})
        elif action=="assign":circuit.assign_parameters({})
        else:tape.cond(bit(0),lambda branch:branch.x(0))
    assert circuit.num_bits==1 and circuit.clbits==[] and len(circuit.operations)==1


def test_foreign_register_size_is_rejected_before_index_callback_in_managed_scope():
    class Trap:
        def __index__(self):pytest.fail("foreign register size callback")
    with scope(),pytest.raises(qb.UnsupportedFeature):qb.QuantumRegister(Trap(),"r")


def test_foreign_circuit_width_is_rejected_before_index_callback_in_managed_scope():
    class Trap:
        def __index__(self):pytest.fail("foreign Circuit width callback")
    with scope(),pytest.raises(qb.UnsupportedFeature):qb.Circuit(Trap())


def test_malformed_native_bit_key_cannot_invoke_foreign_metaclass_equality():
    class Meta(type):
        def __eq__(self,other):pytest.fail("foreign metaclass equality")
    class Trap(metaclass=Meta):pass
    bit=qb.Qubit();bit.__dict__["_key"]=("Qubit",Trap())
    with scope(),pytest.raises((CircuitError,qb.UnsupportedFeature)):qb.Circuit().add_bits([bit])


def test_malformed_native_register_size_cannot_execute_an_index_hook():
    class Trap:
        def __index__(self):pytest.fail("foreign register length callback")
    register=qb.QuantumRegister(1,"r");register.__dict__["_size"]=Trap()
    with scope(),pytest.raises((CircuitError,qb.UnsupportedFeature)):
        qb.QuantumRegister(name="alias",bits=register)


def test_empty_copy_rejects_tampered_bit_collection_before_iterating_it():
    class Trap:
        def __iter__(self):pytest.fail("foreign copied bit iterable")
    circuit=qb.Circuit(1);circuit.__dict__["_qubits"]=Trap()
    with scope(),pytest.raises(qb.UnsupportedFeature):circuit.copy_empty_like()


def test_bit_count_failure_is_atomic_before_installing_new_indices():
    circuit=qb.Circuit(2);original=circuit.qubits[:]
    with gate_circuit_scope(GateCircuitLimits(max_circuit_bits=3)),pytest.raises(MemoryError):
        circuit.add_bits([qb.Qubit(),qb.Qubit()])
    assert circuit.qubits==original and circuit.find_bit(original[1]).index==1


def test_duplicate_new_bits_fail_atomically_even_when_the_public_api_partially_mutates():
    circuit=qb.Circuit();bit=qb.Qubit()
    with pytest.raises(ValueError):circuit.add_bits([bit,bit])
    assert circuit.qubits==[] and circuit.num_qubits==0


def test_malformed_register_cycle_is_rejected_before_copying_or_composing():
    register=qb.QuantumRegister(1,"r");register.__dict__["_bits"]=(register,)
    circuit=qb.Circuit(1)
    with scope(),pytest.raises((CircuitError,qb.UnsupportedFeature)):circuit.add_register(register)
    assert circuit.num_qubits==1
