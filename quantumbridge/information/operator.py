# Copyright 2026 QuantumBridge Contributors.
# Licensed under the Apache License, Version 2.0.
# This file is part of QuantumBridge SDK.
# This implementation is developed for the QuantumBridge native architecture.

from __future__ import annotations

import numpy as np

from quantumbridge.utils.math import apply_unitary, gate_matrix


def _num_qubits_from_dim(dim: int) -> int:
    if dim <= 0 or dim & (dim - 1):
        raise ValueError("QuantumBridge quantum_info dimensions must be powers of two.")
    return int(np.log2(dim))


class Operator:
    """Dense linear operator with a Qiskit quantum_info-like core API."""

    def __init__(self, data):
        self.data = np.asarray(data, dtype=complex)
        if self.data.ndim != 2 or self.data.shape[0] != self.data.shape[1]:
            raise ValueError("QuantumBridge Operator data must be a square matrix.")
        self.num_qubits = _num_qubits_from_dim(self.data.shape[0])

    @classmethod
    def from_label(cls, label: str) -> "Operator":
        from quantumbridge.utils.math import pauli_matrix

        out = np.array([[1]], dtype=complex)
        for char in label.upper():
            if char not in "IXYZ":
                raise ValueError("QuantumBridge Operator labels may contain only I, X, Y, Z.")
            out = np.kron(out, pauli_matrix(char))
        return cls(out)

    @classmethod
    def from_circuit(cls, circuit) -> "Operator":
        size = 1 << circuit.num_qubits
        matrix = np.zeros((size, size), dtype=complex)
        for col in range(size):
            state = np.zeros(size, dtype=complex)
            state[col] = 1.0
            for op in circuit.operations:
                gate = gate_matrix(op.name, op.params, op.metadata)
                state = apply_unitary(state, gate, op.controls + op.targets, circuit.num_qubits)
            matrix[:, col] = state
        return cls(matrix)

    def is_unitary(self, atol: float = 1e-10) -> bool:
        eye = np.eye(self.data.shape[0], dtype=complex)
        return bool(np.allclose(self.data.conj().T @ self.data, eye, atol=atol))

    def adjoint(self) -> "Operator":
        return Operator(self.data.conj().T)

    def transpose(self) -> "Operator":
        return Operator(self.data.T)

    def conjugate(self) -> "Operator":
        return Operator(np.conjugate(self.data))

    def compose(self, other: "Operator", front: bool = False) -> "Operator":
        other = other if isinstance(other, Operator) else Operator(other)
        if self.data.shape != other.data.shape:
            raise ValueError("QuantumBridge Operator compose requires equal dimensions.")
        return Operator(other.data @ self.data if front else self.data @ other.data)

    def tensor(self, other: "Operator") -> "Operator":
        other = other if isinstance(other, Operator) else Operator(other)
        return Operator(np.kron(self.data, other.data))

    def expand(self, other: "Operator") -> "Operator":
        other = other if isinstance(other, Operator) else Operator(other)
        return Operator(np.kron(other.data, self.data))

    def power(self, n: int) -> "Operator":
        if not isinstance(n, int):
            raise ValueError("QuantumBridge Operator power requires an integer exponent.")
        return Operator(np.linalg.matrix_power(self.data, n))

    def equiv(self, other, atol: float = 1e-10) -> bool:
        other_data = other.data if isinstance(other, Operator) else np.asarray(other, dtype=complex)
        return bool(self.data.shape == other_data.shape and np.allclose(self.data, other_data, atol=atol))

    def to_matrix(self) -> np.ndarray:
        return np.array(self.data, copy=True)

    def __matmul__(self, other: "Operator") -> "Operator":
        return self.compose(other)

    def __eq__(self, other) -> bool:
        try:
            return self.equiv(other)
        except Exception:
            return False
