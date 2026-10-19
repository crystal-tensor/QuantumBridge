# Copyright 2026 QuantumBridge Contributors.
# Licensed under the Apache License, Version 2.0.
# Native deterministic training; no upstream SDK or hardware call.

import numpy as np
from quantumbridge import Hamiltonian, PauliZ
from quantumbridge.qml import NativeQNode


def program(tape, angles):
    tape.ry(angles[0], 0)
    tape.ry(angles[1], 1)
    tape.cx(0, 1)
    return tape.expval(Hamiltonian([(1, PauliZ(0)), (1, PauliZ(1))]))


def main():
    node = NativeQNode(program, 2, diff_method="adjoint")
    angles = np.array([.8, .5])
    initial, trace = node(angles), []
    for _ in range(50):
        gradient = node.gradient(angles)
        trace.append(gradient.tolist())
        angles -= .1 * gradient
    final = node(angles)
    print({"provenance": "QuantumBridge native forward + adjoint + gradient descent",
           "initial_loss": initial, "final_loss": final, "angles": angles.tolist(),
           "first_gradient": trace[0], "last_gradient": trace[-1], "steps": len(trace)})
    assert final < initial - 2


if __name__ == "__main__": main()
