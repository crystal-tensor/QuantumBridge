# Copyright 2026 QuantumBridge Contributors.
# Licensed under the Apache License, Version 2.0.
"""Public invocation slots feed the existing engines and survive real edits."""
import numpy as np
import pytest
import quantumbridge as qb
from quantumbridge.core.standard_gates import RYGate
from quantumbridge.information import Operator,Statevector,DensityMatrix,Clifford,Kraus
from quantumbridge.compat.qiskit_adapter import circuit_from_ir
from quantumbridge.ir.qb_ir import IRProgram
from quantumbridge.serialization import qpy_dumps,qpy_loads
from quantumbridge.execution import UnifiedResourceLedger,UnifiedExecutionLimits
from quantumbridge.execution.resource_context import ResourceScope


def ry(x):return np.array([[np.cos(x/2),-np.sin(x/2)],[np.sin(x/2),np.cos(x/2)]])


def managed():return ResourceScope(UnifiedResourceLedger(UnifiedExecutionLimits(max_total_memory_bytes=1000000)))


@pytest.mark.parametrize("symbolic",[False,True])
@pytest.mark.parametrize("action",["copy","bind","compose","compose-copy","inverse","handle-inverse","ir","qpy"])
def test_mutated_display_owner_and_cached_invocation_follow_observed_public_frames(symbolic,action):
    p=qb.Parameter("theta");gate=RYGate(p if symbolic else .3)
    circuit=qb.QuantumCircuit(1);handle=circuit.append(gate,[0],copy=False)
    gate.params[0]=.7
    if action=="copy":out=circuit.copy()
    elif action=="bind":out=circuit.assign_parameters({p:.4} if symbolic else {})
    elif action in {"compose","compose-copy"}:out=qb.QuantumCircuit(1).compose(circuit,copy=action=="compose-copy")
    elif action=="inverse":out=circuit.inverse()
    elif action=="handle-inverse":handle.inverse();out=circuit
    elif action=="ir":out=circuit_from_ir(IRProgram.from_json(circuit.to_ir().to_json()))
    else:out=qpy_loads(qpy_dumps(circuit))[0]
    if action in {"copy","bind","compose","compose-copy","inverse","handle-inverse"}:
        assert type(out) is qb.QuantumCircuit
    # Both installed public versions inverse the exposed owner, but copy/bind
    # reconstitute the invocation's cached params. These are distinct contracts.
    angle=-.7 if action in {"inverse","handle-inverse"} else .4 if symbolic else .3
    if out.parameters:out=out.assign_parameters({out.parameters[0]:.4})
    np.testing.assert_allclose(Operator(out).data,ry(angle),atol=3e-13,rtol=0)
    if action in {"copy","bind","compose-copy"}:
        assert out.data[0].params==list(out.data[0].operation.params)


@pytest.mark.parametrize("factory",[Operator,Statevector,DensityMatrix,Clifford,Kraus])
def test_public_native_class_is_admitted_by_existing_managed_information_engines(factory):
    circuit=qb.QuantumCircuit(1);circuit.h(0)
    with managed():out=factory(circuit)
    if factory is Operator:expected=np.array([[1,1],[1,-1]])/np.sqrt(2)
    elif factory is Statevector:expected=np.ones(2)/np.sqrt(2)
    elif factory is DensityMatrix:expected=np.ones((2,2))/2
    elif factory is Clifford:out=out.to_operator();expected=np.array([[1,1],[1,-1]])/np.sqrt(2)
    else:out=out.data[0];expected=np.array([[1,1],[1,-1]])/np.sqrt(2)
    np.testing.assert_allclose(out if factory is Kraus else out.data,expected,atol=3e-13,rtol=0)


@pytest.mark.parametrize("factory",[Operator,Statevector,DensityMatrix,Clifford,Kraus])
def test_unknown_public_subclass_cannot_gain_managed_array_callback_admission(factory):
    class Foreign(qb.QuantumCircuit):
        def __array__(self,*args,**kwargs):pytest.fail("foreign Circuit conversion")
    circuit=Foreign(1)
    with managed(),pytest.raises(qb.UnsupportedFeature):factory(circuit)


@pytest.mark.parametrize("directive",["barrier","delay"])
def test_public_directive_owner_lowers_in_the_existing_engine(directive):
    circuit=qb.QuantumCircuit(1);circuit.h(0)
    circuit.barrier() if directive=="barrier" else circuit.delay(3,0)
    np.testing.assert_allclose(qb.StatevectorDevice().statevector(circuit),np.ones(2)/np.sqrt(2),atol=3e-13,rtol=0)


def test_binding_preserves_actual_alias_graph_and_not_only_numeric_widths():
    a,b=qb.Qubit(),qb.Qubit();r=qb.QuantumRegister(name="r",bits=[a,b]);s=qb.QuantumRegister(name="s",bits=[b])
    circuit=qb.QuantumCircuit(r,s);p=qb.Parameter("p");circuit.ry(p,b)
    out=circuit.assign_parameters({p:.4})
    assert type(out) is qb.QuantumCircuit and out.qubits==[a,b]
    assert [(reg.name,index) for reg,index in out.find_bit(b).registers]==[("r",1),("s",0)]
    np.testing.assert_allclose(qb.StatevectorDevice().statevector(out),[np.cos(.2),np.sin(.2),0,0],atol=3e-13,rtol=0)


def test_public_inverse_result_keeps_its_new_standard_invocation_frame():
    circuit=qb.QuantumCircuit(1);circuit.ry(.3,0);out=circuit.inverse()
    out.data[0].operation.params[0]=.7
    assert out.data[0].params==[-.3]
    np.testing.assert_allclose(Operator(out).data,ry(-.3),atol=3e-13,rtol=0)
