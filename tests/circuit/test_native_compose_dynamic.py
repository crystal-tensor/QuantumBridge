# Copyright 2026 QuantumBridge Contributors.
# Licensed under the Apache License, Version 2.0.
"""Ordered execution with measurement, loops and lexical boundaries."""
import numpy as np
import quantumbridge as qb
from quantumbridge.core import classical as ce


def test_front_measurement_precedes_target_condition_after_noncontiguous_mapping():
    source=qb.Circuit(1,1).x(0).measure(0,0)
    target=qb.Circuit(2,2).if_else(ce.bit(1),qb.Circuit(2,2).x(0)).measure(0,0)
    out=target.compose(source,qubits=[1],clbits=[1],front=True)
    assert qb.StatevectorDevice().run_shots(out,shots=5).counts()=={"11":5}


def test_back_measurement_does_not_retroactively_enable_an_earlier_condition():
    source=qb.Circuit(1,1).x(0).measure(0,0)
    target=qb.Circuit(2,2).if_else(ce.bit(1),qb.Circuit(2,2).x(0)).measure(0,0)
    out=target.compose(source,qubits=[1],clbits=[1])
    assert qb.StatevectorDevice().run_shots(out,shots=5).counts()=={"01":5}


def test_front_reset_happens_before_hadamard_not_after_it():
    target=qb.Circuit(1).h(0)
    front=target.compose(qb.Circuit(1).reset(0),front=True)
    back=target.compose(qb.Circuit(1).reset(0))
    np.testing.assert_allclose(qb.DensityMatrixDevice().density_matrix(front),np.full((2,2),.5),atol=2e-13,rtol=0)
    np.testing.assert_allclose(qb.DensityMatrixDevice().density_matrix(back),[[1,0],[0,0]],atol=2e-13,rtol=0)


def test_for_loop_body_quantum_and_classical_maps_are_both_preserved():
    source=qb.Circuit(1,1).store(ce.bit(0),1).for_loop(range(3),qb.Circuit(1,1).if_else(ce.bit(0),qb.Circuit(1,1).x(0))).measure(0,0)
    out=qb.Circuit(3,3).compose(source,qubits=[2],clbits=[1],front=True)
    assert qb.StatevectorDevice().run_shots(out,shots=3).counts()=={"010":3}


def test_while_counter_remap_rewrites_condition_body_and_final_classical_trace():
    source=qb.Circuit(1,1);n=source.add_var(ce.Var.new("n",ce.UInt(4)),0)
    body=qb.Circuit(1,1).store(n,n+1).x(0)
    source=source.while_loop(n<3,body).measure(0,0)
    out=qb.Circuit(2,2).compose(source,qubits=[1],clbits=[0],var_remap={"n":"iterations"})
    result=qb.DensityMatrixDevice().run_shots(out,shots=2,memory=True)
    assert result.counts()=={"10":2}
    assert all(record["variables"][out.get_var("iterations").value[0]]["value"]==3 for record in result.metadata()["classical_memory"])


def test_break_keeps_its_loop_scope_after_composition():
    source=qb.Circuit(1,1);n=source.add_var(ce.Var.new("n",ce.UInt(4)),0)
    body=qb.Circuit(1,1).store(n,n+1).if_else(n.eq(2),qb.Circuit(1,1).break_loop()).x(0)
    source=source.while_loop(n<5,body).measure(0,0)
    out=qb.Circuit(2,2).compose(source,qubits=[1],clbits=[1])
    result=qb.StatevectorDevice().run_shots(out,shots=2,memory=True)
    assert result.counts()=={"01":2}
    assert all(record["variables"][n.value[0]]["value"]==2 for record in result.metadata()["classical_memory"])


def test_continue_skips_only_the_selected_iteration_tail_after_remap():
    source=qb.Circuit(1,1);n=source.add_var(ce.Var.new("n",ce.UInt(4)),0)
    body=qb.Circuit(1,1).store(n,n+1).if_else((n&1).eq(1),qb.Circuit(1,1).continue_loop()).x(0)
    source=source.while_loop(n<4,body).measure(0,0)
    out=qb.Circuit(2,2).x(1).compose(source,qubits=[1],clbits=[1])
    assert qb.StatevectorDevice().run_shots(out,shots=2).counts()=={"01":2}


def test_switch_selector_and_case_bodies_share_the_rewritten_variable():
    source=qb.Circuit(1,1);selector=source.add_var(ce.Var.new("selector",ce.UInt(3)),2)
    source=source.switch(selector,{(1,2):qb.Circuit(1,1).x(0)},qb.Circuit(1,1).h(0)).measure(0,0)
    out=qb.Circuit(2,2).compose(source,qubits=[1],clbits=[0],var_remap={"selector":"choice"})
    assert qb.StatevectorDevice().run_shots(out,shots=3).counts()=={"10":3}


def test_nested_local_variables_do_not_escape_into_the_outer_runtime_store():
    body=qb.Circuit(1,1);local=body.add_var("local",True)
    body=body.if_else(local,qb.Circuit(1,1).x(0))
    source=qb.Circuit(1,1).if_else(True,body).measure(0,0)
    result=qb.StatevectorDevice().run_shots(qb.Circuit(1,1).compose(source),shots=2,memory=True)
    assert result.counts()=={"1":2}
    assert all(local.value[0] not in record["variables"] for record in result.metadata()["classical_memory"])


def test_nonunitary_wrapped_source_preserves_front_measurement_position():
    source=qb.Circuit(1,1).x(0).measure(0,0)
    target=qb.Circuit(2,2).if_else(ce.bit(1),qb.Circuit(2,2).x(0)).measure(0,0)
    out=target.compose(source,qubits=[1],clbits=[1],front=True,wrap=True)
    assert len(out.operations)==2
    assert qb.StatevectorDevice().run_shots(out,shots=2).counts()=={"11":2}


def test_inplace_self_composition_reads_one_stable_source_snapshot():
    source=qb.Circuit(1,name="self").h(0);source.global_phase=.17
    assert source.compose(source,inplace=True) is None
    assert len(source.operations)==2 and source.global_phase==.34
    np.testing.assert_allclose(qb.StatevectorDevice().statevector(source),[np.exp(.34j),0],atol=3e-13,rtol=0)


def test_compiler_preserves_typed_scope_and_classical_trace_after_composition():
    source=qb.Circuit(1,1);enabled=source.add_var("enabled",True)
    source=source.if_else(enabled,qb.Circuit(1,1).x(0).x(0).x(0)).measure(0,0)
    out=qb.Circuit(2,2).compose(source,qubits=[1],clbits=[1],var_remap={"enabled":"flag"})
    compiled=qb.transpile(out,optimization_level=2)
    assert compiled.get_var("flag")==out.get_var("flag")
    result=qb.DensityMatrixDevice().run_shots(compiled,shots=2,memory=True)
    assert result.counts()=={"01":2}
    assert all(record["variables"][out.get_var("flag").value[0]]["value"] is True for record in result.metadata()["classical_memory"])
