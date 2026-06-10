# Copyright 2026 QuantumBridge Contributors.
# Licensed under the Apache License, Version 2.0.
# This file is part of QuantumBridge SDK.
# This implementation is developed for the QuantumBridge native architecture.

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

import numpy as np

from quantumbridge.utils.math import pauli_matrix


@dataclass(frozen=True)
class PauliList:
    labels: tuple[str, ...]

    def __init__(self, labels: Iterable[str]):
        normalized = tuple(label.upper() for label in labels)
        if not normalized:
            raise ValueError("QuantumBridge PauliList requires at least one label.")
        width = len(normalized[0])
        for label in normalized:
            if len(label) != width:
                raise ValueError("QuantumBridge PauliList labels must have equal length.")
            if any(char not in "IXYZ" for char in label):
                raise ValueError("QuantumBridge PauliList labels may contain only I, X, Y, Z.")
        object.__setattr__(self, "labels", normalized)

    @classmethod
    def from_symplectic(cls, z: Iterable[Iterable[bool]], x: Iterable[Iterable[bool]]) -> "PauliList":
        labels = []
        for z_row, x_row in zip(z, x):
            label = []
            for z_bit, x_bit in zip(z_row, x_row):
                if x_bit and z_bit:
                    label.append("Y")
                elif x_bit:
                    label.append("X")
                elif z_bit:
                    label.append("Z")
                else:
                    label.append("I")
            labels.append("".join(label))
        return cls(labels)

    @property
    def size(self) -> int:
        return len(self.labels)

    @property
    def num_qubits(self) -> int:
        return len(self.labels[0])

    def to_labels(self) -> list[str]:
        return list(self.labels)

    def to_matrix(self) -> list[np.ndarray]:
        return [self._label_matrix(label) for label in self.labels]

    def tensor(self, other: "PauliList") -> "PauliList":
        return PauliList(a + b for a in self.labels for b in other.labels)

    def compose(self, other: "PauliList") -> "PauliList":
        from quantumbridge.operators.pauli import Pauli

        if self.num_qubits != other.num_qubits:
            raise ValueError("QuantumBridge PauliList compose requires equal label widths.")
        labels = []
        for left in self.labels:
            for right in other.labels:
                label = []
                for a, b in zip(left, right):
                    _, pauli = Pauli(a) @ Pauli(b)
                    label.append(pauli.label)
                labels.append("".join(label))
        return PauliList(labels)

    @staticmethod
    def _label_matrix(label: str) -> np.ndarray:
        out = np.array([[1]], dtype=complex)
        for char in label:
            out = np.kron(out, pauli_matrix(char))
        return out
