# Copyright 2026 QuantumBridge Contributors.
# Licensed under the Apache License, Version 2.0.
"""Public handles and insertion plans obey native resource/ownership limits."""
import pytest
import quantumbridge as qb
from quantumbridge.core.standard_gates import RYGate,XGate
from quantumbridge.core.gate_limits import GateCircuitLimits,gate_circuit_scope


def test_bound_handle_cannot_modify_a_circuit_copy():
    circuit=qb.QuantumCircuit(1);handle=circuit.ry(.3,0);copied=circuit.copy();handle.inverse()
    assert circuit.data[0].params==[-.3] and copied.data[0].params==[.3]


def test_handle_with_a_later_stale_slot_fails_before_committing_any_inverse():
    circuit=qb.QuantumCircuit(2);handle=circuit.ry(.3,[0,1]);del circuit.data[1]
    with pytest.raises(IndexError):handle.inverse()
    assert circuit.data[0].params==[.3]


def test_broadcast_bad_second_target_cannot_leave_a_first_insertion():
    circuit=qb.QuantumCircuit(2)
    with pytest.raises(ValueError):circuit.cx([0,1],[1,1])
    assert len(circuit.data)==0


def test_data_assignment_invalid_later_context_does_not_clear_the_original():
    circuit=qb.QuantumCircuit(2);circuit.ry(.3,0)
    contexts=[qb.CircuitInstruction(XGate(),[circuit.qubits[1]],[]),qb.CircuitInstruction(XGate(),[qb.Qubit()],[])]
    with pytest.raises(ValueError):circuit.data=contexts
    assert len(circuit.data)==1 and circuit.data[0].params==[.3]


def test_standalone_instruction_set_handles_are_bounded_before_append():
    handle=qb.InstructionSet();context=qb.CircuitInstruction(XGate())
    with gate_circuit_scope(GateCircuitLimits(max_total_operations=1)):
        handle.add(context)
        with pytest.raises(MemoryError):handle.add(context)
    assert len(handle)==1


def test_parameterized_public_append_keeps_copy_policy_and_current_invocation_slot():
    p=qb.Parameter("p");gate=RYGate(p);copied=qb.QuantumCircuit(1);shared=qb.QuantumCircuit(1)
    copied.append(gate,[0],copy=True);shared.append(gate,[0],copy=False);gate.params[0]=.7
    assert copied.data[0].operation is not gate and shared.data[0].operation is gate
    assert copied.parameters==shared.parameters==(p,)
    for circuit in (copied,shared):
        circuit.assign_parameters({p:.4},inplace=True)
        assert not circuit.parameters and circuit.data[0].params==[.4]
