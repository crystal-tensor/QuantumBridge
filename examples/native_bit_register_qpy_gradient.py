# Copyright 2026 QuantumBridge Contributors.
# Licensed under the Apache License, Version 2.0.
"""SDK-free standard register records, owned Gate, nonlinear AD and MPS."""
import json
import numpy as np
import quantumbridge as qb
from quantumbridge.information import Operator
from quantumbridge.qml import QNode
from quantumbridge.serialization import qpy_dumps,qpy_loads


def source(width):
    parameters=qb.ParameterVector("angle",1);p=parameters[0]
    body=qb.QuantumCircuit(1,name="nonlinear");body.ry(2*p+p.sin(),0)
    register=qb.QuantumRegister(width,"logical")
    circuit=qb.QuantumCircuit(register,qb.QuantumRegister(name="alias",bits=[register[-1]]))
    circuit.append(body.to_gate(),[register[-1]])
    return qpy_loads(qpy_dumps(circuit))[0]


def main():
    circuit=source(1);p=circuit.parameters[0];x=.3;angle=2*x+np.sin(x)
    bound=circuit.assign_parameters({p:x})
    matrix=np.array([[np.cos(angle/2),-np.sin(angle/2)],[np.sin(angle/2),np.cos(angle/2)]])
    np.testing.assert_allclose(Operator(bound).data,matrix,atol=4e-13,rtol=0)
    memberships=[(reg.name,i) for reg,i in bound.find_bit(bound.qubits[0]).registers]
    assert memberships==[("logical",0),("alias",0)]
    node=QNode.from_circuit(source(100),qb.PauliZ(99),device=qb.MatrixProductStateDevice(
        max_memory_mb=2,max_bond_dim=4,cutoff=0),diff_method="parameter-shift",max_diff=2)
    first=2+np.cos(x);second=-np.sin(x)
    gradient=-np.sin(angle)*first;hessian=-np.cos(angle)*first**2-np.sin(angle)*second
    np.testing.assert_allclose(node(x),np.cos(angle),atol=3e-12,rtol=0)
    np.testing.assert_allclose(node.compute_jacobian(x),gradient,atol=3e-10,rtol=0)
    np.testing.assert_allclose(node.compute_hessian(x),hessian,atol=5e-10,rtol=0)
    np.testing.assert_allclose(node.compute_hvp(.7,x),.7*hessian,atol=5e-10,rtol=0)
    print(json.dumps({"qpy_version":13,"alias_memberships":memberships,"mps_qubits":100,
        "gradient":float(np.asarray(node.compute_jacobian(x))),"hvp":float(node.compute_hvp(.7,x)),
        "full_sdk_parity":False},sort_keys=True))


if __name__=="__main__":main()
