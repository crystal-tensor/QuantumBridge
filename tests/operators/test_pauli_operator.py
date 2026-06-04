# Copyright 2026 QuantumBridge Contributors.
# Licensed under the Apache License, Version 2.0.
# This file is part of QuantumBridge SDK.
# This implementation is developed for the QuantumBridge native architecture.

from quantumbridge.operators import Pauli, PauliString


def test_pauli_operator_labels():
    assert Pauli("z").label == "Z"
    assert PauliString([(0, "X"), (1, "Z")]).terms == ((0, "X"), (1, "Z"))

