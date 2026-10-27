# Copyright 2026 QuantumBridge Contributors.
# Licensed under the Apache License, Version 2.0.
"""Controlled source/base/frame lifetimes and independent coherent math."""
from types import SimpleNamespace
import io
import numpy as np
import pytest
import quantumbridge as qb
from quantumbridge.information import Operator
from quantumbridge.serialization import qpy_dumps,qpy_loads
from quantumbridge.ir.qb_ir import IRProgram
from quantumbridge.compat.qiskit_adapter import circuit_from_ir
from quantumbridge.qml import QNode


MUTATIONS=("external_definition","owned_definition","nested_leaf","owner_params","controlled_definition")


def native_api():return SimpleNamespace(QC=qb.QuantumCircuit,P=qb.Parameter,O=Operator)


def build(a,mutation,symbolic=True,copy=False):
    p=a.P("p");leaf=a.QC(1,name="leaf");leaf.rx(2*p,0)
    body=a.QC(1,name="body",global_phase=p/5);body.append(leaf.to_gate(),[0])
    base=body.to_gate(parameter_map=None if symbolic else {p:.25})
    owner=base.control(2,ctrl_state="01",annotated=False)
    circuit=a.QC(3);circuit.append(owner,[0,1,2],copy=copy)
    value=p if symbolic else .25
    if mutation=="owner_params":owner.params=[.7]
    else:
        target=base if mutation=="external_definition" else owner if mutation=="controlled_definition" else owner.base_gate
        if mutation=="nested_leaf":target=target.definition.data[0].operation
        replacement=a.QC(target.num_qubits,global_phase=value/7);replacement.ry(3*value,target.num_qubits-1)
        target.definition=replacement
    return circuit,p,base,owner


def controlled_oracles(base,count,state):
    width=len(base);size=(1<<count)*width
    start=int(format(state,"0"+str(count)+"b")[::-1],2)*width
    block=np.eye(size,dtype=complex);block[start:start+width,start:start+width]=base
    projector=np.ones((1,1))
    for wire in range(count):projector=np.kron(projector,np.diag([0,1] if state>>wire&1 else [1,0]))
    algebra=np.eye(size)+np.kron(projector,base-np.eye(width))
    np.testing.assert_allclose(block,algebra,atol=1e-15,rtol=0)
    return block


def oracle(mutation,symbolic,copy,x):
    if mutation=="controlled_definition" and not (symbolic and copy):
        local=np.exp(1j*x/7)*np.array([[np.cos(1.5*x),-np.sin(1.5*x)],[np.sin(1.5*x),np.cos(1.5*x)]])
        return np.kron(np.eye(4),local)
    local=np.exp(1j*x/5)*np.array([[np.cos(x),-1j*np.sin(x)],[-1j*np.sin(x),np.cos(x)]])
    return controlled_oracles(local,2,1)


@pytest.mark.parametrize("mutation",MUTATIONS)
@pytest.mark.parametrize("symbolic",[False,True])
@pytest.mark.parametrize("copy",[False,True])
@pytest.mark.parametrize("action",["bind","inverse","nested","nested_qpy","ir","qpy"])
def test_controlled_base_lifetime_factories_binding_and_formats_keep_actual_operator(mutation,symbolic,copy,action,record_property):
    circuit,p,base,owner=build(native_api(),mutation,symbolic,copy)
    assert owner.base_gate is not base
    assert circuit.parameters==((p,) if symbolic else ())
    assert circuit.data[0].params==([p] if symbolic else [.25])
    x=.37 if symbolic else .25;expected=oracle(mutation,symbolic,copy,x)
    if action=="inverse":circuit=circuit.inverse();expected=expected.conj().T
    elif action in {"nested","nested_qpy"}:
        nested=circuit.to_gate().control(ctrl_state=0)
        circuit=qb.QuantumCircuit(4);circuit.append(nested,range(4));expected=controlled_oracles(expected,1,0)
        if action=="nested_qpy":circuit=qpy_loads(qpy_dumps(circuit))[0]
    elif action=="ir":circuit=circuit_from_ir(IRProgram.from_json(circuit.to_ir().to_json()))
    elif action=="qpy":circuit=qpy_loads(qpy_dumps(circuit))[0]
    mapping={circuit.parameters[0]:x} if symbolic else {}
    np.testing.assert_allclose(Operator(circuit.assign_parameters(mapping)).data,expected,atol=3e-12,rtol=0)


