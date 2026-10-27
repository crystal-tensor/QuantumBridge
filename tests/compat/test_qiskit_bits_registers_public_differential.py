# Copyright 2026 QuantumBridge Contributors.
# Licensed under the Apache License, Version 2.0.
"""Independent installed public calls; no SDK implementation source copying."""
import numpy as np
import pytest
import quantumbridge as qb


def apis():
    pytest.importorskip("qiskit")
    from qiskit import QuantumCircuit,QuantumRegister,ClassicalRegister
    from qiskit.circuit import AncillaRegister,Qubit,Clbit,AncillaQubit,Bit
    return ((qb.Circuit,qb.QuantumRegister,qb.ClassicalRegister,qb.AncillaRegister,qb.Qubit,qb.Clbit,qb.AncillaQubit,qb.Bit),
            (QuantumCircuit,QuantumRegister,ClassicalRegister,AncillaRegister,Qubit,Clbit,AncillaQubit,Bit))


def outcome(call):
    try:return ("value",call())
    except Exception as error:return ("error",type(error).__name__)


@pytest.mark.parametrize("kind",[1,2,3])
@pytest.mark.parametrize("size,name",[(0,"empty"),(1,"r"),(2,"r"),(-1,"r"),(1.0,"r"),
    (True,"r"),(np.int64(2),"r"),(1,""),(1,"not a name"),(1,4)])
def test_actual_register_constructors_size_names_types_and_error_classes(kind,size,name):
    native,public=apis()
    def call(api):
        register=api[kind](size,name)
        return register.size,register.name,len(register),[type(bit).__name__ for bit in register]
    assert outcome(lambda:call(native))==outcome(lambda:call(public))


@pytest.mark.parametrize("kind",[1,2,3])
def test_actual_register_index_slice_iteration_and_membership(kind):
    native,public=apis()
    def call(api):
        r=api[kind](3,"r")
        return r[-1]==r[2],r[::-1]==list(reversed(list(r))),r[::2]==[r[0],r[2]],r[0] in r
    assert call(native)==call(public)


@pytest.mark.parametrize("kind",[1,2,3])
def test_actual_duplicate_members_reject_before_constructing_a_register(kind):
    native,public=apis()
    def call(api):
        bit=api[{1:4,2:5,3:6}[kind]]()
        return api[kind](name="r",bits=[bit,bit])
    assert outcome(lambda:call(native))==outcome(lambda:call(public))


@pytest.mark.parametrize("kind,bit_kind",[(1,5),(2,4),(3,4)])
def test_actual_wrong_register_member_types(kind,bit_kind):
    native,public=apis()
    def call(api):return api[kind](name="r",bits=[api[bit_kind]()])
    assert outcome(lambda:call(native))==outcome(lambda:call(public))


@pytest.mark.parametrize("kind",[1,2,3])
def test_actual_size_and_bits_arguments_are_exclusive(kind):
    native,public=apis()
    def call(api):return api[kind](1,"r",bits=[api[{1:4,2:5,3:6}[kind]]()])
    assert outcome(lambda:call(native))==outcome(lambda:call(public))


@pytest.mark.parametrize("kind",[4,5,6])
def test_actual_standalone_bits_are_not_one_global_integer_identity(kind):
    native,public=apis()
    def call(api):
        a,b=api[kind](),api[kind]()
        return a==b,a==a,len({a,b}),isinstance(a,api[4]),isinstance(a,api[5])
    assert call(native)==call(public)


def test_actual_base_bit_cannot_be_instantiated():
    native,public=apis()
    assert outcome(lambda:native[7]())==outcome(lambda:public[7]())


def test_actual_named_registers_recreate_equal_logical_bits_not_standalone_uid_bits():
    native,public=apis()
    def call(api):
        a,b=api[1](2,"q"),api[1](2,"q")
        return a==b,a[0]==b[0],a[0]==b[1],a[0]==api[4]()
    assert call(native)==call(public)


def test_actual_alias_membership_preserves_two_register_positions():
    native,public=apis()
    def call(api):
        a,b,c=api[4](),api[4](),api[4]()
        r=api[1](name="r",bits=[a,b]);s=api[1](name="s",bits=[b,c]);circuit=api[0](r,s)
        found=circuit.find_bit(b)
        return circuit.num_qubits,found.index,[(reg.name,index) for reg,index in found.registers],circuit.qubits==[a,b,c]
    assert call(native)==call(public)


@pytest.mark.parametrize("kind",[4,5,6])
def test_actual_existing_bit_can_be_aliased_by_a_new_register_without_new_wire(kind):
    native,public=apis()
    def call(api):
        c=api[0]();bit=api[kind]();c.add_bits([bit]);reg=api[2 if kind==5 else 1](name="alias",bits=[bit])
        result=c.add_register(reg)
        return result,c.num_qubits,c.num_clbits,[(r.name,i) for r,i in c.find_bit(bit).registers]
    assert call(native)==call(public)


@pytest.mark.parametrize("case",["foreign","integer","duplicate-register","existing-add-bits"])
def test_actual_circuit_bit_registration_errors(case):
    native,public=apis()
    def call(api):
        c=api[0](1)
        if case=="foreign":return c.find_bit(api[4]())
        if case=="integer":return c.find_bit(0)
        if case=="duplicate-register":return c.add_register(api[1](2,"q"))
        return c.add_bits([c.qubits[0]])
    assert outcome(lambda:call(native))==outcome(lambda:call(public))


@pytest.mark.parametrize("case",["register-getitem","register-iterator","circuit-cached","circuit-register","circuit-standalone"])
def test_actual_python_views_are_not_confused_with_logical_bit_equality(case):
    native,public=apis()
    def call(api):
        c=api[0](1);r=c.qregs[0]
        if case=="register-getitem":return r[0] is r[0]
        if case=="register-iterator":return next(iter(r)) is r[0]
        if case=="circuit-cached":return c.qubits[0] is c.qubits[0]
        if case=="circuit-register":return c.qubits[0] is r[0]
        bit=api[4]();c.add_bits([bit]);return c.qubits[-1] is bit,c.qubits[-1]==bit
    assert call(native)==call(public)


@pytest.mark.parametrize("widths",[(0,0),(0,2),(1,0)])
def test_actual_empty_circuit_register_and_width_contracts(widths):
    native,public=apis()
    def call(api):
        c=api[0](*widths)
        return c.num_qubits,c.num_clbits,[(r.name,len(r)) for r in c.qregs+c.cregs]
    assert call(native)==call(public)
