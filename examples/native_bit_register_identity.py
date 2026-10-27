# Copyright 2026 QuantumBridge Contributors.
# Licensed under the Apache License, Version 2.0.
"""SDK-free bit/register identity, scalar phase and native differentiation."""
import json
import numpy as np
import quantumbridge as qb
from quantumbridge.compat.qiskit_adapter import circuit_from_ir
from quantumbridge.information import Operator
from quantumbridge.ir.qb_ir import IRProgram
from quantumbridge.qml import QNode


def main():
    a,b=qb.Qubit(),qb.Qubit()
    main_register=qb.QuantumRegister(name="logical",bits=[a,b])
    alias=qb.QuantumRegister(name="alias",bits=[b])
    classical=qb.ClassicalRegister(2,"readout")
    circuit=qb.Circuit(main_register,classical)
    circuit.add_register(alias)
    circuit.x(b).cx(b,a).measure(b,classical[0]).measure(a,classical[1])
    restored=circuit_from_ir(IRProgram.from_json(circuit.to_ir().to_json()))
    assert restored.qubits==[a,b]
    assert [(reg.name,i) for reg,i in restored.find_bit(b).registers]==[("logical",1),("alias",0)]
    counts=qb.StatevectorDevice().run_shots(restored,shots=4).counts()
    assert counts=={"11":4}

    p=qb.Parameter("angle")
    parameterized=qb.Circuit(main_register).ry(2*p+p.sin(),a).cx(a,b)
    parameterized=circuit_from_ir(IRProgram.from_json(parameterized.to_ir().to_json()))
    node=QNode.from_circuit(parameterized,qb.PauliZ(0),diff_method="parameter-shift",max_diff=2)
    x=.3;angle=2*x+np.sin(x);first=2+np.cos(x);second=-np.sin(x)
    gradient=-np.sin(angle)*first
    hessian=-np.cos(angle)*first**2-np.sin(angle)*second
    np.testing.assert_allclose(node(x),np.cos(angle),atol=3e-12,rtol=0)
    np.testing.assert_allclose(node.compute_jacobian(x),gradient,atol=3e-11,rtol=0)
    np.testing.assert_allclose(node.compute_hvp(.7,x),.7*hessian,atol=4e-10,rtol=0)

    scalar=qb.Circuit(0);scalar.global_phase=.3
    np.testing.assert_allclose(Operator(scalar).data,[[np.exp(.3j)]],atol=2e-13,rtol=0)
    np.testing.assert_allclose(Operator(scalar.repeat(2).to_gate()).data,[[np.exp(.6j)]],atol=3e-13,rtol=0)
    np.testing.assert_allclose(Operator(scalar.control()).data,np.diag([1,np.exp(.3j)]),atol=3e-13,rtol=0)
    print(json.dumps({"counts":counts,"logical_bits":len(restored.qubits),"alias_memberships":2,
        "gradient":float(np.asarray(node.compute_jacobian(x))),"hvp":float(node.compute_hvp(.7,x)),
        "zero_width_coherent_phase":"passed","full_sdk_parity":False},sort_keys=True))


if __name__=="__main__":main()
