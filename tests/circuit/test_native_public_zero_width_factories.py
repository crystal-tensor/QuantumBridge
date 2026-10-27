# Copyright 2026 QuantumBridge Contributors.
# Licensed under the Apache License, Version 2.0.
"""Zero-width public matrix factories retain coherent complex scalars."""
import io
import numpy as np
import pytest
import quantumbridge as qb
from quantumbridge.circuit_library import UnitaryGate
from quantumbridge.information import Operator
from quantumbridge.serialization import qpy_dumps,qpy_loads
from quantumbridge.ir.qb_ir import IRProgram
from quantumbridge.compat.qiskit_adapter import circuit_from_ir
from quantumbridge.core.gate_limits import GateCircuitLimits,gate_circuit_scope


@pytest.mark.parametrize("exponent",[-1,.5])
@pytest.mark.parametrize("transport",["direct","ir","qpy"])
def test_public_zero_width_power_has_a_real_unitary_owner_and_full_scalar_phase(exponent,transport):
    source=qb.QuantumCircuit(global_phase=.2);out=source.power(exponent)
    assert type(out) is qb.QuantumCircuit and type(out.data[0].operation) is UnitaryGate
    if transport=="ir":out=circuit_from_ir(IRProgram.from_json(out.to_ir().to_json()))
    elif transport=="qpy":out=qpy_loads(qpy_dumps(out))[0]
    np.testing.assert_allclose(Operator(out).data,[[np.exp(.2j*exponent)]],atol=5e-13,rtol=0)
    np.testing.assert_allclose(qb.StatevectorDevice().statevector(out),[np.exp(.2j*exponent)],atol=5e-13,rtol=0)


def test_zero_qubit_unitary_matrix_is_coherently_controlled_without_a_fictitious_target():
    owner=UnitaryGate([[np.exp(.3j)]])
    assert owner.num_qubits==0
    np.testing.assert_allclose(Operator(owner.control()).data,np.diag([1,np.exp(.3j)]),atol=5e-13,rtol=0)


@pytest.mark.parametrize("direction",["native_to_public","public_to_native"])
def test_actual_public_scalar_unitary_qpy_records_have_zero_operands(direction):
    pytest.importorskip("qiskit")
    from qiskit import QuantumCircuit,qpy
    from qiskit.circuit.library import UnitaryGate as PublicUnitary
    from qiskit.quantum_info import Operator as PublicOperator
    if direction=="native_to_public":
        c=qb.QuantumCircuit();c.append(UnitaryGate([[np.exp(.3j)]]),[])
        out=qpy.load(io.BytesIO(qpy_dumps(c)))[0];actual=PublicOperator(out).data
    else:
        c=QuantumCircuit();c.append(PublicUnitary([[np.exp(.3j)]]),[])
        f=io.BytesIO();qpy.dump(c,f,version=13);out=qpy_loads(f.getvalue())[0];actual=Operator(out).data
    assert out.num_qubits==0
    np.testing.assert_allclose(actual,[[np.exp(.3j)]],atol=5e-13,rtol=0)


def test_scalar_unitary_admission_does_not_allow_a_forged_targetless_matrix():
    from quantumbridge.core.operations import Operation
    body=qb.Circuit()
    body.operations=[Operation("unitary",(),metadata={"matrix":np.eye(2)})]
    with pytest.raises(ValueError):qb.Gate("forged",0,[],definition=body)


def test_scalar_unitary_retains_matrix_limits_and_unitarity_validation():
    with gate_circuit_scope(GateCircuitLimits(max_matrix_dimension=1)):
        np.testing.assert_allclose(UnitaryGate([[1j]]).to_matrix(),[[1j]],atol=0,rtol=0)
        with pytest.raises(MemoryError):UnitaryGate(np.eye(2))
    for invalid in ([[0]],[[2]],[[np.nan]],[],np.ones((1,2))):
        with pytest.raises(ValueError):UnitaryGate(invalid)


@pytest.mark.parametrize("as_generator",[False,True])
@pytest.mark.parametrize("kind",["gate","instruction"])
def test_from_instructions_preserves_a_cached_symbol_not_a_later_source_binding(kind,as_generator):
    p=qb.Parameter("theta");body=qb.QuantumCircuit(1);body.ry(p,0)
    owner=body.to_gate() if kind=="gate" else body.to_instruction()
    source=qb.QuantumCircuit(1);source.append(owner,[0],copy=False);context=source.data[0]
    owner.params[0]=.7
    values=(item for item in [context]) if as_generator else [context]
    out=qb.QuantumCircuit.from_instructions(values,name="from")
    assert type(out) is qb.QuantumCircuit and out.qubits==source.qubits and not out.qregs
    assert out.data[0].operation is owner and out.data[0].params==[p] and out.parameters==(p,)
    angle=.4;expected=[[np.cos(angle/2),-np.sin(angle/2)],[np.sin(angle/2),np.cos(angle/2)]]
    np.testing.assert_allclose(Operator(out.assign_parameters({p:angle})).data,expected,atol=4e-13,rtol=0)
    assert out.data[0].operation.params==[.7] and source.parameters==(p,)


@pytest.mark.parametrize("as_generator",[False,True])
@pytest.mark.parametrize("kind",["gate","instruction"])
def test_zero_width_from_instructions_really_executes_its_scalar_definition(kind,as_generator):
    body=qb.QuantumCircuit(global_phase=.3)
    owner=body.to_gate() if kind=="gate" else body.to_instruction()
    context=qb.CircuitInstruction(owner,[],[])
    values=(item for item in [context]) if as_generator else [context]
    out=qb.QuantumCircuit.from_instructions(values)
    assert out.num_qubits==0 and len(out.data)==1
    np.testing.assert_allclose(Operator(out).data,[[np.exp(.3j)]],atol=3e-13,rtol=0)
    np.testing.assert_allclose(qb.StatevectorDevice().statevector(out),[np.exp(.3j)],atol=3e-13,rtol=0)


def test_empty_generator_keeps_explicit_bits_but_infers_no_register_owner():
    reg=qb.QuantumRegister(2,"original");cbit=qb.Clbit()
    out=qb.QuantumCircuit.from_instructions(iter(()),qubits=reg,clbits=[cbit],global_phase=.3)
    assert out.qubits==list(reg) and out.clbits==[cbit] and not out.qregs and not out.cregs
    assert not out.data and out.find_bit(reg[1]).registers==[]
    np.testing.assert_allclose(Operator(out).data,np.exp(.3j)*np.eye(4),atol=3e-13,rtol=0)


def test_zero_width_generator_cannot_bypass_the_aggregate_operation_budget():
    owner=qb.QuantumCircuit(global_phase=.3).to_gate();context=qb.CircuitInstruction(owner)
    consumed=[]
    def values():
        for index in range(100):
            consumed.append(index);yield context
    with gate_circuit_scope(GateCircuitLimits(max_total_operations=1)),pytest.raises(MemoryError):
        qb.QuantumCircuit.from_instructions(values())
    assert consumed==[0,1]
