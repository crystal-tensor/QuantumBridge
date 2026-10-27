# Copyright 2026 QuantumBridge Contributors.
# Licensed under the Apache License, Version 2.0.
"""Execute public instructions, rather than only describe their return types."""
import numpy as np
import pytest
import quantumbridge as qb
from quantumbridge.compiler import native_transpile
from quantumbridge.information import Operator
from quantumbridge.qml import QNode
from quantumbridge.serialization import qpy_dumps,qpy_loads
from quantumbridge.ir.qb_ir import IRProgram
from quantumbridge.compat.qiskit_adapter import circuit_from_ir


def symbolic_source(width=1):
    p=qb.ParameterVector("v",1)[0];body=qb.QuantumCircuit(1,name="nonlinear");body.ry(2*p+p.sin(),0)
    r=qb.QuantumRegister(width,"r");alias=qb.QuantumRegister(name="alias",bits=[r[-1]])
    circuit=qb.QuantumCircuit(r,alias);circuit.append(body.to_gate(),[r[-1]])
    return circuit


@pytest.mark.parametrize("kind",[qb.StatevectorDevice,qb.DensityMatrixDevice,qb.MatrixProductStateDevice,qb.StabilizerDevice])
def test_public_measurement_enters_all_four_dynamic_devices(kind):
    q=qb.QuantumRegister(2,"q");c=qb.ClassicalRegister(2,"c");circuit=qb.QuantumCircuit(q,c)
    circuit.x(q[1]);circuit.measure(q[1],c[0]);circuit.reset(q[1]);circuit.measure(q[1],c[1])
    assert kind().run_shots(circuit,shots=3,seed=7).counts()=={"10":3}


def test_public_builder_and_handle_feed_the_existing_native_compiler():
    circuit=qb.QuantumCircuit(2);circuit.h(0);handle=circuit.x([0,1]);handle.inverse()
    out=native_transpile(circuit,basis_gates=["rz","sx","x","cx"],optimization_level=1)
    expected=np.kron(np.array([[0,1],[1,0]])@np.array([[1,1],[1,-1]])/np.sqrt(2),np.array([[0,1],[1,0]]))
    np.testing.assert_allclose(Operator(out).data,expected,atol=6e-13,rtol=0)


@pytest.mark.parametrize("format",["qpy","ir"])
def test_public_alias_custom_gate_has_real_hundred_wire_higher_derivatives_without_dense_conversion(format,monkeypatch):
    from quantumbridge.information.matrix_product_state import MatrixProductState
    source=symbolic_source(100)
    restored=qpy_loads(qpy_dumps(source))[0] if format=="qpy" else circuit_from_ir(IRProgram.from_json(source.to_ir().to_json()))
    assert len(restored.find_bit(restored.qubits[99]).registers)==2
    def forbidden(*args,**kwargs):pytest.fail("public hundred-wire execution used a dense fallback")
    for kind,method in [(qb.Gate,"to_matrix"),(qb.StatevectorDevice,"statevector"),
            (qb.DensityMatrixDevice,"density_matrix"),(MatrixProductState,"statevector")]:
        monkeypatch.setattr(kind,method,forbidden)
    node=QNode.from_circuit(restored,qb.PauliZ(99),device=qb.MatrixProductStateDevice(
        max_memory_mb=2,max_bond_dim=4,cutoff=0),diff_method="parameter-shift",max_diff=2)
    x=.3;angle=2*x+np.sin(x);first=2+np.cos(x);second=-np.sin(x)
    expected=-np.cos(angle)*first**2-np.sin(angle)*second
    assert node(x)==pytest.approx(np.cos(angle),abs=3e-12)
    assert node.compute_jacobian(x)==pytest.approx(-np.sin(angle)*first,abs=3e-10)
    assert node.compute_hessian(x)==pytest.approx(expected,abs=5e-10)
    assert node.compute_hvp(.7,x)==pytest.approx(.7*expected,abs=5e-10)


@pytest.mark.parametrize("framework",["torch","autograd","jax","tensorflow"])
@pytest.mark.parametrize("format",["qpy","ir"])
def test_public_custom_gate_roundtrip_reaches_actual_framework_gradient(framework,format):
    source=symbolic_source()
    circuit=qpy_loads(qpy_dumps(source))[0] if format=="qpy" else circuit_from_ir(IRProgram.from_json(source.to_ir().to_json()))
    node=QNode.from_circuit(circuit,qb.PauliZ(0),interface=framework,diff_method="parameter-shift")
    module=pytest.importorskip(framework);x=.3;expected=-np.sin(2*x+np.sin(x))*(2+np.cos(x))
    if framework=="torch":
        value=module.tensor(x,dtype=module.float64,requires_grad=True);node(value).backward();actual=float(value.grad)
    elif framework=="autograd":actual=float(module.grad(node)(x))
    elif framework=="jax":actual=float(module.grad(node)(module.numpy.asarray(x,dtype=module.numpy.float64)))
    else:
        value=module.Variable(x,dtype=module.float64)
        with module.GradientTape() as tape:result=node(value)
        actual=float(tape.gradient(result,value))
    assert actual==pytest.approx(expected,abs=3e-10)
