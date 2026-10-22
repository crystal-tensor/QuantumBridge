# Copyright 2026 QuantumBridge Contributors.
# Licensed under the Apache License, Version 2.0.
"""Explicit operation sharing and independent snapshots with live owners."""
import gc
import numpy as np
import pytest
import quantumbridge as qb
from quantumbridge.information import Operator
from quantumbridge.serialization import qpy_dumps,qpy_loads
from quantumbridge.execution import UnifiedResourceLedger, UnifiedExecutionLimits
from quantumbridge.execution.resource_context import ResourceScope


def source_gate():
    p=qb.Parameter("p")
    gate=qb.Circuit(1,name="custom").ry(p,0).to_gate().assign_parameters({p:.2})
    source=qb.Circuit(1).append(gate,[0])
    return source,source.operations[0].metadata["gate"]


def ry(angle):
    c,s=np.cos(angle/2),np.sin(angle/2)
    return np.array([[c,-s],[s,c]])


def test_copy_false_reuses_custom_operation_and_executes_live_updates():
    source,gate=source_gate();out=qb.Circuit(1).compose(source,copy=False)
    assert out.operations[0].metadata["gate"] is gate
    gate.params[0]=.7
    assert out.operations[0].params==(.7,)
    np.testing.assert_allclose(Operator(out).data,ry(.7),atol=4e-13,rtol=0)


def test_copy_true_isolates_source_mutation_and_definition_binding():
    source,gate=source_gate();out=qb.Circuit(1).compose(source,copy=True)
    assert out.operations[0].metadata["gate"] is not gate
    gate.params[0]=.7
    np.testing.assert_allclose(Operator(out).data,ry(.2),atol=4e-13,rtol=0)


def test_source_invocation_parameter_index_tracks_its_exposed_mutable_gate():
    source,gate=source_gate();p=qb.Parameter("new")
    gate.params[0]=p
    assert source.parameters==(p,)
    out=qb.Circuit(1).compose(source,copy=False).bind({p:.4})
    np.testing.assert_allclose(Operator(out).data,ry(.4),atol=4e-13,rtol=0)


def test_two_compositions_share_one_live_owner_not_list_storage():
    source,gate=source_gate()
    left=qb.Circuit(1).compose(source,copy=False);right=qb.Circuit(1).compose(source,copy=False)
    left.x(0);assert len(right.operations)==1 and len(source.operations)==1
    gate.params[0]=.6
    assert right.operations[0].params==(.6,)


def test_shared_output_retains_owner_after_source_lifetime_ends():
    source,gate=source_gate();out=qb.Circuit(1).compose(source,copy=False)
    del source,gate;gc.collect()
    np.testing.assert_allclose(Operator(out).data,ry(.2),atol=4e-13,rtol=0)


def test_copy_of_shared_output_takes_an_independent_owner_snapshot():
    source,gate=source_gate();out=qb.Circuit(1).compose(source,copy=False)
    snapshot=out.copy(name="snapshot");gate.params[0]=.9
    np.testing.assert_allclose(Operator(snapshot).data,ry(.2),atol=4e-13,rtol=0)
    np.testing.assert_allclose(Operator(out).data,ry(.9),atol=4e-13,rtol=0)


def test_invalid_live_parameter_update_is_atomic_for_all_sharing_circuits():
    source,gate=source_gate();out=qb.Circuit(1).compose(source,copy=False)
    with pytest.raises((TypeError,ValueError)):gate.params[0]="not a native parameter"
    assert source.operations[0].params==(.2,) and out.operations[0].params==(.2,)


def test_shared_custom_gate_qpy_uses_current_params_for_both_source_and_output():
    source,gate=source_gate();out=qb.Circuit(1).compose(source,copy=False);gate.params[0]=.8
    for circuit in (source,out):
        restored=qpy_loads(qpy_dumps(circuit))[0]
        np.testing.assert_allclose(Operator(restored).data,ry(.8),atol=4e-13,rtol=0)


def test_copy_false_borrows_owned_matrix_storage_without_unaccounted_copy():
    from quantumbridge.core.standard_gates import UnitaryGate
    source=qb.Circuit(1).append(UnitaryGate(np.array([[0,1],[1,0]])),[0])
    ledger=UnifiedResourceLedger(UnifiedExecutionLimits(max_total_memory_bytes=66))
    with ResourceScope(ledger):out=qb.Circuit(1).compose(source,copy=False)
    assert out.operations[0].metadata["gate"] is source.operations[0].metadata["gate"]
    assert ledger.receipt()["live_memory_bytes"]==0
    np.testing.assert_allclose(Operator(out).data,[[0,1],[1,0]],atol=4e-13,rtol=0)


def test_wrap_hierarchy_decomposes_one_level_at_a_time():
    inner=qb.Circuit(1,name="inner").h(0).rz(.2,0)
    middle=qb.Circuit(1,name="middle").compose(inner,wrap=True)
    outer=qb.Circuit(1).compose(middle,wrap=True)
    first=outer.decompose(reps=1);second=outer.decompose(reps=2)
    assert len(first.operations)==1 and first.operations[0].metadata["gate"].name=="inner"
    assert [op.name for op in second.operations]==["h","rz"]
    np.testing.assert_allclose(Operator(outer).data,Operator(second).data,atol=4e-13,rtol=0)


def test_direct_gate_copy_false_reuses_the_given_operation_not_an_intermediate_snapshot():
    p=qb.Parameter("p");gate=qb.Circuit(1).ry(p,0).to_gate().assign_parameters({p:.2})
    out=qb.Circuit(1).compose(gate,copy=False)
    assert out.operations[0].metadata["gate"] is gate
    gate.params[0]=.6
    np.testing.assert_allclose(Operator(out).data,ry(.6),atol=4e-13,rtol=0)


def test_direct_opaque_gate_wrap_flag_does_not_create_a_fake_definition():
    gate=qb.Gate("opaque",1,[.2])
    out=qb.Circuit(1).compose(gate,copy=False,wrap=True)
    assert out.operations[0].metadata["gate"] is gate and gate.definition is None
    with pytest.raises((ValueError,qb.UnsupportedFeature)):Operator(out)


def test_direct_annotation_is_a_real_borrowed_operation_with_executable_modifiers():
    from quantumbridge.core.standard_gates import RYGate
    annotation=qb.AnnotatedOperation(RYGate(.3),[qb.InverseModifier()])
    out=qb.Circuit(1).compose(annotation)
    assert out.operations[0].metadata["annotated_operation"] is annotation
    np.testing.assert_allclose(Operator(out).data,ry(-.3),atol=4e-13,rtol=0)
