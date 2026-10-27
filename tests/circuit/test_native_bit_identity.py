# Copyright 2026 QuantumBridge Contributors.
# Licensed under the Apache License, Version 2.0.
"""Logical bit identity is independent of a Circuit's integer position."""
import pytest
import quantumbridge as qb
from quantumbridge.core.errors import CircuitError


def test_standalone_bits_have_distinct_stable_hashable_identities():
    a,b=qb.Qubit(),qb.Qubit()
    assert a!=b and len({a,b})==2 and a==a
    assert qb.Clbit()!=a


def test_ancilla_is_quantum_but_not_classical():
    bit=qb.AncillaQubit()
    assert isinstance(bit,qb.Qubit) and not isinstance(bit,qb.Clbit)


def test_base_bit_is_abstract_not_an_integer_wrapper():
    with pytest.raises(TypeError):qb.Bit()


def test_register_backed_bits_compare_by_logical_register_and_position():
    left,right=qb.QuantumRegister(2,"q"),qb.QuantumRegister(2,"q")
    assert left==right and left[0]==right[0] and left[0]!=right[1]
    assert left[0]!=qb.QuantumRegister(2,"other")[0]


def test_independent_bits_can_have_different_indices_in_different_circuits():
    a,b=qb.Qubit(),qb.Qubit()
    left,right=qb.Circuit(),qb.Circuit()
    left.add_bits([a,b]);right.add_bits([b,a])
    assert left.find_bit(a).index==0 and right.find_bit(a).index==1
    assert left.find_bit(a).registers==[]


def test_register_membership_records_all_alias_positions():
    a,b,c=qb.Qubit(),qb.Qubit(),qb.Qubit()
    first=qb.QuantumRegister(name="first",bits=[a,b])
    second=qb.QuantumRegister(name="second",bits=[b,c])
    circuit=qb.Circuit(first,second)
    assert circuit.num_qubits==3 and circuit.qubits==[a,b,c]
    assert circuit.find_bit(b).index==1
    assert circuit.find_bit(b).registers==[(first,1),(second,0)]


def test_circuit_bit_collections_are_not_mutable_detached_ownership_tables():
    circuit=qb.Circuit(2,1)
    original=circuit.qubits[:]
    circuit.qubits.clear();circuit.clbits.clear();circuit.qregs.clear()
    assert circuit.qubits==original and circuit.num_clbits==1 and len(circuit.qregs)==1


def test_find_bit_does_not_accept_integer_positions_or_unregistered_foreign_bits():
    circuit=qb.Circuit(1)
    for bit in (0,qb.Qubit(),qb.Clbit()):
        with pytest.raises(CircuitError):circuit.find_bit(bit)


def test_copy_and_empty_copy_keep_aliases_without_creating_new_logical_bits():
    a,b=qb.Qubit(),qb.Qubit();register=qb.QuantumRegister(name="q",bits=[a,b])
    source=qb.Circuit(register).x(a)
    for result in (source.copy(),source.copy_empty_like()):
        assert result.qubits==source.qubits and result.qregs==source.qregs
        assert result.find_bit(a).registers==[(register,0)]
    assert not source.copy_empty_like().operations and len(source.operations)==1


def test_bit_identity_fields_are_immutable():
    bit=qb.Qubit()
    with pytest.raises(AttributeError):bit._key=("fake",0)


def test_inverse_and_power_preserve_the_actual_input_register_graph():
    bit=qb.Qubit();register=qb.QuantumRegister(name="alias",bits=[bit])
    circuit=qb.Circuit(register).ry(.3,bit)
    for out in (circuit.inverse(),circuit.power(2)):
        assert out.qubits==circuit.qubits and out.qregs==[register]


def test_compose_maps_native_bit_operands_to_real_target_positions():
    register=qb.QuantumRegister(3,"target")
    source=qb.Circuit(2).x(0).cx(0,1)
    out=qb.Circuit(register).compose(source,qubits=[register[2],register[0]])
    assert out.qubits==list(register)
    assert out.operations[0].targets==(2,) and out.operations[1].controls==(2,)
    assert qb.StatevectorDevice().probabilities(out)["101"]==pytest.approx(1.)


def test_compose_maps_native_classical_bits_without_changing_quantum_order():
    q,c=qb.QuantumRegister(2,"q2"),qb.ClassicalRegister(2,"c2")
    source=qb.Circuit(1,1).x(0).measure(0,0)
    out=qb.Circuit(q,c).compose(source,qubits=q[1:2],clbits=[c[0]])
    assert qb.StatevectorDevice().run_shots(out,shots=2).counts()=={"10":2}