@pytest.mark.parametrize("mutation",MUTATIONS)
@pytest.mark.parametrize("symbolic",[False,True])
@pytest.mark.parametrize("copy",[False,True])
def test_actual_public_controlled_base_bound_operator_and_owner_lifetime(mutation,symbolic,copy,record_property):
    public=pytest.importorskip("qiskit")
    from qiskit.circuit import Parameter
    from qiskit.quantum_info import Operator as PublicOperator
    for api in (native_api(),SimpleNamespace(QC=public.QuantumCircuit,P=Parameter,O=PublicOperator)):
        circuit,p,base,owner=build(api,mutation,symbolic,copy)
        assert owner.base_gate is not base
        assert (circuit.data[0].operation is owner)==(not symbolic or not copy)
        assert tuple(value.name for value in circuit.parameters)==(("p",) if symbolic else ())
        matrix=api.O(circuit.assign_parameters({p:.37} if symbolic else {})).data
        if api.O is PublicOperator:
            order=[0,4,2,6,1,5,3,7];matrix=matrix[np.ix_(order,order)]
        np.testing.assert_allclose(matrix,oracle(mutation,symbolic,copy,.37 if symbolic else .25),atol=3e-12,rtol=0)
    record_property("contract","MATCH")


@pytest.mark.parametrize("mutation",["external_definition","owned_definition","nested_leaf","controlled_definition"])
@pytest.mark.parametrize("symbolic",[False,True])
@pytest.mark.parametrize("copy",[False,True])
@pytest.mark.parametrize("direction",["native-to-public","public-to-native"])
def test_actual_bilateral_qpy_controlled_base_graph_and_captured_math(mutation,symbolic,copy,direction,record_property):
    public=pytest.importorskip("qiskit")
    from qiskit.circuit import Parameter
    from qiskit.quantum_info import Operator as PublicOperator
    from qiskit import qpy
    source,p,_,_=build(native_api() if direction=="native-to-public" else SimpleNamespace(
        QC=public.QuantumCircuit,P=Parameter,O=PublicOperator),mutation,symbolic,copy)
    if direction=="native-to-public":
        restored=qpy.load(io.BytesIO(qpy_dumps(source)))[0]
        mapping={next(iter(restored.parameters)):.37} if symbolic else {}
        matrix=PublicOperator(restored.assign_parameters(mapping)).data
        order=[0,4,2,6,1,5,3,7];matrix=matrix[np.ix_(order,order)]
    else:
        stream=io.BytesIO();qpy.dump(source,stream,version=13)
        restored=qpy_loads(stream.getvalue())[0]
        mapping={restored.parameters[0]:.37} if symbolic else {}
        matrix=Operator(restored.assign_parameters(mapping)).data
    np.testing.assert_allclose(matrix,oracle(mutation,symbolic,copy,.37 if symbolic else .25),atol=3e-12,rtol=0)
    record_property("contract","MATCH")


@pytest.mark.parametrize("transport",["direct","ir","qpy"])
@pytest.mark.parametrize("method",["parameter-shift","adjoint"])
def test_cached_two_control_base_mutation_retains_jacobian_hessian_and_hvp(transport,method):
    circuit,p,_,_=build(native_api(),"owned_definition")
    if transport=="ir":circuit=circuit_from_ir(IRProgram.from_json(circuit.to_ir().to_json()))
    elif transport=="qpy":circuit=qpy_loads(qpy_dumps(circuit))[0]
    prepared=qb.QuantumCircuit(3);prepared.h(0);prepared.compose(circuit,inplace=True)
    node=QNode.from_circuit(prepared,qb.PauliX(0),diff_method=method,max_diff=2)
    x=.37;k=.2
    assert node(x)==pytest.approx(np.cos(x)*np.cos(k*x),abs=5e-12)
    assert node.compute_jacobian(x)==pytest.approx(-np.sin(x)*np.cos(k*x)-k*np.cos(x)*np.sin(k*x),abs=7e-10)
    second=-(1+k*k)*np.cos(x)*np.cos(k*x)+2*k*np.sin(x)*np.sin(k*x)
    assert node.compute_hessian(x)==pytest.approx(second,abs=9e-10)
    assert node.compute_hvp(.7,x)==pytest.approx(.7*second,abs=9e-10)


