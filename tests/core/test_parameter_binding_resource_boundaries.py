# Copyright 2026 QuantumBridge Contributors.
# Licensed under the Apache License, Version 2.0.
"""Admission, atomic failure and reuse for parameterized native objects."""

import gc
from copy import deepcopy

import numpy as np
import pytest

from quantumbridge import Circuit, Instruction, Parameter, ParameterVector
from quantumbridge.core.classical import UnsupportedFeature
from quantumbridge.execution import UnifiedExecutionLimits as Limits, UnifiedResourceLedger as Ledger
from quantumbridge.execution.resource_context import ResourceScope
from quantumbridge.information import Operator
from quantumbridge.ir.qb_ir import IRProgram
from quantumbridge.serialization.errors import ResourceLimitError
from quantumbridge.serialization.limits import SerializationLimits


def vector_document(length=4):
    vector=ParameterVector("angles",length)
    return Circuit(1).rx(vector[0],0).to_ir().to_dict()


def watch_vector_allocation(monkeypatch, maximum):
    original=ParameterVector.resize
    allocated=[]
    def resize(vector,length):
        if length:
            allocated.append(length)
            assert sum(allocated)<=maximum,"Vector allocated before input validation/admission"
        return original(vector,length)
    monkeypatch.setattr(ParameterVector,"resize",resize)
    return allocated


@pytest.mark.parametrize("corruption",["uuid","name"])
def test_invalid_ir_vector_identity_rejects_before_vector_factory(monkeypatch,corruption):
    document=vector_document()
    parameter=document["instructions"][0]["params"][0]
    parameter["parameter_uuid" if corruption=="uuid" else "parameter"]="invalid"
    allocated=watch_vector_allocation(monkeypatch,0)
    with pytest.raises(ValueError):IRProgram.from_dict(document)
    assert allocated==[]


def test_ir_distinct_roots_share_one_vector_allocation_budget(monkeypatch):
    first,second=ParameterVector("a",2),ParameterVector("b",2)
    document=Circuit(1).rx(first[0],0).ry(second[0],0).to_ir().to_dict()
    recovery=vector_document(1)
    allocated=watch_vector_allocation(monkeypatch,3)
    with pytest.raises(ResourceLimitError):
        IRProgram.from_dict(document,serialization_limits=SerializationLimits(max_parameter_nodes=3))
    assert allocated==[2]
    allocated.clear()
    recovered=IRProgram.from_dict(recovery,serialization_limits=SerializationLimits(max_parameter_nodes=3))
    assert len(recovered.instructions)==1


@pytest.mark.parametrize("location",["instruction_metadata","nested_control","loop_parameter"])
def test_ir_vector_limits_reach_provenance_and_control_bodies(monkeypatch,location):
    body=vector_document(4)
    parent=Circuit(1).x(0).to_ir().to_dict()
    if location=="instruction_metadata":
        parent["instructions"][0]["metadata"]["instruction"]={"params":[body["instructions"][0]["params"][0]]}
    else:
        parameter=None
        if location=="loop_parameter":
            value=body["instructions"][0]["params"][0]
            parameter={"loop_parameter":value["parameter"],"loop_parameter_uuid":value["parameter_uuid"],
                "loop_parameter_vector":value["parameter_vector"]}
            body=Circuit(1).to_ir().to_dict()
        parent["instructions"][0]["metadata"]["control_node"]={
            "version":"qb-control-v1","kind":"for",
            "data":{"values":[1],"variable":None,"parameter":parameter,"body":{"circuit":body}}}
    allocated=watch_vector_allocation(monkeypatch,0)
    with pytest.raises(ResourceLimitError):
        IRProgram.from_dict(parent,serialization_limits=SerializationLimits(max_parameter_nodes=3))
    assert allocated==[]


