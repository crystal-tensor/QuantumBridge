# Copyright 2026 QuantumBridge Contributors.
# Licensed under the Apache License, Version 2.0.
# This file is part of QuantumBridge SDK.
# This implementation is developed for the QuantumBridge native architecture.


def basic_entangler(circuit, parameters):
    for wire, theta in enumerate(parameters):
        circuit.ry(float(theta), wire)
    for wire in range(circuit.num_qubits - 1):
        circuit.cx(wire, wire + 1)
    return circuit

