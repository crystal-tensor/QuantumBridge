# Copyright 2026 QuantumBridge Contributors.
# Licensed under the Apache License, Version 2.0.
"""Public factory types carry real stores, phase, identities and executable math."""
import numpy as np
import pytest
import quantumbridge as qb
from quantumbridge.information import Operator
from quantumbridge.compiler import native_transpile


def make(kind):
    if kind=="zero":return qb.QuantumCircuit(name="source",global_phase=.2,metadata={"note":[7]})
    r=qb.QuantumRegister(2 if kind=="alias" else 1,"data")
    circuit=qb.QuantumCircuit(r,name="source",global_phase=.2,metadata={"note":[7]})
    if kind=="alias":circuit.add_register(qb.QuantumRegister(name="alias",bits=[r[-1]]))
    circuit.ry(.3,r[-1])
    return circuit


@pytest.mark.parametrize("kind",["unitary","alias","zero"])
@pytest.mark.parametrize("action",["copy","empty","inverse","repeat0","repeat2","power0","power2","decompose"])
def test_public_factories_have_their_actual_class_bit_graph_and_full_complex_math(kind,action):
    circuit=make(kind);before=Operator(circuit).data
    if action=="copy":out=circuit.copy()
    elif action=="empty":out=circuit.copy_empty_like()
    elif action=="inverse":out=circuit.inverse()
    elif action=="repeat0":out=circuit.repeat(0)
    elif action=="repeat2":out=circuit.repeat(2)
    elif action=="power0":out=circuit.power(0)
    elif action=="power2":out=circuit.power(2)
    else:out=circuit.decompose()
    assert type(out) is qb.QuantumCircuit
    assert out.qubits==circuit.qubits and out.qregs==circuit.qregs
    assert len(out.data)==len(out.operations)+len(out.measurements)
    if action in {"repeat0","power0"}:expected=np.eye(len(before));assert out.global_phase==0
    elif action=="empty":expected=np.exp(.2j)*np.eye(len(before));assert out.global_phase==.2
    elif action=="inverse":expected=before.conj().T
    elif action in {"repeat2","power2"}:expected=before@before;assert len(out.data)==2 and out.global_phase==0
    else:expected=before
    np.testing.assert_allclose(Operator(out).data,expected,atol=7e-13,rtol=0)
    np.testing.assert_allclose(Operator(circuit).data,before,atol=3e-13,rtol=0)


def test_tensor_preserves_real_named_and_alias_membership_and_executes_public_data():
    circuit=make("alias");other=qb.QuantumCircuit(1,name="other");other.x(0)
    out=circuit.tensor(other)
    assert type(out) is qb.QuantumCircuit and out.qubits==other.qubits+circuit.qubits
    assert [reg.name for reg in out.qregs]==["q","data","alias"]
    assert [(reg.name,i) for reg,i in out.find_bit(out.qubits[2]).registers]==[("data",1),("alias",0)]
    assert len(out.data)==2
    np.testing.assert_allclose(Operator(out).data,np.kron(Operator(other).data,Operator(circuit).data),atol=6e-13,rtol=0)


def test_empty_copy_preserves_a_symbolic_scalar_phase_as_an_executable_parameter():
    p=qb.Parameter("phase");circuit=qb.QuantumCircuit(1,name="symbolic",global_phase=p)
    out=circuit.copy_empty_like();assert out.parameters==(p,)
    np.testing.assert_allclose(Operator(out.assign_parameters({p:.2})).data,np.exp(.2j)*np.eye(2),atol=4e-13,rtol=0)


@pytest.mark.parametrize("factory",["repeat","power"])
def test_public_repeated_nonunitary_factory_owns_two_actual_instruction_references(factory):
    circuit=qb.QuantumCircuit(1,1,name="readout",global_phase=.2)
    circuit.reset(0);circuit.x(0);circuit.measure(0,0)
    out=getattr(circuit,factory)(2)
    assert type(out) is qb.QuantumCircuit and len(out.data)==2
    assert all(type(context.operation) is qb.Instruction for context in out.data)
    assert out.global_phase==0 and out.qubits==circuit.qubits and out.clbits==circuit.clbits
    for device in (qb.StatevectorDevice,qb.DensityMatrixDevice,qb.MatrixProductStateDevice,qb.StabilizerDevice):
        assert device().run_shots(out,shots=3).counts()=={"1":3}


@pytest.mark.parametrize("factory",["copy","decompose","power","tensor"])
@pytest.mark.parametrize("device",[qb.StatevectorDevice,qb.DensityMatrixDevice,qb.MatrixProductStateDevice])
def test_public_factory_compiler_device_loop_has_an_independent_complex_oracle(factory,device):
    p=qb.Parameter("angle");register=qb.QuantumRegister(1,"data")
    source=qb.QuantumCircuit(register,qb.QuantumRegister(name="alias",bits=[register[0]]),global_phase=.2)
    source.ry(p,0)
    if factory=="power":out=source.power(2)
    elif factory=="tensor":
        other=qb.QuantumCircuit(1);other.x(0);out=source.tensor(other)
    else:out=getattr(source,factory)()
    assert type(out) is qb.QuantumCircuit and out.parameters==(p,)
    x=.3;multiple=2 if factory=="power" else 1;angle=multiple*x
    matrix=np.exp(.2j*multiple)*np.array([[np.cos(angle/2),-np.sin(angle/2)],
        [np.sin(angle/2),np.cos(angle/2)]])
    if factory=="tensor":matrix=np.kron(np.array([[0,1],[1,0]]),matrix)
    compiled=native_transpile(out.assign_parameters({p:x}),basis_gates=["rz","sx","x","cx"],optimization_level=1)
    np.testing.assert_allclose(Operator(compiled).data,matrix,atol=1e-12,rtol=0)
    state=matrix[:,0]
    if device is qb.DensityMatrixDevice:
        actual=device().density_matrix(compiled);expected=np.outer(state,state.conj())
    else:actual=device().statevector(compiled);expected=state
    np.testing.assert_allclose(actual,expected,atol=1e-12,rtol=0)
    assert source.data[0].params==[p] and source.num_qubits==1
