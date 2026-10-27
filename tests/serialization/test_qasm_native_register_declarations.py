# Copyright 2026 QuantumBridge Contributors.
# Licensed under the Apache License, Version 2.0.
"""Representable register arrays use actual declarations and native bit tables."""
import numpy as np
import pytest
import quantumbridge as qb
from quantumbridge.information import Operator
from quantumbridge import serialization as codec


@pytest.mark.parametrize("format",["qasm2","qasm3"])
def test_named_native_register_arrays_roundtrip_real_find_bit_membership(format):
    left=qb.QuantumRegister(1,"left");right=qb.QuantumRegister(2,"right");bits=qb.ClassicalRegister(2,"readout")
    circuit=qb.Circuit(left,bits);circuit.add_register(right);circuit.h(left[0]).cx(left[0],right[1])
    text=getattr(codec,format+"_dumps")(circuit);out=getattr(codec,format+"_loads")(text)
    assert [reg.name for reg in out.qregs]==["left","right"] and [reg.name for reg in out.cregs]==["readout"]
    assert [(reg.name,i) for reg,i in out.find_bit(out.qubits[2]).registers]==[("right",1)]
    np.testing.assert_allclose(Operator(out).data,Operator(circuit).data,atol=4e-13,rtol=0)


@pytest.mark.parametrize("format",["qasm2","qasm3"])
def test_actual_source_measurement_maps_to_the_named_native_classical_register(format):
    q=qb.QuantumRegister(2,"data");c=qb.ClassicalRegister(2,"readout")
    circuit=qb.Circuit(q,c).x(q[1]).measure(q[1],c[0])
    text=getattr(codec,format+"_dumps")(circuit);out=getattr(codec,format+"_loads")(text)
    assert out.clbits[0]==c[0] and qb.StatevectorDevice().run_shots(out,shots=2).counts()=={"10":2}


@pytest.mark.parametrize("format",["qasm2","qasm3"])
def test_public_standard_gate_keeps_invocation_frame_and_named_source_register(format):
    from quantumbridge.core.standard_gates import RYGate
    register=qb.QuantumRegister(1,"data");circuit=qb.QuantumCircuit(register,name="frame")
    gate=RYGate(.3);circuit.append(gate,[register[0]],copy=False);gate.params[0]=.7
    out=getattr(codec,format+"_loads")(getattr(codec,format+"_dumps")(circuit,allow_metadata_loss=True))
    np.testing.assert_allclose(Operator(out).data,[[np.cos(.15),-np.sin(.15)],[np.sin(.15),np.cos(.15)]],atol=4e-13,rtol=0)
    assert out.qregs[0].name=="data"


@pytest.mark.parametrize("format",["qasm2","qasm3"])
@pytest.mark.parametrize("case",["alias","loose","reordered","ancilla"])
def test_nonrepresentable_source_graphs_are_not_silently_renamed(format,case):
    r=qb.QuantumRegister(2,"r")
    if case=="alias":circuit=qb.Circuit(r);circuit.add_register(qb.QuantumRegister(name="s",bits=[r[0]]))
    elif case=="loose":circuit=qb.Circuit();circuit.add_bits([qb.Qubit()])
    elif case=="reordered":circuit=qb.Circuit();circuit.add_bits([r[1],r[0]]);circuit.add_register(r)
    else:circuit=qb.Circuit(qb.AncillaRegister(1,"anc"))
    with pytest.raises(codec.UnsupportedFeature):getattr(codec,format+"_dumps")(circuit,allow_metadata_loss=True)
