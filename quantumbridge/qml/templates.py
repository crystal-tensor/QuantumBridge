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


def basic_entangler_layers(circuit, parameters):
    for layer in parameters:
        basic_entangler(circuit, layer)
    return circuit


def strongly_entangling_layers(circuit, parameters):
    for layer in parameters:
        for wire, triple in enumerate(layer):
            phi, theta, omega = triple
            circuit.rz(float(phi), wire)
            circuit.ry(float(theta), wire)
            circuit.rz(float(omega), wire)
        for wire in range(circuit.num_qubits):
            circuit.cx(wire, (wire + 1) % circuit.num_qubits)
    return circuit


def hardware_efficient_ansatz(circuit, parameters):
    for layer in parameters:
        for wire, theta in enumerate(layer):
            circuit.ry(float(theta), wire)
        for wire in range(circuit.num_qubits - 1):
            circuit.cx(wire, wire + 1)
    return circuit
