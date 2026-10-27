# Copyright 2026 QuantumBridge Contributors.
# Licensed under the Apache License, Version 2.0.
"""Public bindings retain native atomicity, formal lineage and actual math."""
import numpy as np
import pytest
import quantumbridge as qb
from quantumbridge.core.gate_limits import GateCircuitLimits,gate_circuit_scope
from quantumbridge.execution import UnifiedResourceLedger
from quantumbridge.execution.resource_context import ResourceScope
from quantumbridge.information import Operator
from quantumbridge.ir.qb_ir import IRProgram
from quantumbridge.compat.qiskit_adapter import circuit_from_ir
from quantumbridge.serialization import qpy_dumps,qpy_loads


@pytest.mark.parametrize("case",["complex","nan","inf","object","unknown","unknown-string","flat-string",
    "vector-length","sequence-length"])
def test_failed_public_inplace_binding_leaves_the_whole_original_unchanged(case):
    vector=qb.ParameterVector("v",2);p=vector[0]
    circuit=qb.QuantumCircuit(1,name="original",global_phase=p/5,metadata={"note":[7]})
    circuit.ry(p,0);before=circuit.to_ir().to_dict()
    values={"complex":{p:1j},"nan":{p:np.nan},"inf":{p:np.inf},"object":{p:object()},
        "unknown":{qb.Parameter("v[0]"):.2},"unknown-string":{"unknown":.2},
        "flat-string":{"v[0]":.2},"vector-length":{vector:[.2]},"sequence-length":[]}[case]
    with pytest.raises((TypeError,ValueError,KeyError)):
        circuit.assign_parameters(values,inplace=True,flat_input=case=="flat-string")
    assert circuit.name=="original" and circuit.to_ir().to_dict()==before


@pytest.mark.parametrize("case",["mapping","sequence","generator"])
def test_public_binding_budgets_reject_before_circuit_copy(case,monkeypatch):
    p=qb.Parameter("p");c=qb.QuantumCircuit(1);c.ry(p,0)
    values={p:.2,qb.Parameter("extra"):.3} if case=="mapping" else [.2,.3]
    if case=="generator":values=(x for x in values)
    monkeypatch.setattr(qb.QuantumCircuit,"copy",lambda *a,**kw:pytest.fail("oversized binding copied the Circuit"))
    with gate_circuit_scope(GateCircuitLimits(max_gate_parameters=1)),pytest.raises(MemoryError):
        c.assign_parameters(values,strict=False)
    assert c.parameters==(p,)


def test_public_infinite_binding_iterable_stops_at_parameter_count_plus_one(monkeypatch):
    p=qb.Parameter("p");c=qb.QuantumCircuit(1);c.ry(p,0);consumed=[]
    def values():
        index=0
        while True:
            consumed.append(index);yield .2;index+=1
    monkeypatch.setattr(qb.QuantumCircuit,"copy",lambda *a,**kw:pytest.fail("invalid iterable copied the Circuit"))
    with pytest.raises(ValueError):c.assign_parameters(values())
    assert consumed==[0,1] and c.parameters==(p,)


@pytest.mark.parametrize("kind",["mapping","value"])
def test_managed_public_binding_rejects_foreign_callbacks_before_invocation(kind):
    class ForeignMapping(dict):
        def items(self):pytest.fail("foreign mapping callback")
        def __iter__(self):pytest.fail("foreign iteration callback")
    class ForeignValue:
        def __array__(self,*a,**kw):pytest.fail("foreign array callback")
        def __deepcopy__(self,memo):pytest.fail("foreign copy callback")
    p=qb.Parameter("p");c=qb.QuantumCircuit(1);c.ry(p,0)
    values=ForeignMapping({p:.2}) if kind=="mapping" else {p:ForeignValue()}
    with ResourceScope(UnifiedResourceLedger()),pytest.raises(qb.UnsupportedFeature):c.assign_parameters(values,inplace=True)
    assert c.parameters==(p,)


@pytest.mark.parametrize("vector",[False,True])
def test_public_parameter_query_is_a_safe_uuid_preserving_immutable_view(vector):
    p=qb.ParameterVector("v",1)[0] if vector else qb.Parameter("p")
    c=qb.QuantumCircuit(1);c.ry(p,0)
    stored=c.parameters[0]
    with ResourceScope(UnifiedResourceLedger()):
        view=c.get_parameter(p.name)
        assert c.has_parameter(view) and c.has_parameter(p.name) and not c.has_parameter(qb.Parameter(p.name))
    assert view==p and view is not p and view.uuid==p.uuid and type(view) is type(p)
    if vector:assert view.vector is stored.vector and view.index==stored.index


@pytest.mark.parametrize("kind",["gate","instruction"])
def test_public_conversion_parameter_map_keeps_a_deterministic_native_binding_plan(kind):
    p=qb.Parameter("p");source=qb.QuantumCircuit(1,name="source");source.ry(p,0)
    owner=getattr(source,"to_"+kind)(parameter_map={p:.2})
    parent=qb.QuantumCircuit(1);parent.append(owner,[0],copy=False)
    restored=circuit_from_ir(IRProgram.from_json(parent.to_ir().to_json()))
    q=qb.Parameter("replacement")
    stored=next(restored.iter_instructions()).metadata["gate" if kind=="gate" else "instruction_object"]
    stored.params=[q]
    # The decoded native Circuit has live owner semantics, not a public stale
    # invocation frame. Its binding plan must remain editable after transport.
    bound=restored.assign_parameters({q:.4})
    np.testing.assert_allclose(Operator(bound).data,[[np.cos(.2),-np.sin(.2)],[np.sin(.2),np.cos(.2)]],atol=4e-13,rtol=0)


@pytest.mark.parametrize("mapping_kind",["parameter","string","vector","sequence","flat"])
@pytest.mark.parametrize("transport",["direct","ir","qpy"])
def test_public_binding_source_frames_and_nested_phase_have_an_independent_complex_oracle(mapping_kind,transport):
    vector=qb.ParameterVector("v",1);p=vector[0];r=qb.QuantumRegister(1,"data")
    source=qb.QuantumCircuit(r,qb.QuantumRegister(name="alias",bits=[r[0]]),global_phase=p/5)
    source.ry(p,0);body=qb.QuantumCircuit(1,global_phase=p/7);body.ry(3*p,0)
    owner=body.to_gate();source.append(owner,[r[0]],copy=False);owner.params[0]=.7
    if transport=="ir":source=circuit_from_ir(IRProgram.from_json(source.to_ir().to_json()))
    elif transport=="qpy":source=qpy_loads(qpy_dumps(source))[0]
    parameter=source.parameters[0];x=.3
    values={"parameter":{parameter:x},"string":{parameter.name:x},"vector":{parameter.vector:[x]},
        "sequence":[x],"flat":{parameter:x}}[mapping_kind]
    if type(source) is qb.QuantumCircuit:out=source.assign_parameters(values,flat_input=mapping_kind=="flat")
    else:out=source.assign_parameters(values)
    expected=np.exp(1j*x*(1/5+1/7))*np.array([[np.cos(2*x),-np.sin(2*x)],[np.sin(2*x),np.cos(2*x)]])
    np.testing.assert_allclose(Operator(out).data,expected,atol=6e-13,rtol=0)
    assert not out.parameters and len(out.find_bit(out.qubits[0]).registers)==2
