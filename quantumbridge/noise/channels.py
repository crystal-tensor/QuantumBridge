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


def _is_trace_preserving(kraus_ops, atol: float = 1e-10) -> bool:
    total = sum(op.conj().T @ op for op in kraus_ops)
    return bool(np.allclose(total, np.eye(total.shape[0]), atol=atol))


class BitFlipChannel:
    name = "bit_flip"

    def __init__(self, probability: float):
        self.probability = _validate_probability(probability)

    def apply_probabilities(self, probabilities):
        p = self.probability
        return {"0": (1 - p) * probabilities.get("0", 0) + p * probabilities.get("1", 0), "1": p * probabilities.get("0", 0) + (1 - p) * probabilities.get("1", 0)}

    def kraus(self):
        p = self.probability
        return [np.sqrt(1 - p) * np.eye(2, dtype=complex), np.sqrt(p) * np.array([[0, 1], [1, 0]], dtype=complex)]

    def is_trace_preserving(self, atol: float = 1e-10) -> bool:
        return _is_trace_preserving(self.kraus(), atol)


class PhaseFlipChannel:
    name = "phase_flip"

    def __init__(self, probability: float):
        self.probability = _validate_probability(probability)

    def kraus(self):
        p = self.probability
        return [np.sqrt(1 - p) * np.eye(2, dtype=complex), np.sqrt(p) * np.array([[1, 0], [0, -1]], dtype=complex)]

    def is_trace_preserving(self, atol: float = 1e-10) -> bool:
        return _is_trace_preserving(self.kraus(), atol)


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

    def is_trace_preserving(self, atol: float = 1e-10) -> bool:
        return _is_trace_preserving(self.kraus(), atol)


class QuantumChannel:
    name = "quantum_channel"

    def kraus(self):
        raise NotImplementedError("QuantumBridge quantum channels must define Kraus matrices.")

    def is_trace_preserving(self, atol: float = 1e-10) -> bool:
        return _is_trace_preserving(self.kraus(), atol)


class KrausChannel(QuantumChannel):
    name = "kraus"

    def __init__(self, kraus_ops, name: str = "kraus"):
        self._kraus = [np.asarray(op, dtype=complex) for op in kraus_ops]
        if not self._kraus:
            raise ValueError("QuantumBridge KrausChannel requires at least one operator.")
        self.name = name

    def kraus(self):
        return [op.copy() for op in self._kraus]


class AmplitudeDampingChannel:
    name = "amplitude_damping"

    def __init__(self, probability: float):
        self.probability = _validate_probability(probability)

    def kraus(self):
        p = self.probability
        return [
            np.array([[1, 0], [0, np.sqrt(1 - p)]], dtype=complex),
            np.array([[0, np.sqrt(p)], [0, 0]], dtype=complex),
        ]

    def is_trace_preserving(self, atol: float = 1e-10) -> bool:
        return _is_trace_preserving(self.kraus(), atol)


class PhaseDampingChannel:
    name = "phase_damping"

    def __init__(self, probability: float):
        self.probability = _validate_probability(probability)

    def kraus(self):
        p = self.probability
        return [
            np.sqrt(1 - p) * np.eye(2, dtype=complex),
            np.sqrt(p) * np.array([[1, 0], [0, 0]], dtype=complex),
            np.sqrt(p) * np.array([[0, 0], [0, 1]], dtype=complex),
        ]

    def is_trace_preserving(self, atol: float = 1e-10) -> bool:
        return _is_trace_preserving(self.kraus(), atol)