def test_ir_parent_and_nested_roots_share_one_vector_allocation_budget(monkeypatch):
    first,second=ParameterVector("a",2),ParameterVector("b",2)
    parent=Circuit(1).rx(first[0],0).to_ir().to_dict()
    body=Circuit(1).ry(second[0],0).to_ir().to_dict()
    parent["instructions"][0]["metadata"]["control_node"]={
        "version":"qb-control-v1","kind":"for",
        "data":{"values":[1],"variable":None,"parameter":None,"body":{"circuit":body}}}
    allocated=watch_vector_allocation(monkeypatch,3)
    with pytest.raises(ResourceLimitError):
        IRProgram.from_dict(parent,serialization_limits=SerializationLimits(max_parameter_nodes=3))
    assert allocated==[2]


def test_instruction_copy_reserves_before_array_factory():
    source=np.eye(4,dtype=complex)
    instruction=Instruction("custom",2,metadata={"matrix":source})
    ledger=Ledger(Limits(max_total_memory_bytes=source.nbytes-1))
    with ResourceScope(ledger),pytest.raises(MemoryError):instruction.copy()
    assert ledger.receipt()["live_memory_bytes"]==0


def test_instruction_copy_retains_array_view_and_recovers_after_limit():
    source=np.eye(4,dtype=complex)
    instruction=Instruction("custom",2,metadata={"matrix":source})
    ledger=Ledger(Limits(max_total_memory_bytes=source.nbytes))
    with ResourceScope(ledger):copied=instruction.copy("renamed")
    assert copied.name=="renamed"
    assert not np.shares_memory(source,copied.metadata["matrix"])
    view=copied.metadata["matrix"][:,0]
    del copied
    gc.collect()
    assert ledger.receipt()["live_memory_bytes"]==source.nbytes
    with ResourceScope(ledger),pytest.raises(MemoryError):instruction.copy()
    del view
    gc.collect()
    assert ledger.receipt()["live_memory_bytes"]==0
    with ResourceScope(ledger):recovered=instruction.copy()
    np.testing.assert_array_equal(recovered.metadata["matrix"],source)


def test_managed_instruction_copy_rejects_foreign_copy_protocol():
    class Foreign:
        def __deepcopy__(self,memo):pytest.fail("Foreign copy protocol executed")
    instruction=Instruction("custom",1,metadata={"foreign":Foreign()})
    with ResourceScope(Ledger()),pytest.raises(UnsupportedFeature):instruction.copy()


def test_failed_bindings_preserve_original_and_reused_instruction_results():
    angle=Parameter("angle")
    instruction=Circuit(1).rx(angle,0).ry(angle*angle,0).to_instruction()
    parent=Circuit(2).append(instruction,(1,)).append(instruction.copy(),(0,))
    before=deepcopy(parent.to_ir().to_dict())
    results=[]
    for value in (.2,-.7,.8):
        results.append(Operator(parent.bind({angle:value})).data)
        for invalid in ({angle:object()},{angle:.2,"unknown":.5},[],{angle:1j}):
            with pytest.raises((ValueError,TypeError,UnsupportedFeature)):
                parent.assign_parameters(invalid,inplace=True)
            assert parent.to_ir().to_dict()==before
    assert all(np.max(np.abs(results[index]-results[index+1]))>.01 for index in (0,1))
    np.testing.assert_array_equal(Operator(parent.bind({angle:.2})).data,results[0])
    assert instruction.definition.parameters==(angle,)


def test_managed_binding_rejects_foreign_array_and_mapping_before_callbacks():
    class ForeignArray:
        def __array__(self,*args,**kwargs):pytest.fail("Foreign array protocol executed")
    class ForeignMapping(dict):
        def items(self):pytest.fail("Foreign mapping protocol executed")
        def __iter__(self):pytest.fail("Foreign mapping iteration executed")
    angle=Parameter("angle")
    parent=Circuit(1).rx(angle,0)
    with ResourceScope(Ledger()):
        for invalid in ({angle:ForeignArray()},ForeignMapping({angle:.2})):
            with pytest.raises((ValueError,TypeError,UnsupportedFeature)):
                parent.assign_parameters(invalid,inplace=True)
    assert parent.parameters==(angle,)