@pytest.mark.parametrize("transport",["direct","ir","qpy"])
def test_hundred_wire_nested_controlled_base_history_has_actual_nondense_mps_hvp(transport,monkeypatch):
    from quantumbridge.information.matrix_product_state import MatrixProductState
    circuit,p,_,_=build(native_api(),"owned_definition")
    nested=circuit.to_gate().control(ctrl_state=0)
    source=qb.QuantumCircuit(100);source.h(0);source.x(1);source.append(nested,[0,1,2,3])
    if transport=="ir":source=circuit_from_ir(IRProgram.from_json(source.to_ir().to_json()))
    elif transport=="qpy":source=qpy_loads(qpy_dumps(source))[0]
    def forbidden(*a,**kw):pytest.fail("nested hundred-wire control used dense expansion")
    for cls,name in ((qb.Gate,"to_matrix"),(qb.StatevectorDevice,"statevector"),
            (qb.DensityMatrixDevice,"density_matrix"),(MatrixProductState,"statevector"),
            (MatrixProductState,"reduced_density_matrix")):
        monkeypatch.setattr(cls,name,forbidden)
    node=QNode.from_circuit(source,qb.PauliX(0),device=qb.MatrixProductStateDevice(
        max_memory_mb=2,max_bond_dim=8,cutoff=0),max_diff=2,diff_method="parameter-shift")
    x=.37;k=.2
    assert node(x)==pytest.approx(np.cos(x)*np.cos(k*x),abs=7e-12)
    assert node.compute_jacobian(x)==pytest.approx(-np.sin(x)*np.cos(k*x)-k*np.cos(x)*np.sin(k*x),abs=9e-10)
    second=-(1+k*k)*np.cos(x)*np.cos(k*x)+2*k*np.sin(x)*np.sin(k*x)
    assert node.compute_hvp(.7,x)==pytest.approx(.7*second,abs=2e-9)


@pytest.mark.parametrize("framework",["torch","autograd","jax","tensorflow"])
@pytest.mark.parametrize("method",["parameter-shift","adjoint"])
def test_two_control_phase_interference_runs_actual_framework_first_and_second_rules(framework,method):
    module=pytest.importorskip(framework)
    circuit,p,_,_=build(native_api(),"owned_definition")
    prepared=qb.QuantumCircuit(3);prepared.h(0);prepared.compose(circuit,inplace=True)
    node=QNode.from_circuit(prepared,qb.PauliX(0),interface=framework,diff_method=method,max_diff=2)
    x=.37;k=.2
    if framework=="torch":
        value=module.tensor(x,dtype=module.float64,requires_grad=True)
        result=node(value);first=module.autograd.grad(result,value,create_graph=True)[0]
        actual=(float(result.detach()),float(first.detach()),float(module.autograd.grad(first,value)[0]))
    elif framework=="autograd":actual=(node(x),module.grad(node)(x),module.grad(module.grad(node))(x))
    elif framework=="jax":
        value=module.numpy.asarray(x,dtype=module.numpy.float64)
        result,first=module.jit(module.value_and_grad(node))(value)
        actual=(result,first,module.jit(module.grad(module.grad(node)))(value))
    else:
        value=module.Variable(x,dtype=module.float64)
        with module.GradientTape() as outer:
            with module.GradientTape() as inner:result=node(value)
            first=inner.gradient(result,value)
        actual=(result.numpy(),first.numpy(),outer.gradient(first,value).numpy())
    expected=(np.cos(x)*np.cos(k*x),-np.sin(x)*np.cos(k*x)-k*np.cos(x)*np.sin(k*x),
        -(1+k*k)*np.cos(x)*np.cos(k*x)+2*k*np.sin(x)*np.sin(k*x))
    np.testing.assert_allclose(actual,expected,atol=2e-9,rtol=0)
