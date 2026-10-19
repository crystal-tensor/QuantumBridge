# Copyright 2026 QuantumBridge Contributors.
# Licensed under the Apache License, Version 2.0.

import numpy as np
from quantumbridge import PauliZ
from quantumbridge.qml import NativeQNode


def program(tape, theta):
    tape.ry(theta, 0)
    tape.ry(np.sin(theta), 0)
    tape.cx(0, 1)
    return tape.expval(PauliZ(1))


def main():
    node = NativeQNode(program, 2)
    adjoint = node.gradient(.4, method="adjoint")
    shifted = node.gradient(.4, method="parameter-shift")
    expected = -np.sin(.4 + np.sin(.4)) * (1 + np.cos(.4))
    print({"adjoint": adjoint, "parameter_shift": shifted, "analytic": expected})
    np.testing.assert_allclose([adjoint, shifted], expected, atol=1e-10)


if __name__ == "__main__": main()
