# Copyright 2026 QuantumBridge Contributors.
# Licensed under the Apache License, Version 2.0.
"""Independent coherent derivative blocks and bounded native descriptor rules."""
import gc
import numpy as np
import pytest
import quantumbridge as qb
from quantumbridge.core.gate_limits import GateCircuitLimits,gate_circuit_scope
from quantumbridge.diff.adjoint import gate_derivative
from quantumbridge.execution import UnifiedExecutionLimits as Limits,UnifiedResourceLedger as Ledger
from quantumbridge.execution.resource_context import ResourceScope
from quantumbridge.qml import QNode


def operation(name,controls=0,inverses=()):
    metadata={}
    for inverse in inverses:
        metadata={"controlled_base":{"name":name,"metadata":metadata,"controls":1,"inverse":inverse}}
        name="native_controlled"
    if controls:
        metadata={"controlled_base":{"name":name,"metadata":metadata,"controls":controls}}
        name="native_controlled"
    return qb.Operation(name,(0,),(),(.37,),metadata)


def analytic(name,x):
    i=np.eye(2,dtype=complex)
    paulis={"x":np.array([[0,1],[1,0]]),"y":np.array([[0,-1j],[1j,0]]),"z":np.diag([1,-1])}
    if name in {"phase","p","u1","global_phase"}:
        return 1j*np.exp(1j*x)*(i if name=="global_phase" else np.diag([0,1]))
    generator=paulis[name[-1]]
    if name in {"rxx","ryy","rzz"}:generator=np.kron(generator,generator);i=np.eye(4)
    unitary=np.cos(x/2)*i-1j*np.sin(x/2)*generator
    return -.5j*generator@unitary


@pytest.mark.parametrize("name",["rx","ry","rz","phase","p","u1","rxx","ryy","rzz","global_phase","crx","cry","crz","cp","cphase"])
@pytest.mark.parametrize("controls,inverses",[(0,()),(2,()),(0,(True,)),(1,(True,True))])
def test_real_controlled_derivative_is_zero_off_active_subspace_and_matches_generator(name,controls,inverses):
    base={"crx":"rx","cry":"ry","crz":"rz","cp":"phase","cphase":"phase"}.get(name,name)
    local=analytic(base,.37)
    if sum(inverses)%2:local=local.conj().T
    count=controls+len(inverses)+int(base!=name)
    expected=np.zeros((len(local)*(1<<count),)*2,complex);expected[-len(local):,-len(local):]=local
    ledger=Ledger()
    with ResourceScope(ledger):result=gate_derivative(operation(name,controls,inverses),(.37,))
    np.testing.assert_allclose(result,expected,atol=2e-16,rtol=1e-15)
    assert ledger.receipt()["live_memory_bytes"]==result.nbytes
    view=result[-1:];del result;gc.collect()
    assert ledger.receipt()["live_memory_bytes"]==expected.nbytes
    del view;gc.collect()
    assert ledger.receipt()["live_memory_bytes"]==0


@pytest.mark.parametrize("name",["rx","phase","rxx","crz"])
def test_controlled_derivative_denies_memory_before_any_numeric_factory(name,monkeypatch):
    item=operation(name,2)
    def forbidden(*a,**kw):pytest.fail("controlled derivative allocated before admission")
    for key in ("array","empty","zeros","eye","diag","kron"):monkeypatch.setattr(np,key,forbidden)
    with ResourceScope(Ledger(Limits(max_total_memory_bytes=0))),pytest.raises(MemoryError):gate_derivative(item,(.37,))


@pytest.mark.parametrize("kind",["cycle","depth","controls","matrix","inverse","foreign"])
def test_malformed_or_unadmitted_derivative_descriptors_fail_before_numeric_work(kind,monkeypatch):
    item=operation("rx",1,(False,))
    limits=GateCircuitLimits()
    if kind=="cycle":item.metadata["controlled_base"]["metadata"]=item.metadata
    elif kind=="depth":limits=GateCircuitLimits(max_definition_depth=1)
    elif kind=="controls":limits=GateCircuitLimits(max_control_qubits=1)
    elif kind=="matrix":limits=GateCircuitLimits(max_matrix_dimension=4)
    elif kind=="inverse":item.metadata["controlled_base"]["inverse"]="true"
    else:
        class Foreign:
            def __contains__(self,key):pytest.fail("foreign descriptor callback")
        item.metadata["controlled_base"]["metadata"]=Foreign()
    monkeypatch.setattr(np,"empty",lambda *a,**kw:pytest.fail("invalid descriptor allocated"))
    from quantumbridge.core.classical import UnsupportedFeature
    with gate_circuit_scope(limits),pytest.raises((ValueError,MemoryError,UnsupportedFeature)):
        gate_derivative(item,(.37,))


@pytest.mark.parametrize("name",["rx","ry","rz","rxx","ryy","rzz"])
@pytest.mark.parametrize("method",["parameter-shift","adjoint"])
def test_controlled_rotation_interference_requires_half_frequency_first_and_second_rules(name,method):
    p=qb.Parameter("p");width=2 if len(name)==3 else 1
    source=qb.Circuit(2+width).h(0).x(1).append("native_controlled",tuple(range(2,2+width)),controls=(0,1),params=(p,),
        metadata={"controlled_base":{"name":name,"metadata":{},"controls":2}})
    if name in {"rz","rzz"}:source.h(2)
    node=QNode.from_circuit(source,qb.PauliX(0),max_diff=2,diff_method=method)
    x=.37
    assert node(x)==pytest.approx(np.cos(x/2),abs=3e-13)
    assert node.compute_jacobian(x)==pytest.approx(-.5*np.sin(x/2),abs=3e-11)
    assert node.compute_hessian(x)==pytest.approx(-.25*np.cos(x/2),abs=3e-11)
    assert node.compute_hvp(.7,x)==pytest.approx(-.175*np.cos(x/2),abs=3e-11)


def test_managed_derivative_strips_array_subclasses_without_foreign_dispatch():
    class Angles(np.ndarray):
        def __getitem__(self,key):pytest.fail("foreign angle indexing")
        def __array_ufunc__(self,*a,**kw):pytest.fail("foreign numeric dispatch")
    angles=np.array([.37]).view(Angles)
    with ResourceScope(Ledger()):actual=gate_derivative(operation("rx",2),angles)
    expected=np.zeros((8,8),complex);expected[-2:,-2:]=analytic("rx",.37)
    np.testing.assert_allclose(actual,expected,atol=2e-16,rtol=1e-15)


@pytest.mark.parametrize("location",["metadata","descriptor","parameters"])
def test_derivative_opaque_input_errors_precede_foreign_equality_and_length(location):
    class ForeignKey:
        def __hash__(self):return hash("controlled_base")
        def __eq__(self,other):pytest.fail("foreign descriptor key equality")
    class ForeignParameters:
        def __len__(self):pytest.fail("foreign angle length")
    item=operation("rx",2);parameters=(.37,)
    if location=="metadata":item.metadata.clear();item.metadata[ForeignKey()]=None
    elif location=="descriptor":item.metadata["controlled_base"]={ForeignKey():None}
    else:parameters=ForeignParameters()
    from quantumbridge.core.classical import UnsupportedFeature
    with ResourceScope(Ledger()),pytest.raises((ValueError,UnsupportedFeature)):
        gate_derivative(item,parameters)
