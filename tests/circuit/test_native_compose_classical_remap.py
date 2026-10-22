# Copyright 2026 QuantumBridge Contributors.
# Licensed under the Apache License, Version 2.0.
"""Typed identifier identity, scope and executable remapping."""
import pytest
import quantumbridge as qb
from quantumbridge.core import classical as ce
from quantumbridge.core.errors import CircuitError


def test_var_object_remap_rewrites_store_target_and_all_expression_leaves():
    source=qb.Circuit(1);a=source.add_var("a",True)
    source.store(a,ce.logical_not(a))
    b=ce.Var.new("b",ce.Bool())
    out=qb.Circuit(1).compose(source,var_remap={a:b})
    assert out.get_var("b") is b and not out.has_var("a")
    for op in out.operations:
        data=op.metadata["control_node"].data
        assert data["target"] is b
    assert out.operations[-1].metadata["control_node"].data["value"].args[0] is b


def test_nested_local_name_remap_rewrites_its_own_lexical_declaration():
    body=qb.Circuit(1,1);local=body.add_var("nested",True)
    body=body.if_else(local,qb.Circuit(1,1).x(0))
    source=qb.Circuit(1,1).if_else(True,body).measure(0,0)
    out=qb.Circuit(1,1).compose(source,var_remap={"nested":"renamed"})
    child=out.operations[0].metadata["control_node"].data["body"]
    assert child.get_var("renamed").name=="renamed" and not child.has_var("nested")
    assert qb.StatevectorDevice().run_shots(out,shots=3).counts()=={"1":3}


def test_parameter_and_classical_variable_same_name_are_separate_namespaces():
    p=qb.Parameter("a");source=qb.Circuit(1)
    a=source.add_var("a",True)
    source=source.if_else(a,qb.Circuit(1).ry(p,0))
    out=qb.Circuit(1).compose(source,var_remap={"a":"b"})
    assert out.parameters==(p,) and out.get_var("b").type==ce.Bool()
    assert qb.StatevectorDevice().run(out.bind({p:0})).probabilities()=={"0":1,"1":0}


def test_remap_type_error_is_atomic_even_after_an_existing_target_operation():
    target=qb.Circuit(1).h(0);source=qb.Circuit(1);a=source.add_var("a",True)
    with pytest.raises(CircuitError): target.compose(source,var_remap={a:ce.Var.new("b",ce.UInt(2))},inplace=True)
    assert [op.name for op in target.operations]==["h"] and target.num_vars==0


def test_var_cannot_be_replaced_with_stretch():
    source=qb.Circuit(1);a=source.add_var("a",True)
    with pytest.raises(CircuitError): qb.Circuit(1).compose(source,var_remap={a:ce.Stretch.new("b")})


def test_stretch_cannot_be_replaced_with_var():
    source=qb.Circuit(1);a=source.add_stretch("a")
    with pytest.raises(CircuitError): qb.Circuit(1).compose(source,var_remap={a:ce.Var.new("b",ce.Bool())})


def test_unused_name_mapping_does_not_rename_an_unrelated_identifier():
    source=qb.Circuit(1);source.add_var("a",True)
    out=qb.Circuit(1).compose(source,var_remap={"unused":"b"})
    assert out.has_var("a") and not out.has_var("b")


def test_two_source_identifiers_cannot_map_to_same_name():
    source=qb.Circuit(1);source.add_var("a",True);source.add_var("b",False)
    with pytest.raises(CircuitError): qb.Circuit(1).compose(source,var_remap={"a":"c","b":"c"})


def test_local_remap_cannot_redeclare_a_target_variable():
    source=qb.Circuit(1);a=source.add_var("a",True)
    target=qb.Circuit(1);b=target.add_var("b",False)
    with pytest.raises(CircuitError):target.compose(source,var_remap={a:b},inline_captures=True)


def test_input_and_capture_scopes_cannot_coexist():
    target=qb.Circuit(1);target.add_input("input",ce.Bool())
    with pytest.raises(CircuitError):target.add_capture(ce.Var.new("capture",ce.Bool()))


def test_var_and_stretch_share_an_identifier_name_namespace():
    target=qb.Circuit(1);target.add_var("a",True)
    with pytest.raises(CircuitError):target.add_stretch("a")


def test_empty_identifier_name_is_valid_storage_and_survives_ir():
    from quantumbridge.compat.qiskit_adapter import circuit_from_ir
    from quantumbridge.ir.qb_ir import IRProgram
    source=qb.Circuit(1);a=source.add_var("",True)
    restored=circuit_from_ir(IRProgram.from_json(source.to_ir().to_json()))
    assert restored.get_var("")==a
    actual=qb.StatevectorDevice().run(restored).metadata()["classical_ensemble"][0]
    assert next(iter(actual["variables"].values()))["value"] is True


def test_invalid_scope_metadata_is_not_accepted_as_arbitrary_circuit_metadata():
    source=qb.Circuit(1,metadata={"classical_scope":{"version":1,"identifiers":[{"node":{},"scope":"local"}]}})
    with pytest.raises((ValueError,TypeError)):source.compose(qb.Circuit(1))


def test_stretch_capture_can_be_inlined_to_same_target_stretch():
    target=qb.Circuit(1);s=target.add_stretch("s")
    source=qb.Circuit(1);source.add_capture(s)
    out=target.compose(source,inline_captures=True)
    assert list(out.iter_declared_stretches())==[s] and not list(out.iter_captured_stretches())


def test_uninitialized_var_alike_copy_retains_identity_but_not_initial_store():
    source=qb.Circuit(1);a=source.add_var("a",True)
    empty=source.copy_empty_like()
    assert empty.get_var("a")==a and not empty.operations
    with pytest.raises(ce.ClassicalExecutionError,match="initialization"):
        qb.StatevectorDevice().run(empty.if_else(a,qb.Circuit(1).x(0)))


def test_empty_named_typed_storage_roundtrips_its_actual_runtime_snapshot():
    source=qb.Circuit(1);a=source.add_var("",True)
    data=qb.StatevectorDevice().run(source).metadata()["classical_ensemble"][0]
    restored=ce.ClassicalStore.from_dict(data)
    assert ce.classical_eval(a,restored) is True
