# Copyright 2026 QuantumBridge Contributors.
# Licensed under the Apache License, Version 2.0.
# This file is part of QuantumBridge SDK.
# This implementation is developed for the QuantumBridge native architecture.

from quantumbridge import Circuit
from quantumbridge.qml import angle_embedding, basic_entangler


def test_qml_template_basic_builds_circuit():
    circuit = angle_embedding(Circuit(2), [0.1, 0.2])
    basic_entangler(circuit, [0.3, 0.4])
    assert [op.name for op in circuit.operations] == ["ry", "ry", "ry", "ry", "cx"]

