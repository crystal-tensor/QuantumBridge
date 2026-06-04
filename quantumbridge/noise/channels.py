# Copyright 2026 QuantumBridge Contributors.
# Licensed under the Apache License, Version 2.0.
# This file is part of QuantumBridge SDK.
# This implementation is developed for the QuantumBridge native architecture.

import numpy as np


def _validate_probability(p: float) -> float:
    p = float(p)
    if not 0.0 <= p <= 1.0:
        raise ValueError("QuantumBridge noise probabilities must be between 0 and 1.")
    return p


class BitFlipChannel:
    name = "bit_flip"

    def __init__(self, probability: float):
        self.probability = _validate_probability(probability)

    def apply_probabilities(self, probabilities):
        p = self.probability
        return {"0": (1 - p) * probabilities.get("0", 0) + p * probabilities.get("1", 0), "1": p * probabilities.get("0", 0) + (1 - p) * probabilities.get("1", 0)}


class PhaseFlipChannel:
    name = "phase_flip"

    def __init__(self, probability: float):
        self.probability = _validate_probability(probability)


class DepolarizingChannel:
    name = "depolarizing"

    def __init__(self, probability: float):
        self.probability = _validate_probability(probability)

    def kraus(self):
        p = self.probability
        identity = np.eye(2, dtype=complex)
        x = np.array([[0, 1], [1, 0]], dtype=complex)
        y = np.array([[0, -1j], [1j, 0]], dtype=complex)
        z = np.array([[1, 0], [0, -1]], dtype=complex)
        return [np.sqrt(1 - p) * identity, np.sqrt(p / 3) * x, np.sqrt(p / 3) * y, np.sqrt(p / 3) * z]

