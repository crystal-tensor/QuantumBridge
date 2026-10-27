# Copyright 2026 QuantumBridge Contributors.
# Licensed under the Apache License, Version 2.0.
"""Generic native executable frames do not drift with a borrowed source owner."""
import gc
import weakref
import numpy as np
import pytest
import quantumbridge as qb
from quantumbridge.information import Operator
from quantumbridge.qml import QNode
from quantumbridge.serialization import qpy_dumps,qpy_loads
from quantumbridge.compat.qiskit_adapter import circuit_from_ir
from quantumbridge.ir.qb_ir import IRProgram


def owner(kind):
    p=qb.Parameter("p");body=qb.Circuit(1).ry(2*p+p.sin(),0)
    return (body.to_gate() if kind=="gate" else body.to_instruction()),p


def rotation(x):
    a=2*x+np.sin(x);return np.array([[np.cos(a/2),-np.sin(a/2)],[np.sin(a/2),np.cos(a/2)]])


@pytest.mark.parametrize("kind",["gate","instruction"])
@pytest.mark.parametrize("action",["direct","copy","bind","ir","qpy"])
def test_generic_source_mutation_retains_parameter_graph_and_actual_bound_execution(kind,action):
    gate,p=owner(kind);circuit=qb.QuantumCircuit(1);circuit.append(gate,[0],copy=False)
    gate.params[0]=.7;gate.name="changed"
    assert circuit.parameters==(p,) and circuit.data[0].params==[p]
    if action=="copy":circuit=circuit.copy()
    elif action=="ir":circuit=circuit_from_ir(IRProgram.from_json(circuit.to_ir().to_json()))
    elif action=="qpy":circuit=qpy_loads(qpy_dumps(circuit))[0]
    bound=circuit.assign_parameters({circuit.parameters[0]:.3})
    np.testing.assert_allclose(Operator(bound).data,rotation(.3),atol=5e-13,rtol=0)


@pytest.mark.parametrize("kind",["gate","instruction"])
def test_generic_frame_owner_lifetime_is_retained_without_borrowing_the_circuit_copy(kind):
    source,p=owner(kind);ref=weakref.ref(source);circuit=qb.QuantumCircuit(1)
    circuit.append(source,[0],copy=False);copied=circuit.copy();del source;gc.collect()
    assert ref() is circuit.data[0].operation
    circuit.data[0].operation.params[0]=.7
    assert copied.data[0].operation is not ref() and copied.parameters==(p,)
    np.testing.assert_allclose(Operator(copied.assign_parameters({p:.3})).data,rotation(.3),atol=5e-13,rtol=0)


@pytest.mark.parametrize("kind",["gate","instruction"])
def test_generic_stored_symbolic_frame_reaches_real_jacobian_hessian_and_hvp(kind):
    source,p=owner(kind);circuit=qb.QuantumCircuit(1);circuit.append(source,[0],copy=False)
    source.params[0]=.7
    node=QNode.from_circuit(circuit,qb.PauliZ(0),diff_method="parameter-shift",max_diff=2)
    x=.3;a=2*x+np.sin(x);first=2+np.cos(x);second=-np.sin(x)
    hessian=-np.cos(a)*first**2-np.sin(a)*second
    assert node(x)==pytest.approx(np.cos(a),abs=4e-12)
    assert node.compute_jacobian(x)==pytest.approx(-np.sin(a)*first,abs=3e-10)
    assert node.compute_hessian(x)==pytest.approx(hessian,abs=5e-10)
    assert node.compute_hvp(.7,x)==pytest.approx(.7*hessian,abs=5e-10)


@pytest.mark.parametrize("kind",["gate","instruction"])
@pytest.mark.parametrize("framework",["torch","autograd","jax","tensorflow"])
def test_generic_cached_source_frame_has_real_framework_gradient(kind,framework):
    source,p=owner(kind);circuit=qb.QuantumCircuit(1);circuit.append(source,[0],copy=False);source.params[0]=.7
    node=QNode.from_circuit(circuit,qb.PauliZ(0),interface=framework,diff_method="parameter-shift")
    module=pytest.importorskip(framework);x=.3
    if framework=="torch":
        value=module.tensor(x,dtype=module.float64,requires_grad=True);node(value).backward();actual=float(value.grad)
    elif framework=="autograd":actual=float(module.grad(node)(x))
    elif framework=="jax":actual=float(module.grad(node)(module.numpy.asarray(x,dtype=module.numpy.float64)))
    else:
        value=module.Variable(x,dtype=module.float64)
        with module.GradientTape() as tape:result=node(value)
        actual=float(tape.gradient(result,value))
    assert actual==pytest.approx(-np.sin(2*x+np.sin(x))*(2+np.cos(x)),abs=3e-10)


@pytest.mark.parametrize("kind",["gate","instruction"])
@pytest.mark.parametrize("framework",["torch","autograd","jax","tensorflow"])
def test_generic_cached_source_frame_has_actual_framework_second_derivatives(kind,framework):
    source,p=owner(kind);circuit=qb.QuantumCircuit(1);circuit.append(source,[0],copy=False)
    source.params[0]=.7
    node=QNode.from_circuit(circuit,qb.PauliZ(0),interface=framework,diff_method="parameter-shift",max_diff=2)
    module=pytest.importorskip(framework);x=.3
    if framework=="torch":
        value=module.tensor(x,dtype=module.float64,requires_grad=True)
        first=module.autograd.grad(node(value),value,create_graph=True)[0]
        actual=float(module.autograd.grad(first,value)[0])
    elif framework=="autograd":actual=float(module.grad(module.grad(node))(x))
    elif framework=="jax":actual=float(module.grad(module.grad(node))(module.numpy.asarray(x,dtype=module.numpy.float64)))
    else:
        value=module.Variable(x,dtype=module.float64)
        with module.GradientTape() as outer:
            with module.GradientTape() as inner:result=node(value)
            first=inner.gradient(result,value)
        actual=float(outer.gradient(first,value))
    expected=-np.cos(2*x+np.sin(x))*(2+np.cos(x))**2+np.sin(2*x+np.sin(x))*np.sin(x)
    assert actual==pytest.approx(expected,abs=5e-10)
