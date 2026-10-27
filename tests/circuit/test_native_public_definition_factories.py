# Copyright 2026 QuantumBridge Contributors.
# Licensed under the Apache License, Version 2.0.
"""Conversion definitions have actual local operands and coherent phase math."""
import numpy as np
import pytest
import quantumbridge as qb
from quantumbridge.information import Operator
from quantumbridge.qml import QNode
from quantumbridge.core.gate_limits import GateCircuitLimits,gate_circuit_scope
from quantumbridge.serialization import qpy_dumps,qpy_loads
from quantumbridge.ir.qb_ir import IRProgram
from quantumbridge.compat.qiskit_adapter import circuit_from_ir


def phase_source():
    vector=qb.ParameterVector("angle",1);p=vector[0]
    r=qb.QuantumRegister(3,"data");source=qb.QuantumCircuit(r,qb.QuantumRegister(name="alias",bits=[r[0]]),
        name="source",global_phase=p/7)
    body=qb.QuantumCircuit(2,name="inner",global_phase=p/5);body.ry(2*p,1);body.cx(1,0)
    source.append(body.to_gate(),[r[2],r[0]])
    return source,p


def coherent_oracle(x):
    controlled=np.zeros((16,16),complex);phase=np.exp(1j*x*(1/5+1/7))
    rotation=np.array([[np.cos(x),-np.sin(x)],[np.sin(x),np.cos(x)]])
    for column in range(16):
        bits=[(column>>(3-i))&1 for i in range(4)]
        if bits[3]:controlled[column,column]=1;continue
        for value in (0,1):
            row_bits=list(bits);row_bits[1]=value;row_bits[2]^=value
            row=sum(bit<<(3-i) for i,bit in enumerate(row_bits))
            controlled[row,column]=phase*rotation[value,bits[1]]
    return controlled@np.kron(np.eye(8),np.array([[1,1],[1,-1]])/np.sqrt(2))


@pytest.mark.parametrize("transport",["direct","ir","qpy"])
def test_public_to_gate_control_bind_format_loop_has_independent_full_complex_math_and_hvp(transport):
    source,p=phase_source();owner=source.to_gate(label="converted")
    assert type(owner.definition) is qb.QuantumCircuit
    assert [(r.name,len(r)) for r in owner.definition.qregs]==[("q",3)]
    assert owner.definition.qubits[0]!=source.qubits[0]
    parent=qb.QuantumCircuit(4);parent.h(3);parent.append(owner.control(ctrl_state=0),[3,1,0,2])
    if transport=="ir":parent=circuit_from_ir(IRProgram.from_json(parent.to_ir().to_json()))
    elif transport=="qpy":parent=qpy_loads(qpy_dumps(parent))[0]
    x=.3;parameter=parent.parameters[0]
    np.testing.assert_allclose(Operator(parent.assign_parameters({parameter:x})).data,coherent_oracle(x),atol=2e-12,rtol=0)
    node=QNode.from_circuit(parent,qb.PauliX(3),diff_method="parameter-shift",max_diff=2)
    k=1/5+1/7
    first=-np.sin(x)*np.cos(k*x)-k*np.cos(x)*np.sin(k*x)
    second=-(1+k*k)*np.cos(x)*np.cos(k*x)+2*k*np.sin(x)*np.sin(k*x)
    assert node(x)==pytest.approx(np.cos(x)*np.cos(k*x),abs=4e-12)
    assert node.compute_jacobian(x)==pytest.approx(first,abs=4e-10)
    assert node.compute_hvp(.7,x)==pytest.approx(.7*second,abs=7e-10)
    assert [r.name for r in source.qregs]==["data","alias"] and source.parameters==(p,)


@pytest.mark.parametrize("transport",["direct","ir"])
def test_public_nonunitary_instruction_conversion_maps_real_local_classical_operands(transport):
    r=qb.QuantumRegister(1,"data");bits=qb.ClassicalRegister(2,"readout")
    source=qb.QuantumCircuit(r,bits,name="readout");source.reset(0);source.x(0);source.measure(0,1)
    owner=source.to_instruction(label="nonunitary")
    assert [(r.name,len(r)) for r in owner.definition.qregs+owner.definition.cregs]==[("q",1),("c",2)]
    parent=qb.QuantumCircuit(3,2);parent.append(owner,[2],[1,0])
    if transport=="ir":parent=circuit_from_ir(IRProgram.from_json(parent.to_ir().to_json()))
    for device in (qb.StatevectorDevice,qb.DensityMatrixDevice,qb.MatrixProductStateDevice,qb.StabilizerDevice):
        assert device().run_shots(parent,shots=3).counts()=={"10":3}
    with pytest.raises(ValueError):source.to_gate()


@pytest.mark.parametrize("kind",["gate","instruction"])
def test_public_parameter_map_conversion_keeps_normalized_formal_template_editable_after_ir(kind):
    p=qb.ParameterVector("p",1)[0];r=qb.QuantumRegister(1,"data")
    source=qb.QuantumCircuit(r,qb.QuantumRegister(name="alias",bits=[r[0]]),name="source",global_phase=p/5)
    source.ry(p,0)
    owner=getattr(source,"to_"+kind)(parameter_map={p:.2})
    assert [(r.name,len(r)) for r in owner.definition.qregs]==[("q",1)]
    parent=qb.QuantumCircuit(1);parent.append(owner,[0])
    restored=circuit_from_ir(IRProgram.from_json(parent.to_ir().to_json()))
    stored=restored.operations[0].metadata["gate" if kind=="gate" else "instruction_object"]
    q=qb.Parameter("replacement");stored.params=[q]
    np.testing.assert_allclose(Operator(restored.assign_parameters({q:.4})).data,
        np.exp(.08j)*np.array([[np.cos(.2),-np.sin(.2)],[np.sin(.2),np.cos(.2)]]),atol=6e-13,rtol=0)


@pytest.mark.parametrize("kind",["gate","instruction"])
def test_conversion_work_and_parameter_map_validation_precede_initial_copy(kind,monkeypatch):
    source,p=phase_source()
    monkeypatch.setattr(qb.Circuit,"copy",lambda *a,**kw:pytest.fail("conversion copied before admission"))
    with gate_circuit_scope(GateCircuitLimits(max_decomposition_work=1)),pytest.raises(MemoryError):
        getattr(source,"to_"+kind)()
