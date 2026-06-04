# Copyright 2026 QuantumBridge Contributors.
# Licensed under the Apache License, Version 2.0.
# This file is part of QuantumBridge SDK.
# This implementation is developed for the QuantumBridge native architecture.

from quantumbridge import Circuit
from quantumbridge.information import Statevector


def test_statevector_extended_probabilities():
    state = Statevector.from_circuit(Circuit(1).h(0))
    probs = state.probabilities()
    assert abs(probs["0"] - 0.5) < 1e-12
    assert abs(probs["1"] - 0.5) < 1e-12

