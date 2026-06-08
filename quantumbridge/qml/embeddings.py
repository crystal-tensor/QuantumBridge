# Copyright 2026 QuantumBridge Contributors.
# Licensed under the Apache License, Version 2.0.
# This file is part of QuantumBridge SDK.
# This implementation is developed for the QuantumBridge native architecture.


def angle_embedding(circuit, features, wires=None, rotation: str = "ry"):
    wires = list(range(len(features))) if wires is None else list(wires)
    for value, wire in zip(features, wires):
        getattr(circuit, rotation)(float(value), wire)
    return circuit


def amplitude_embedding(circuit, features, wires=None, normalize: bool = True):
    values = [complex(value) for value in features]
    norm = sum(abs(value) ** 2 for value in values) ** 0.5
    if normalize and norm:
        values = [value / norm for value in values]
    circuit.metadata["amplitude_embedding"] = {
        "wires": list(range(circuit.num_qubits) if wires is None else wires),
        "features": [{"real": value.real, "imag": value.imag} for value in values],
        "mode": "metadata-only",
        "status": "planned-native-state-preparation",
    }
    return circuit
