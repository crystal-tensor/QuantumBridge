# Copyright 2026 QuantumBridge Contributors.
# Licensed under the Apache License, Version 2.0.
# This file is part of QuantumBridge SDK.
# This implementation is developed for the QuantumBridge native architecture.


def angle_embedding(circuit, features, wires=None, rotation: str = "ry"):
    wires = list(range(len(features))) if wires is None else list(wires)
    for value, wire in zip(features, wires):
        getattr(circuit, rotation)(float(value), wire)
    return circuit

