# Copyright 2026 QuantumBridge Contributors.
# Licensed under the Apache License, Version 2.0.
# This file is part of QuantumBridge SDK.
# This implementation is developed for the QuantumBridge native architecture.

from __future__ import annotations

import numpy as np

from typing import Union

from .statevector import Statevector
from quantumbridge.utils.math import bit_at


def _validate_qargs(qargs, num_qubits: int) -> tuple[int, ...]:
    normalized = tuple(range(num_qubits) if qargs is None else (int(qarg) for qarg in qargs))
    if len(set(normalized)) != len(normalized):
        raise ValueError("QuantumBridge DensityMatrix qargs must be distinct.")
    if any(qarg < 0 or qarg >= num_qubits for qarg in normalized):
        raise ValueError("QuantumBridge DensityMatrix qargs are outside this state.")
    return normalized


def _reverse_permutation(num_qubits: int) -> np.ndarray:
    size = 1 << num_qubits
    permutation = np.zeros((size, size), dtype=complex)
    for source in range(size):
        bits = format(source, f"0{num_qubits}b")
        dest = int(bits[::-1], 2)
        permutation[dest, source] = 1.0
    return permutation


class DensityMatrix:
    def __init__(self, data):
        self.data = np.asarray(data, dtype=complex)
        if self.data.ndim != 2 or self.data.shape[0] != self.data.shape[1]:
            raise ValueError("QuantumBridge DensityMatrix data must be a square matrix.")
        dim = self.data.shape[0]
        if dim == 0 or dim & (dim - 1):
            raise ValueError("QuantumBridge DensityMatrix dimension must be a power of two.")

    @property
    def dim(self) -> tuple[int, int]:
        return self.data.shape

    def dims(self, qargs=None) -> tuple[int, ...]:
        return (2,) * len(_validate_qargs(qargs, self.num_qubits))

    @classmethod
    def from_statevector(cls, statevector: Union[Statevector, np.ndarray]) -> "DensityMatrix":
        vector = statevector.data if isinstance(statevector, Statevector) else np.asarray(statevector, dtype=complex)
        return cls(np.outer(vector, np.conjugate(vector)))

    @classmethod
    def from_circuit(cls, circuit) -> "DensityMatrix":
        return cls.from_statevector(Statevector.from_circuit(circuit))

    def trace(self) -> complex:
        return np.trace(self.data)

    @property
    def num_qubits(self) -> int:
        return int(np.log2(self.data.shape[0]))

    def is_valid(self, atol: float = 1e-10) -> bool:
        hermitian = np.allclose(self.data, self.data.conj().T, atol=atol)
        trace_one = np.isclose(np.trace(self.data), 1.0, atol=atol)
        positive = np.all(np.linalg.eigvalsh(self.data) >= -atol)
        return bool(hermitian and trace_one and positive)

    def purity(self) -> float:
        return float(np.real_if_close(np.trace(self.data @ self.data)))

    def probabilities(self, wires=None) -> dict[str, float]:
        selected = tuple(range(self.num_qubits) if wires is None else wires)
        probs: dict[str, float] = {}
        diag = np.real_if_close(np.diag(self.data))
        for index, value in enumerate(diag):
            key = "".join(str(bit_at(index, wire, self.num_qubits)) for wire in selected)
            probs[key] = probs.get(key, 0.0) + float(np.real(value))
        return probs

    def probabilities_dict(self, qargs=None) -> dict[str, float]:
        return self.probabilities(qargs)

    def expectation_value(self, observable, qargs=None) -> complex:
        from quantumbridge.information.operator import Operator

        matrix = observable.data if hasattr(observable, "data") else np.asarray(observable, dtype=complex)
        if qargs is not None:
            qargs_tuple = _validate_qargs(qargs, self.num_qubits)
            matrix = Operator(np.eye(self.data.shape[0], dtype=complex)).compose(Operator(matrix), qargs=qargs_tuple).data
        if matrix.shape != self.data.shape:
            raise ValueError("QuantumBridge observable dimension must match DensityMatrix dimension.")
        return np.trace(self.data @ matrix)

    def evolve(self, operator, qargs=None) -> "DensityMatrix":
        from quantumbridge.information.operator import Operator

        op = Operator.from_circuit(operator) if hasattr(operator, "operations") else operator
        matrix = op.data if isinstance(op, Operator) else np.asarray(op, dtype=complex)
        if qargs is not None:
            qargs_tuple = _validate_qargs(qargs, self.num_qubits)
            dim = 1 << len(qargs_tuple)
            if matrix.shape != (dim, dim):
                raise ValueError("QuantumBridge subsystem evolution operator dimension must match qargs.")
            matrix = Operator(np.eye(self.data.shape[0], dtype=complex)).compose(Operator(matrix), qargs=qargs_tuple).data
        if matrix.shape != self.data.shape:
            raise ValueError("QuantumBridge evolution operator dimension must match DensityMatrix dimension.")
        return DensityMatrix(matrix @ self.data @ matrix.conj().T)

    def tensor(self, other) -> "DensityMatrix":
        other_state = other if isinstance(other, DensityMatrix) else DensityMatrix(other)
        return DensityMatrix(np.kron(self.data, other_state.data))

    def expand(self, other) -> "DensityMatrix":
        other_state = other if isinstance(other, DensityMatrix) else DensityMatrix(other)
        return DensityMatrix(np.kron(other_state.data, self.data))

    def reverse_qargs(self) -> "DensityMatrix":
        permutation = _reverse_permutation(self.num_qubits)
        return DensityMatrix(permutation @ self.data @ permutation.T)

    def sample_counts(self, shots: int, qargs=None, seed: int | None = None) -> dict[str, int]:
        if shots < 0:
            raise ValueError("QuantumBridge DensityMatrix sample_counts shots cannot be negative.")
        labels = sorted(self.probabilities(qargs))
        probs_dict = self.probabilities(qargs)
        probs = np.array([probs_dict[label] for label in labels], dtype=float)
        probs = probs / probs.sum()
        rng = np.random.default_rng(seed)
        draws = rng.choice(len(labels), size=shots, p=probs)
        counts = {label: 0 for label in labels}
        for draw in draws:
            counts[labels[int(draw)]] += 1
        return {key: value for key, value in counts.items() if value}

    def sample_memory(self, shots: int, qargs=None, seed: int | None = None) -> list[str]:
        if shots < 0:
            raise ValueError("QuantumBridge DensityMatrix sample_memory shots cannot be negative.")
        labels = sorted(self.probabilities(qargs))
        probs_dict = self.probabilities(qargs)
        probs = np.array([probs_dict[label] for label in labels], dtype=float)
        probs = probs / probs.sum()
        rng = np.random.default_rng(seed)
        draws = rng.choice(len(labels), size=shots, p=probs)
        return [labels[int(draw)] for draw in draws]

    def copy(self) -> "DensityMatrix":
        return DensityMatrix(np.array(self.data, copy=True))

    def to_statevector(self, atol: float = 1e-10) -> Statevector:
        values, vectors = np.linalg.eigh(self.data)
        index = int(np.argmax(values))
        if not np.isclose(values[index], 1.0, atol=atol):
            raise ValueError("QuantumBridge DensityMatrix is not a pure state.")
        if np.count_nonzero(values > atol) != 1:
            raise ValueError("QuantumBridge DensityMatrix is not a pure state.")
        return Statevector(vectors[:, index])
