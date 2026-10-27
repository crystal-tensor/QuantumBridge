# Copyright 2026 QuantumBridge Contributors.
# Licensed under the Apache License, Version 2.0.
"""Native IR retains invalidated numeric history without activating stale plans."""
import numpy as np
import pytest
import quantumbridge as qb
from quantumbridge.ir.qb_ir import IRProgram
from quantumbridge.compat.qiskit_adapter import circuit_from_ir
from quantumbridge.information import Operator
from quantumbridge.core.instruction_parameters import definition_signature


def edited(kind):
    p=qb.ParameterVector("angle",1)[0]
    body=qb.QuantumCircuit(1,name="body",global_phase=p/5);body.rx(2*p,0)
    owner=getattr(body,"to_gate" if kind=="gate" else "to_instruction")(parameter_map={p:.4})
    owner.definition.rz(.23,0)
    circuit=qb.QuantumCircuit(1);circuit.append(owner,[0],copy=False)
    return circuit,owner


def record(payload,kind):return payload["instructions"][0]["metadata"]["gate" if kind=="gate" else "instruction_object"]


@pytest.mark.parametrize("kind",["gate","instruction"])
def test_ir_transports_current_numeric_definition_and_explicitly_invalidated_formal_history(kind):
    source,owner=edited(kind);original_plan=owner._parameter_plan
    assert original_plan.signature!=definition_signature(owner.definition)
    payload=source.to_ir().to_dict()
    assert record(payload,kind)["parameter_binding"]["invalidated"] is True
    restored=circuit_from_ir(IRProgram.from_json(IRProgram.from_dict(payload).to_json()))
    clone=restored.operations[0].metadata["gate" if kind=="gate" else "instruction_object"]
    assert clone._parameter_plan.signature!=definition_signature(clone.definition)
    assert clone._parameter_plan.formals[0].uuid==original_plan.formals[0].uuid
    assert source.parameters==restored.parameters==()
    expected=np.diag([np.exp(-.115j),np.exp(.115j)])@(
        np.exp(.08j)*np.array([[np.cos(.4),-1j*np.sin(.4)],[-1j*np.sin(.4),np.cos(.4)]]))
    np.testing.assert_allclose(Operator(source).data,expected,atol=9e-13,rtol=0)
    np.testing.assert_allclose(Operator(restored).data,expected,atol=9e-13,rtol=0)
    for operation in (owner,clone):
        before=operation._parameter_plan
        with pytest.raises(ValueError,match="explicit symbolic formals"):operation.params=[.7]
        assert operation.params==[.4] and operation._parameter_plan is before
    assert owner._parameter_plan is original_plan


@pytest.mark.parametrize("kind",["gate","instruction"])
@pytest.mark.parametrize("change",["missing","false","string","stale_template"])
def test_invalidated_history_record_cannot_be_forged_into_an_active_or_unchecked_plan(kind,change):
    source,_=edited(kind);payload=source.to_ir().to_dict();binding=record(payload,kind)["parameter_binding"]
    if change=="missing":del binding["invalidated"]
    elif change=="false":binding["invalidated"]=False
    elif change=="string":binding["invalidated"]="true"
    else:
        binding["definition"]=record(payload,kind)["definition"]
    with pytest.raises(ValueError):IRProgram.from_dict(payload)


@pytest.mark.parametrize("kind",["gate","instruction"])
def test_valid_plan_cannot_claim_to_be_invalidated_to_bypass_definition_validation(kind):
    p=qb.Parameter("p");body=qb.QuantumCircuit(1);body.rx(p,0)
    owner=getattr(body,"to_gate" if kind=="gate" else "to_instruction")(parameter_map={p:.4})
    source=qb.QuantumCircuit(1);source.append(owner,[0])
    payload=source.to_ir().to_dict();record(payload,kind)["parameter_binding"]["invalidated"]=True
    with pytest.raises(ValueError):IRProgram.from_dict(payload)
