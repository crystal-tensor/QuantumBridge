# Copyright 2026 QuantumBridge Contributors.
# Licensed under the Apache License, Version 2.0.
# Native example without upstream SDKs or hardware calls.

from quantumbridge import DensityMatrixDevice
from quantumbridge.qml import QNode
from quantumbridge.utils.math import PauliZ


def main():
    def program(tape):
        tape.h(0)
        measured = tape.measure(0, reset=True)
        tape.cond(measured, lambda branch: branch.x(1))
        return tape.expval(PauliZ(0)), tape.probs([1])
    print("Reset and conditional correction:", QNode(program, 2, device=DensityMatrixDevice())())


if __name__ == "__main__": main()
