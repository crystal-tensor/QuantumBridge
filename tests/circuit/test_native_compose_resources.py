# Copyright 2026 QuantumBridge Contributors.
# Licensed under the Apache License, Version 2.0.
"""Construction must reject before copying, callbacks or partial mutation."""
import numpy as np
import pytest
import quantumbridge as qb
from quantumbridge.core import classical as ce
from quantumbridge.core.errors import CircuitError
from quantumbridge.core.gate_limits import GateCircuitLimits,gate_circuit_scope
from quantumbridge.execution import UnifiedResourceLedger,UnifiedExecutionLimits
from quantumbridge.execution.resource_context import ResourceScope


def scope():return ResourceScope(UnifiedResourceLedger(UnifiedExecutionLimits(max_total_memory_bytes=100000)))


def test_aggregate_operations_reject_before_native_copy(monkeypatch):
    import quantumbridge.execution.array_ownership as ownership
    source=qb.Circuit(1).x(0).h(0)
    monkeypatch.setattr(ownership,"native_configuration_copy",lambda *a,**k:pytest.fail("copy before work admission"))
    with gate_circuit_scope(GateCircuitLimits(max_total_operations=1)),pytest.raises(MemoryError):
        qb.Circuit(1).compose(source)


def test_nested_definitions_reject_before_copy_depth_limit():
    source=qb.Circuit(1).x(0)
    for index in range(4):source=qb.Circuit(1).compose(source,wrap=True)
    with gate_circuit_scope(GateCircuitLimits(max_definition_depth=2)),pytest.raises(MemoryError):qb.Circuit(1).compose(source)


def test_remap_count_is_admitted_before_unused_entries_are_ignored():
    source=qb.Circuit(1)
    with gate_circuit_scope(GateCircuitLimits(max_gate_parameters=2)),pytest.raises(MemoryError):
        qb.Circuit(1).compose(source,var_remap={"a":"b","c":"d","e":"f"})


def test_scope_count_rejects_before_allocating_replacement_identifiers():
    source=qb.Circuit(1)
    for name in ("a","b","c"):source.add_var(name,True)
    with gate_circuit_scope(GateCircuitLimits(max_gate_parameters=2)),pytest.raises(MemoryError):qb.Circuit(1).compose(source)


def test_target_numeric_metadata_copy_is_preallocated_and_atomic():
    target=qb.Circuit(1,metadata={"numeric":np.ones(8)}).h(0)
    ledger=UnifiedResourceLedger(UnifiedExecutionLimits(max_total_memory_bytes=63))
    with ResourceScope(ledger),pytest.raises(MemoryError):target.compose(qb.Circuit(1),inplace=True)
    assert [op.name for op in target.operations]==["h"] and ledger.receipt()["live_memory_bytes"]==0


def test_managed_foreign_metadata_is_rejected_without_deepcopy_callback():
    calls=[]
    class Foreign:
        def __deepcopy__(self,memo):calls.append("copy");return self
    source=qb.Circuit(1,metadata={"opaque":Foreign()})
    with scope(),pytest.raises(ce.UnsupportedFeature):qb.Circuit(1).compose(source)
    assert calls==[]


def test_managed_remap_mapping_subclass_is_not_iterated():
    calls=[]
    class Foreign(dict):
        def items(self):calls.append("items");return super().items()
    with scope(),pytest.raises(ce.UnsupportedFeature):qb.Circuit(1).compose(qb.Circuit(1),var_remap=Foreign())
    assert calls==[]


def test_managed_foreign_key_metaclass_is_not_hashed_or_compared():
    calls=[]
    class Meta(type):
        def __hash__(cls):calls.append("class-hash");return type.__hash__(cls)
        def __eq__(cls,other):calls.append("class-eq");return cls is other
    class Foreign(metaclass=Meta):pass
    mapping={Foreign():"name"};calls.clear()
    with scope(),pytest.raises((ce.UnsupportedFeature,CircuitError)):
        qb.Circuit(1).compose(qb.Circuit(1),var_remap=mapping)
    assert calls==[]


def test_managed_foreign_classical_expression_does_not_receive_remap_callback():
    from quantumbridge.core.control_flow import ControlBlock
    calls=[]
    class Foreign(ce.ClassicalExpression):
        def remap(self,*a,**k):calls.append("remap");return self
    source=qb.Circuit(1)
    source.operations.append(qb.Operation("control_flow",(),metadata={"control_node":ControlBlock("if",{
        "condition":Foreign("literal",ce.Bool(),value=True),"body":qb.Circuit(1).x(0),"alternate":None})}))
    with scope(),pytest.raises(ce.UnsupportedFeature):qb.Circuit(1).compose(source)
    assert calls==[]


def test_malformed_instruction_owner_cannot_be_normalized_into_valid_invocation():
    gate=qb.Circuit(1).rx(qb.Parameter("p"),0).to_gate()
    source=qb.Circuit(1)
    source.operations.append(qb.Operation(gate.name,(0,),params=(.7,),metadata={"gate":gate}))
    with pytest.raises(ValueError):qb.Circuit(1).compose(source,copy=False)


def test_parameter_namespace_conflict_is_atomic_before_inplace_copy():
    target=qb.Circuit(1).rx(qb.Parameter("same"),0)
    other=qb.Circuit(1).ry(qb.Parameter("same"),0)
    with pytest.raises(ValueError):target.compose(other,inplace=True)
    assert [op.name for op in target.operations]==["rx"]


def test_invalid_source_measurement_position_cannot_commit_half_a_composition():
    target=qb.Circuit(1,1).h(0);source=qb.Circuit(1,1).measure(0,0)
    source.measurements[0].metadata["operation_index"]=-1
    with pytest.raises(ValueError):target.compose(source,inplace=True,front=True)
    assert [op.name for op in target.operations]==["h"] and not target.measurements


def test_duplicate_quantum_mapping_rejects_without_modifying_target():
    target=qb.Circuit(2).h(0)
    with pytest.raises(ValueError):target.compose(qb.Circuit(2).cx(0,1),qubits=[1,1],inplace=True)
    assert len(target.operations)==1


def test_cyclic_control_graph_rejects_without_recursive_copy():
    from quantumbridge.core.control_flow import ControlBlock
    source=qb.Circuit(1)
    source.operations.append(qb.Operation("control_flow",(),metadata={"control_node":ControlBlock("while",{
        "condition":ce.literal(True),"body":source})}))
    with pytest.raises(ValueError,match="Cyclic"):qb.Circuit(1).compose(source)


def test_wrap_does_not_erase_scope_to_look_like_a_unitary_gate():
    source=qb.Circuit(1);source.add_var("a",True)
    target=qb.Circuit(1).h(0)
    with pytest.raises(ValueError):target.compose(source,wrap=True,inplace=True)
    assert len(target.operations)==1 and target.num_vars==0
