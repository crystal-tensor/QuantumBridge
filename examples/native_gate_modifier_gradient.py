# Copyright 2026 QuantumBridge Contributors.
# Licensed under the Apache License, Version 2.0.
"""SDK-free annotation -> native QNode -> analytic first/second/HVP checks."""

import numpy as np

from quantumbridge import AnnotatedOperation, Circuit, ControlModifier, PowerModifier, Parameter, PauliX
from quantumbridge.qml import QNode


def main():
    p, q = Parameter("p"), Parameter("q")
    angle = p.sin()+q*p*p
    body = Circuit(1).rz(angle, 0)
    body.global_phase = angle/3
    op = AnnotatedOperation(body.to_gate(), [ControlModifier(1, 0), PowerModifier(2)])
    node = QNode.from_circuit(Circuit(2).h(0).append(op, [0, 1]), PauliX(0), max_diff=2)
    point, direction = np.array([.4, -.2]), np.array([.3, -.2])
    p, q = point
    f = np.sin(p)+q*p*p
    df, hf = np.array([np.cos(p)+2*q*p, p*p]), np.array([[-np.sin(p)+2*q, 2*p], [2*p, 0]])
    gradient = -np.sin(f/3)*df/3
    hessian = -np.cos(f/3)*np.outer(df, df)/9-np.sin(f/3)*hf/3
    np.testing.assert_allclose(node(point), np.cos(f/3), atol=2e-12)
    np.testing.assert_allclose(node.compute_jacobian(point), gradient, atol=2e-10)
    np.testing.assert_allclose(node.compute_hessian(point), hessian, atol=3e-10)
    np.testing.assert_allclose(node.compute_hvp(direction, point), hessian@direction, atol=3e-10)
    print("Native modifier value/Jacobian/Hessian/HVP passed independent calculus.")


if __name__ == "__main__": main()
