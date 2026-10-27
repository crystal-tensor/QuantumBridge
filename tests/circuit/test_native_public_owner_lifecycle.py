# Copyright 2026 QuantumBridge Contributors.
# Licensed under the Apache License, Version 2.0.
"""Frame admission rejects corrupted owners before copy or foreign callbacks."""
import numpy as np
import pytest
import quantumbridge as qb
from quantumbridge.core.operations import execution_operation
from quantumbridge.core.gate_limits import GateCircuitLimits,gate_circuit_scope
from quantumbridge.execution import UnifiedResourceLedger
from quantumbridge.execution.resource_context import ResourceScope
from quantumbridge.information import Operator


def source(kind="gate"):
    p=qb.Parameter("p");body=qb.Circuit(1).ry(p,0)
    gate=body.to_gate() if kind=="gate" else body.to_instruction()
    circuit=qb.QuantumCircuit(1);circuit.append(gate,[0],copy=False);gate.params[0]=.7
    return circuit,gate,p


@pytest.mark.parametrize("kind",["gate","instruction"])
def test_corrupted_owner_cycle_is_rejected_before_any_frame_owner_copy(kind,monkeypatch):
    circuit,gate,p=source(kind)
    key="gate" if kind=="gate" else "instruction_object"
    gate.definition.operations.append(qb.Operation("cycle",(0,),metadata={key:gate}))
    monkeypatch.setattr(type(gate),"copy",lambda *a,**kw:pytest.fail("cyclic frame copied"))
    with pytest.raises(ValueError,match="Cyclic"):execution_operation(circuit.operations[0])


@pytest.mark.parametrize("kind",["gate","instruction"])
def test_frame_rebinding_budget_is_checked_before_owner_copy(kind,monkeypatch):
    circuit,gate,p=source(kind)
    monkeypatch.setattr(type(gate),"copy",lambda *a,**kw:pytest.fail("frame copied before work admission"))
    with gate_circuit_scope(GateCircuitLimits(max_decomposition_work=1)),pytest.raises(MemoryError):
        execution_operation(circuit.operations[0])


@pytest.mark.parametrize("kind",["gate","instruction"])
def test_invalid_frame_width_is_rejected_before_owner_copy(kind,monkeypatch):
    circuit,gate,p=source(kind);object.__setattr__(circuit.operations[0],"targets",())
    monkeypatch.setattr(type(gate),"copy",lambda *a,**kw:pytest.fail("bad-width frame copied"))
    with pytest.raises(ValueError):execution_operation(circuit.operations[0])


def test_parameter_slot_budget_precedes_parameterized_public_append_copy(monkeypatch):
    gate=qb.Gate("opaque",1,[qb.Parameter("p"),qb.Parameter("q")]);circuit=qb.QuantumCircuit(1)
    monkeypatch.setattr(qb.Gate,"copy",lambda *a,**kw:pytest.fail("oversized params copied"))
    with gate_circuit_scope(GateCircuitLimits(max_gate_parameters=1)),pytest.raises(MemoryError):
        circuit.append(gate,[0])
    assert len(circuit.data)==0


@pytest.mark.parametrize("kind",["gate","instruction"])
def test_foreign_parameter_callbacks_are_rejected_before_managed_frame_copy(kind):
    circuit,gate,p=source(kind)
    class Trap:
        def __array__(self,*args,**kwargs):pytest.fail("foreign parameter array callback")
        def __deepcopy__(self,memo):pytest.fail("foreign parameter copy callback")
        def __eq__(self,other):pytest.fail("foreign parameter equality callback")
    object.__setattr__(gate,"_params",(Trap(),))
    with ResourceScope(UnifiedResourceLedger()),pytest.raises(qb.UnsupportedFeature):Operator(circuit)


@pytest.mark.parametrize("kind",["gate","instruction"])
def test_bound_handle_inverse_uses_the_stored_generic_parameter_frame(kind):
    circuit,gate,p=source(kind)
    handle=qb.InstructionSet.bound(circuit,[0]);handle.inverse()
    assert circuit.parameters==(p,)
    matrix=Operator(circuit.assign_parameters({p:.4})).data
    np.testing.assert_allclose(matrix,[[np.cos(.2),np.sin(.2)],[-np.sin(.2),np.cos(.2)]],atol=4e-13,rtol=0)
