# Copyright 2026 QuantumBridge Contributors.
# Licensed under the Apache License, Version 2.0.
# This file is part of QuantumBridge SDK.
# This implementation is developed for the QuantumBridge native architecture.

from __future__ import annotations

import numpy as np

from quantumbridge.devices import StatevectorDevice
from quantumbridge.utils.math import expectation_hamiltonian, probabilities_from_state


class Statevector:
    def __init__(self, data, normalize: bool = False):
        self.data = np.asarray(data, dtype=complex)
        if self.data.ndim != 1:
            raise ValueError("QuantumBridge Statevector data must be one-dimensional.")
        if len(self.data) == 0 or len(self.data) & (len(self.data) - 1):
            raise ValueError("QuantumBridge Statevector dimension must be a power of two.")
        if normalize:
            norm = np.linalg.norm(self.data)
            if norm == 0:
                raise ValueError("QuantumBridge cannot normalize a zero Statevector.")
            self.data = self.data / norm
        self.num_qubits = int(np.log2(len(self.data)))

    @classmethod
    def from_circuit(cls, circuit) -> "Statevector":
        return cls(StatevectorDevice().statevector(circuit))

    @classmethod
    def from_label(cls, label: str) -> "Statevector":
        if any(bit not in "01" for bit in label):
            raise ValueError("QuantumBridge Statevector labels may contain only 0 and 1.")
        data = np.zeros(1 << len(label), dtype=complex)
        data[int(label, 2)] = 1.0
        return cls(data)

    def is_valid(self, atol: float = 1e-10) -> bool:
        return bool(np.isclose(np.vdot(self.data, self.data), 1.0, atol=atol))

    def probabilities(self, wires=None) -> dict[str, float]:
        return probabilities_from_state(self.data, self.num_qubits, wires)

    def probabilities_dict(self, qargs=None) -> dict[str, float]:
        return self.probabilities(qargs)

    def expectation_value(self, observable) -> complex:
        if hasattr(observable, "to_hamiltonian"):
            return expectation_hamiltonian(self.data, self.num_qubits, observable.to_hamiltonian())
        matrix = observable.data if hasattr(observable, "data") else np.asarray(observable, dtype=complex)
        if matrix.shape != (len(self.data), len(self.data)):
            raise ValueError("QuantumBridge observable dimension must match Statevector dimension.")
        return np.vdot(self.data, matrix @ self.data)

    def evolve(self, operator) -> "Statevector":
        from quantumbridge.information.operator import Operator

        op = Operator.from_circuit(operator) if hasattr(operator, "operations") else operator
        matrix = op.data if isinstance(op, Operator) else np.asarray(op, dtype=complex)
        if matrix.shape != (len(self.data), len(self.data)):
            raise ValueError("QuantumBridge evolution operator dimension must match Statevector dimension.")
        return Statevector(matrix @ self.data)

    def sample_counts(self, shots: int, seed: int | None = None) -> dict[str, int]:
        if shots < 0:
            raise ValueError("QuantumBridge sample_counts shots cannot be negative.")
        rng = np.random.default_rng(seed)
        labels = [format(index, f"0{self.num_qubits}b") for index in range(len(self.data))]
        probs = np.array([abs(value) ** 2 for value in self.data], dtype=float)
        probs = probs / probs.sum()
        draws = rng.choice(len(labels), size=shots, p=probs)
        counts = {label: 0 for label in labels}
        for draw in draws:
            counts[labels[int(draw)]] += 1
        return {key: value for key, value in counts.items() if value}

    def to_operator(self):
        from quantumbridge.information.operator import Operator

        return Operator(np.outer(self.data, np.conjugate(self.data)))
