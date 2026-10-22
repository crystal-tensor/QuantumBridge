# Copyright 2026 QuantumBridge Contributors.
# Licensed under the Apache License, Version 2.0.
"""Capture composition must execute state updates, not just rename records."""
import pytest
import quantumbridge as qb
from quantumbridge.core import classical as ce
from quantumbridge.core.errors import CircuitError


def test_capture_remap_precedes_inlining_and_updates_the_target_storage():
    target=qb.Circuit(1,1);counter=target.add_var(ce.Var.new("counter",ce.UInt(4)),0)
    source=qb.Circuit(1,1);external=ce.Var.new("external",ce.UInt(4));source.add_capture(external)
    source.store(external,external+3)
    out=target.compose(source,var_remap={external:counter},inline_captures=True)
    out=out.if_else(counter.eq(3),qb.Circuit(1,1).x(0)).measure(0,0)
    for device in (qb.StatevectorDevice(),qb.DensityMatrixDevice(),qb.MatrixProductStateDevice(),qb.StabilizerDevice()):
        result=device.run_shots(out,shots=3,memory=True)
        assert result.counts()=={"1":3}
        assert all(memory["variables"][counter.value[0]]["value"]==3 for memory in result.metadata()["classical_memory"])


def test_capture_inlining_requires_an_existing_identity_not_only_same_name():
    source=qb.Circuit(1);source.add_capture(ce.Var.new("a",ce.Bool()))
    target=qb.Circuit(1);target.add_var("a",True)
    with pytest.raises(CircuitError):target.compose(source,inline_captures=True)


def test_missing_capture_fails_before_inplace_mutation():
    source=qb.Circuit(1).x(0);source.add_capture(ce.Var.new("a",ce.Bool()))
    target=qb.Circuit(1).h(0)
    with pytest.raises(CircuitError):target.compose(source,inline_captures=True,inplace=True)
    assert [x.name for x in target.operations]==["h"] and target.num_vars==0


def test_noninline_capture_is_imported_as_capture_not_as_new_local():
    a=ce.Var.new("a",ce.Bool());source=qb.Circuit(1);source.add_capture(a)
    out=qb.Circuit(1).compose(source)
    assert list(out.iter_captured_vars())==[a] and not list(out.iter_declared_vars())
    with pytest.raises(ce.ClassicalExecutionError,match="lexical"):
        qb.StatevectorDevice().run(out)


def test_existing_capture_cannot_be_redeclared_without_inlining():
    target=qb.Circuit(1);a=target.add_var("a",True)
    source=qb.Circuit(1);source.add_capture(a)
    with pytest.raises(CircuitError):target.compose(source)


def test_capture_only_copy_and_drop_copy_have_distinct_scopes():
    source=qb.Circuit(1);a=source.add_var("a",True);s=source.add_stretch("s")
    captures=source.copy_empty_like(vars_mode="captures");dropped=source.copy_empty_like(vars_mode="drop")
    assert list(captures.iter_captured_vars())==[a] and list(captures.iter_captured_stretches())==[s]
    assert dropped.num_vars==dropped.num_stretches==0 and not dropped.operations


def test_capture_body_updates_survive_nested_while_and_if_scopes():
    target=qb.Circuit(1,1);n=target.add_var(ce.Var.new("n",ce.UInt(4)),0)
    body=target.copy_empty_like(vars_mode="captures").store(n,n+1).x(0)
    source=target.copy_empty_like(vars_mode="captures").while_loop(n<3,body)
    out=target.compose(source,inline_captures=True).measure(0,0)
    result=qb.DensityMatrixDevice().run_shots(out,shots=2,memory=True)
    assert result.counts()=={"1":2}
    assert all(memory["variables"][n.value[0]]["value"]==3 for memory in result.metadata()["classical_memory"])


def test_input_is_not_inlined_as_a_capture_even_when_explicitly_remapped():
    target=qb.Circuit(1);a=target.add_var("a",True)
    source=qb.Circuit(1);b=source.add_input("b",ce.Bool())
    with pytest.raises(CircuitError):target.compose(source,var_remap={b:a},inline_captures=True)


def test_scope_only_uninitialized_declaration_is_visible_in_actual_classical_state():
    circuit=qb.Circuit(1);a=ce.Var.new("a",ce.Bool());circuit.add_uninitialized_var(a)
    result=qb.StatevectorDevice().run(circuit)
    record=result.metadata()["classical_ensemble"][0]["variables"][a.value[0]]
    assert record["initialized"] is False and record["name"]=="a"


def test_nested_capture_does_not_declare_a_duplicate_runtime_variable():
    circuit=qb.Circuit(1,1);a=circuit.add_var("a",True)
    inner=circuit.copy_empty_like(vars_mode="captures").store(a,False)
    outer=circuit.copy_empty_like(vars_mode="captures").if_else(a,inner)
    result=circuit.compose(outer,inline_captures=True)
    assert qb.StatevectorDevice().run_shots(result.if_else(ce.logical_not(a),qb.Circuit(1,1).x(0)).measure(0,0),shots=2).counts()=={"1":2}


def test_capture_bool_assigned_from_a_mapped_measurement_is_runtime_data():
    target=qb.Circuit(2,2);flag=target.add_var("flag",False)
    source=qb.Circuit(1,1).x(0).measure(0,0);source.add_capture(flag)
    source.store(flag,ce.cast(ce.bit(0),ce.Bool()))
    out=target.compose(source,qubits=[1],clbits=[1],inline_captures=True)
    out=out.if_else(flag,qb.Circuit(2,2).x(0)).measure(0,0)
    assert qb.StatevectorDevice().run_shots(out,shots=3).counts()=={"11":3}


def test_invalid_empty_copy_mode_does_not_change_original_scope():
    circuit=qb.Circuit(1);a=circuit.add_var("a",True)
    with pytest.raises(ValueError):circuit.copy_empty_like(vars_mode="invalid")
    assert circuit.get_var("a") is a and len(circuit.operations)==1
