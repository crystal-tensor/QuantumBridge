# Copyright 2026 QuantumBridge Contributors.
# Licensed under the Apache License, Version 2.0.
"""Independent public composition contracts and actual native execution."""

import numpy as np
import pytest
import quantumbridge as qb
from quantumbridge.information import Operator
from quantumbridge.core import classical as ce


def test_wrap_unitary_preserves_one_real_gate_and_definition_order():
    inner = qb.Circuit(1, name="inner").h(0).rz(.37, 0)
    out = qb.Circuit(2).compose(inner, qubits=[1], wrap=True)
    assert len(out.operations) == 1
    gate = out.operations[0].metadata["gate"]
    assert type(gate) is qb.Gate and gate.name == "inner"
    assert [op.name for op in gate.definition.operations] == ["h", "rz"]
    expected = np.kron(np.eye(2), np.diag(np.exp([-.185j,.185j])) @ np.array([[1,1],[1,-1]])/np.sqrt(2))
    np.testing.assert_allclose(Operator(out).data, expected, atol=5e-13, rtol=0)


@pytest.mark.parametrize("measured", [False, True])
def test_wrap_nonunitary_retains_instruction_and_executes_mapped_bits(measured):
    inner = qb.Circuit(1, int(measured), name="reset_body").reset(0).x(0)
    if measured: inner.measure(0,0)
    out = qb.Circuit(3,3).compose(inner, qubits=[2], clbits=[1] if measured else [], wrap=True)
    assert len(out.operations) == 1
    owner = out.operations[0].metadata["instruction_object"]
    assert type(owner) is qb.Instruction
    if not measured: out.measure(2,1)
    assert qb.StatevectorDevice().run_shots(out, shots=4).counts() == {"010":4}


@pytest.mark.parametrize("copy", [True, False])
def test_public_copy_keyword_preserves_primitive_parameter_values(copy):
    source = qb.Circuit(1).rx(.2,0)
    out = qb.Circuit(1).compose(source, copy=copy)
    source.operations[0] = qb.Operation("rx",(0,),params=(.8,))
    assert out.operations[0].params == (.2,)


def test_compose_single_instruction_retains_an_invocation_object():
    owner = qb.Instruction("opaque",1,0,[])
    out = qb.Circuit(2).compose(owner, qubits=[1])
    assert out.operations[0].metadata["instruction_object"].name == "opaque"
    assert out.operations[0].targets == (1,)


def test_copy_name_is_an_actual_independent_circuit():
    source = qb.Circuit(1,name="old").x(0)
    out = source.copy(name="new")
    assert out.name == "new" and source.name == "old"
    out.h(0)
    assert len(source.operations)==1


def test_front_noncontiguous_mapping_has_independent_full_phase_matrix():
    left = qb.Circuit(3).cx(0,2); left.global_phase=.13
    right=qb.Circuit(2).rx(.31,0).cx(0,1);right.global_phase=.07
    out=left.compose(right,qubits=[2,0],front=True)
    c,s=np.cos(.155),-1j*np.sin(.155)
    rx=np.kron(np.eye(4),np.array([[c,s],[s,c]]))
    mapped=np.zeros((8,8));original=np.zeros((8,8))
    for index in range(8):
        mapped[index^(4 if index&1 else 0),index]=1
        original[index^(1 if index&4 else 0),index]=1
    np.testing.assert_allclose(Operator(out).data,np.exp(.2j)*original@mapped@rx,atol=5e-13,rtol=0)
    assert len(left.operations)==1


def test_public_typed_variable_construction_and_inplace_capture_execution():
    target=qb.Circuit(1,1)
    enabled=target.add_var("enabled",True)
    source=qb.Circuit(1,1)
    source.add_capture(enabled)
    source.store(enabled,ce.logical_not(enabled))
    assert target.compose(source,inline_captures=True,inplace=True) is None
    target=target.if_else(enabled,qb.Circuit(1,1).x(0),qb.Circuit(1,1).z(0)).measure(0,0)
    assert qb.StatevectorDevice().run_shots(target,shots=4).counts()=={"0":4}


def test_var_remap_rewrites_actual_store_and_nested_condition_references():
    source=qb.Circuit(1,1)
    original=source.add_var("flag",True)
    source=source.if_else(original,qb.Circuit(1,1).x(0)).measure(0,0)
    out=qb.Circuit(2,2).compose(source,qubits=[1],clbits=[1],var_remap={"flag":"renamed"})
    assert out.get_var("renamed").name=="renamed" and not out.has_var("flag")
    assert qb.DensityMatrixDevice().run_shots(out,shots=4).counts()=={"01":4}


def test_copy_empty_like_can_create_a_capture_only_scope():
    source=qb.Circuit(1)
    flag=source.add_var("flag",True)
    child=source.copy_empty_like(vars_mode="captures")
    assert list(child.iter_captured_vars())==[flag]
    assert not list(child.iter_declared_vars()) and not child.operations


def test_stretch_scope_can_be_remapped_without_becoming_a_variable():
    source=qb.Circuit(1)
    stretch=source.add_stretch("duration")
    out=qb.Circuit(1).compose(source,var_remap={stretch:"renamed"})
    assert out.get_stretch("renamed").name=="renamed" and not out.has_var("renamed")


def test_native_var_keys_have_stable_hashable_storage_identity():
    a=ce.Var.new("a",ce.Bool())
    b=ce.Var.new("a",ce.Bool())
    assert a!=b and {a:1,b:2}[a]==1
    assert a.name=="a" and a.type==ce.Bool()
