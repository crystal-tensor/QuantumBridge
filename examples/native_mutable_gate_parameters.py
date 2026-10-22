# Copyright 2026 QuantumBridge Contributors.
# Licensed under the Apache License, Version 2.0.
"""SDK-free mutable definitions, owned copies, native IR/QPY and derivatives."""

import numpy as np

from quantumbridge import Circuit, ParameterVector, PauliZ
from quantumbridge.compat.qiskit_adapter import circuit_from_ir
from quantumbridge.information import Operator
from quantumbridge.ir.qb_ir import IRProgram
from quantumbridge.qml import QNode
from quantumbridge.serialization import qpy_dumps, qpy_loads


def main():
    p, q = ParameterVector("definition", 2)
    r, s = ParameterVector("inputs", 2)
    body = Circuit(1).ry(p.sin()+q.exp()*p*p, 0)
    body.global_phase = p/3
    gate = body.to_gate()
    gate.params[:] = [r, s]
    source = Circuit(1).append(gate, [0])
    restored = circuit_from_ir(IRProgram.from_json(source.to_ir().to_json()))
    copied = restored.operations[0].metadata["gate"].copy()
    for values in ([.4, -.2], [.7, .3]):
        copied.params[:] = values
        x, y = values
        f = np.sin(x)+np.exp(y)*x*x
        matrix = np.exp(1j*x/3)*np.array([[np.cos(f/2), -np.sin(f/2)], [np.sin(f/2), np.cos(f/2)]])
        np.testing.assert_allclose(Operator(copied).data, matrix, atol=2e-13)
    assert restored.parameters == (r, s) and source.parameters == (r, s)

    # Standard QPY preserves this explicit symbolic definition. It does not
    # claim to serialize private lineage of every already-numeric custom Gate.
    qpy_restored = qpy_loads(qpy_dumps(restored))[0]
    assert qpy_restored.parameters == (r, s)
    node = QNode.from_circuit(qpy_restored, PauliZ(0), diff_method="adjoint", max_diff=2)
    point, direction = np.array([.4, -.2]), np.array([.3, -.2])
    x, y = point
    e = np.exp(y)
    f = np.sin(x)+e*x*x
    df = np.array([np.cos(x)+2*e*x, e*x*x])
    hf = np.array([[-np.sin(x)+2*e, 2*e*x], [2*e*x, e*x*x]])
    gradient = -np.sin(f)*df
    hessian = -np.cos(f)*np.outer(df, df)-np.sin(f)*hf
    np.testing.assert_allclose(node(point), np.cos(f), atol=2e-12)
    np.testing.assert_allclose(node.compute_jacobian(point), gradient, atol=2e-10)
    np.testing.assert_allclose(node.compute_hessian(point), hessian, atol=4e-10)
    np.testing.assert_allclose(node.compute_hvp(direction, point), hessian@direction, atol=4e-10)
    print("Mutable native Gate copies, IR/QPY and analytic Jacobian/Hessian/HVP passed.")


if __name__ == "__main__": main()
