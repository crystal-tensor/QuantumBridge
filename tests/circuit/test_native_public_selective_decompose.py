# Copyright 2026 QuantumBridge Contributors.
# Licensed under the Apache License, Version 2.0.
"""Selective decomposition remains layered, bounded and phase exact."""
import numpy as np
import pytest
import quantumbridge as qb
from quantumbridge.core.gate_limits import GateCircuitLimits,gate_circuit_scope
from quantumbridge.information import Operator
from quantumbridge.qml import QNode


def source(kind):
    p=qb.Parameter("p");leaf=qb.QuantumCircuit(1,name="leaf",global_phase=.1);leaf.ry(p,0)
    owner=getattr(leaf,"to_"+kind)(label="inner")
    middle=qb.QuantumCircuit(1,name="outer",global_phase=.3);middle.append(owner,[0])
    result=qb.QuantumCircuit(3,global_phase=.2)
    result.append(getattr(middle,"to_"+kind)(label="chosen"),[2])
    return result,p


@pytest.mark.parametrize("kind",["gate","instruction"])
@pytest.mark.parametrize("reps",[1,2])
@pytest.mark.parametrize("selection",["all","name","label","pattern","type","mixed","unselected"])
def test_public_selective_decompose_preserves_layer_depth_and_independent_complex_math(kind,reps,selection):
    circuit,p=source(kind)
    selector={"all":None,"name":"outer","label":"chosen","pattern":"out*",
        "type":qb.Gate if kind=="gate" else qb.Instruction,"mixed":["chosen","leaf"],"unselected":"absent"}[selection]
    out=circuit.decompose(selector,reps=reps)
    assert type(out) is qb.QuantumCircuit and out.parameters==(p,) and out.qubits==circuit.qubits
    expected_name="outer" if selection=="unselected" else "ry" if reps==2 and selection in {"all","type","mixed"} else "leaf"
    assert len(out.data)==1 and out.data[0].name==expected_name
    x=.3;rotation=np.array([[np.cos(x/2),-np.sin(x/2)],[np.sin(x/2),np.cos(x/2)]])
    np.testing.assert_allclose(Operator(out.assign_parameters({p:x})).data,
        np.exp(.6j)*np.kron(np.eye(4),rotation),atol=7e-13,rtol=0)
    assert circuit.data[0].name=="outer" and circuit.global_phase==.2


@pytest.mark.parametrize("kind",["gate","instruction"])
def test_layered_decomposition_bind_inverse_keeps_real_analytic_higher_derivatives(kind):
    circuit,p=source(kind);out=circuit.decompose(reps=2).inverse()
    node=QNode.from_circuit(out,qb.PauliZ(2),diff_method="parameter-shift",max_diff=2)
    x=.3
    assert node(x)==pytest.approx(np.cos(x),abs=3e-12)
    assert node.compute_jacobian(x)==pytest.approx(-np.sin(x),abs=3e-10)
    assert node.compute_hvp(.7,x)==pytest.approx(-.7*np.cos(x),abs=5e-10)


def test_same_name_custom_gate_uses_its_real_body_not_the_standard_recipe():
    body=qb.QuantumCircuit(1,global_phase=.2);body.x(0)
    owner=body.to_gate(_name="ry");c=qb.QuantumCircuit(1);c.append(owner,[0])
    out=c.decompose("ry")
    assert out.data[0].name=="x"
    np.testing.assert_allclose(Operator(out).data,np.exp(.2j)*np.array([[0,1],[1,0]]),atol=4e-13,rtol=0)


@pytest.mark.parametrize("kind",["gate","instruction"])
def test_nested_decomposition_budget_precedes_the_initial_circuit_copy(kind,monkeypatch):
    circuit,p=source(kind)
    monkeypatch.setattr(qb.Circuit,"copy",lambda *a,**kw:pytest.fail("nested decompose copied before admission"))
    with gate_circuit_scope(GateCircuitLimits(max_decomposition_work=1)),pytest.raises(MemoryError):
        circuit.decompose(reps=1)


def test_selector_generator_budget_precedes_materialization_and_circuit_copy(monkeypatch):
    circuit,p=source("gate");consumed=[]
    def selectors():
        for i in range(100):consumed.append(i);yield "unselected"
    monkeypatch.setattr(qb.Circuit,"copy",lambda *a,**kw:pytest.fail("selectors copied before admission"))
    with gate_circuit_scope(GateCircuitLimits(max_decomposition_work=8)),pytest.raises(MemoryError):
        circuit.decompose(selectors())
    assert consumed==list(range(9))
