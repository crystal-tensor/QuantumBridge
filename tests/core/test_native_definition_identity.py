# Copyright 2026 QuantumBridge Contributors. Apache-2.0.
"""Active object identity, shared-DAG accounting and transient owner lifetime."""

import gc

import numpy as np
import pytest

import quantumbridge as qb
from quantumbridge.core.gates import validate_definition
from quantumbridge.core.operations import instruction_definition_work
from quantumbridge.core import GateCircuitLimits,gate_circuit_scope


def shared_matrix_dag():
    inner=qb.QuantumCircuit(1)
    inner.unitary(np.array([[1,1j],[1j,1]])/np.sqrt(2),[0])
    leaf=inner.to_gate()
    root=qb.Circuit(1)
    operation=qb.Operation(leaf.name,(0,),metadata={"gate":leaf})
    root.operations.extend([operation,operation])
    assert root.operations[0].metadata["gate"] is root.operations[1].metadata["gate"]
    return root


@pytest.mark.parametrize("validator",[validate_definition,instruction_definition_work])
def test_shared_dag_counts_every_reference_at_exact_and_one_below_work(validator):
    source=shared_matrix_dag()
    with gate_circuit_scope(GateCircuitLimits(max_total_operations=6,max_custom_definitions=5,max_definition_depth=2)):
        assert validator(source)==6
    for limits in [GateCircuitLimits(max_total_operations=5),GateCircuitLimits(max_custom_definitions=4),
                   GateCircuitLimits(max_definition_depth=1)]:
        with gate_circuit_scope(limits),pytest.raises(MemoryError): validator(source)
    assert validator(source)==6


@pytest.mark.parametrize("kind",["gate","instruction"])
@pytest.mark.parametrize("indirect",[False,True])
def test_true_active_path_cycles_remain_rejected_before_copy(kind,indirect,monkeypatch):
    source=qb.Circuit(1).h(0)
    owner=source.to_gate() if kind=="gate" else source.to_instruction()
    key="gate" if kind=="gate" else "instruction_object"
    container=owner.definition
    if indirect:
        second=source.to_gate() if kind=="gate" else source.to_instruction()
        container.operations.append(qb.Operation(second.name,(0,),metadata={key:second}))
        container=second.definition
    container.operations.append(qb.Operation(owner.name,(0,),metadata={key:owner}))
    monkeypatch.setattr(type(owner),"copy",lambda *a,**k:pytest.fail("Cyclic owner was copied"))
    validator=validate_definition if kind=="gate" else instruction_definition_work
    with pytest.raises(ValueError,match="Cyclic"): validator(owner.definition,owner=owner)


def test_transient_execution_snapshot_graph_survives_collection_pressure(monkeypatch):
    import quantumbridge.core.gates as gates
    import quantumbridge.core.operations as operations
    original=operations.execution_operation
    def collect_after_snapshot(operation):
        result=original(operation)
        gc.collect()
        return result
    source=shared_matrix_dag()
    monkeypatch.setattr(gates,"execution_operation",collect_after_snapshot)
    monkeypatch.setattr(operations,"execution_operation",collect_after_snapshot)
    for _ in range(6):
        assert validate_definition(source)==6
        assert instruction_definition_work(source)==6
