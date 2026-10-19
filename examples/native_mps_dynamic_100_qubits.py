# Copyright 2026 QuantumBridge Contributors.
# Licensed under the Apache License, Version 2.0.
# Native MPS example; no dense state expansion or hardware submission.

from quantumbridge import Circuit, MatrixProductStateDevice
from quantumbridge.core.classical import bit


def main():
    circuit = Circuit(100, 2).h(0)
    for wire in range(99): circuit.cx(wire, wire + 1)
    circuit.measure(0, 0)
    circuit.if_else(bit(0), Circuit(100, 2).x(99), inplace=True)
    circuit.measure(99, 1)
    result = MatrixProductStateDevice(max_memory_mb=2).run_shots(circuit, shots=16, seed=9, memory=True)
    print("Recorded c0/c1:", result.counts())
    print("Peak MPS bond:", result.metadata()["max_bond_observed"])
    print("Maximum discarded Schmidt weight:", result.metadata()["max_discarded_weight"])
    print("Dynamic execution:", result.metadata()["dynamic_control_flow"])


if __name__ == "__main__": main()
