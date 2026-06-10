# Copyright 2026 QuantumBridge Contributors.
# Licensed under the Apache License, Version 2.0.
# This file is part of QuantumBridge SDK.
# This implementation is developed for the QuantumBridge native architecture.

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

import numpy as np

from quantumbridge.utils.math import pauli_matrix


def _label_to_zx(label: str) -> tuple[list[bool], list[bool]]:
    z = []
    x = []
    for char in label:
        z.append(char in {"Z", "Y"})
        x.append(char in {"X", "Y"})
    return z, x


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

    @property
    def z(self) -> np.ndarray:
        return np.array([_label_to_zx(label)[0] for label in self.labels], dtype=bool)

    @property
    def x(self) -> np.ndarray:
        return np.array([_label_to_zx(label)[1] for label in self.labels], dtype=bool)

    def to_symplectic(self) -> tuple[np.ndarray, np.ndarray]:
        return self.z, self.x

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

    def commutes(self, other: "PauliList") -> np.ndarray:
        if self.num_qubits != other.num_qubits:
            raise ValueError("QuantumBridge PauliList commutes requires equal label widths.")
        left_z, left_x = self.to_symplectic()
        right_z, right_x = other.to_symplectic()
        values = []
        for z_row, x_row in zip(left_z, left_x):
            row = []
            for oz_row, ox_row in zip(right_z, right_x):
                parity = (np.logical_and(x_row, oz_row).sum() + np.logical_and(z_row, ox_row).sum()) % 2
                row.append(parity == 0)
            values.append(row)
        return np.array(values, dtype=bool)

    def anticommutes(self, other: "PauliList") -> np.ndarray:
        return np.logical_not(self.commutes(other))

    def weight(self) -> np.ndarray:
        return np.array([sum(char != "I" for char in label) for label in self.labels], dtype=int)

    def argsort(self, weight: bool = False) -> np.ndarray:
        keys = [(int(self.weight()[index]) if weight else 0, self.labels[index], index) for index in range(self.size)]
        return np.array([index for _, _, index in sorted(keys)], dtype=int)

    def sort(self, weight: bool = False) -> "PauliList":
        order = self.argsort(weight=weight)
        return PauliList(self.labels[int(index)] for index in order)

    def repeat(self, repeats: int) -> "PauliList":
        if repeats <= 0:
            raise ValueError("QuantumBridge PauliList repeat count must be positive.")
        return PauliList(label for label in self.labels for _ in range(repeats))

    def delete(self, indices) -> "PauliList":
        remaining = list(self.labels)
        for index in sorted(np.atleast_1d(indices).astype(int), reverse=True):
            del remaining[int(index)]
        return PauliList(remaining)

    def insert(self, index: int, values) -> "PauliList":
        insert_values = values if isinstance(values, PauliList) else PauliList(values)
        if insert_values.num_qubits != self.num_qubits:
            raise ValueError("QuantumBridge PauliList insert requires equal label widths.")
        labels = list(self.labels)
        for offset, label in enumerate(insert_values.labels):
            labels.insert(index + offset, label)
        return PauliList(labels)

    @staticmethod
    def _label_matrix(label: str) -> np.ndarray:
        out = np.array([[1]], dtype=complex)
        for char in label:
            out = np.kron(out, pauli_matrix(char))
        return out
