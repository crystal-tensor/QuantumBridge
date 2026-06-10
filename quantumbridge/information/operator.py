# Copyright 2026 QuantumBridge Contributors.
# Licensed under the Apache License, Version 2.0.
# This file is part of QuantumBridge SDK.
# This implementation is developed for the QuantumBridge native architecture.

from __future__ import annotations

from copy import deepcopy
from numbers import Number

import numpy as np

from quantumbridge.core.operations import Instruction
from quantumbridge.utils.math import apply_unitary, gate_matrix


def _num_qubits_from_dim(dim: int) -> int:
    if dim <= 0 or dim & (dim - 1):
        raise ValueError("QuantumBridge quantum_info dimensions must be powers of two.")
    return int(np.log2(dim))


def _validate_qargs(qargs, num_qubits: int, width: int) -> tuple[int, ...]:
    normalized = tuple(int(qarg) for qarg in qargs)
    if len(normalized) != width:
        raise ValueError("QuantumBridge Operator qargs width must match the composed operator.")
    if len(set(normalized)) != len(normalized):
        raise ValueError("QuantumBridge Operator qargs must be distinct.")
    if any(qarg < 0 or qarg >= num_qubits for qarg in normalized):
        raise ValueError("QuantumBridge Operator qargs are outside this operator.")
    return normalized


def _index_to_bits(index: int, num_qubits: int) -> list[int]:
    return [(index >> (num_qubits - 1 - wire)) & 1 for wire in range(num_qubits)]


def _bits_to_index(bits: list[int] | tuple[int, ...]) -> int:
    out = 0
    for bit in bits:
        out = (out << 1) | int(bit)
    return out


def _expand_subsystem_operator(data: np.ndarray, qargs: tuple[int, ...], num_qubits: int) -> np.ndarray:
    size = 1 << num_qubits
    sub_dim = 1 << len(qargs)
    out = np.zeros((size, size), dtype=complex)
    for col in range(size):
        basis_bits = _index_to_bits(col, num_qubits)
        sub_col = _bits_to_index([basis_bits[qarg] for qarg in qargs])
        for sub_row in range(sub_dim):
            row_bits = basis_bits.copy()
            replacement_bits = _index_to_bits(sub_row, len(qargs))
            for offset, qarg in enumerate(qargs):
                row_bits[qarg] = replacement_bits[offset]
            row = _bits_to_index(row_bits)
            out[row, col] += data[sub_row, sub_col]
    return out


def _reverse_qubit_order(data: np.ndarray, num_qubits: int) -> np.ndarray:
    size = 1 << num_qubits
    permutation = np.zeros((size, size), dtype=complex)
    for source in range(size):
        bits = _index_to_bits(source, num_qubits)
        dest = _bits_to_index(list(reversed(bits)))
        permutation[dest, source] = 1.0
    return permutation @ data @ permutation.T


class Operator:
    """Dense linear operator with a Qiskit quantum_info-like core API."""

    def __init__(self, data):
        self.data = np.asarray(data, dtype=complex)
        if self.data.ndim != 2 or self.data.shape[0] != self.data.shape[1]:
            raise ValueError("QuantumBridge Operator data must be a square matrix.")
        self.num_qubits = _num_qubits_from_dim(self.data.shape[0])

    @property
    def dim(self) -> tuple[int, int]:
        return (self.data.shape[0], self.data.shape[1])

    def input_dims(self, qargs=None) -> tuple[int, ...]:
        if qargs is None:
            return (2,) * self.num_qubits
        qargs_tuple = tuple(qargs)
        return (2,) * len(_validate_qargs(qargs_tuple, self.num_qubits, len(qargs_tuple)))

    def output_dims(self, qargs=None) -> tuple[int, ...]:
        if qargs is None:
            return (2,) * self.num_qubits
        qargs_tuple = tuple(qargs)
        return (2,) * len(_validate_qargs(qargs_tuple, self.num_qubits, len(qargs_tuple)))

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
                if op.metadata.get("directive") and op.name in {"barrier", "delay"}:
                    continue
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

    def copy(self) -> "Operator":
        return Operator(np.array(self.data, copy=True))

    def compose(self, other: "Operator", qargs=None, front: bool = False) -> "Operator":
        other = other if isinstance(other, Operator) else Operator(other)
        other_data = other.data
        if qargs is not None:
            qargs_tuple = _validate_qargs(qargs, self.num_qubits, other.num_qubits)
            other_data = _expand_subsystem_operator(other.data, qargs_tuple, self.num_qubits)
        elif self.data.shape != other.data.shape:
            raise ValueError("QuantumBridge Operator compose requires equal dimensions unless qargs are provided.")
        return Operator(other_data @ self.data if front else self.data @ other_data)

    def dot(self, other: "Operator", qargs=None) -> "Operator":
        return self.compose(other, qargs=qargs)

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

    def tensorpower(self, n: int) -> "Operator":
        if not isinstance(n, int) or n < 0:
            raise ValueError("QuantumBridge Operator tensorpower requires a non-negative integer exponent.")
        out = Operator(np.array([[1]], dtype=complex))
        for _ in range(n):
            out = out.tensor(self)
        return out

    def reverse_qargs(self) -> "Operator":
        return Operator(_reverse_qubit_order(self.data, self.num_qubits))

    def is_identity(self, atol: float = 1e-10) -> bool:
        return bool(np.allclose(self.data, np.eye(self.data.shape[0], dtype=complex), atol=atol))

    def reshape(self, input_dims=None, output_dims=None, num_qubits: int | None = None) -> "Operator":
        if input_dims is not None and tuple(input_dims) != self.input_dims():
            raise ValueError("QuantumBridge Operator currently supports qubit input dimensions only.")
        if output_dims is not None and tuple(output_dims) != self.output_dims():
            raise ValueError("QuantumBridge Operator currently supports qubit output dimensions only.")
        if num_qubits is not None and int(num_qubits) != self.num_qubits:
            raise ValueError("QuantumBridge Operator reshape cannot change dense matrix size.")
        return self.copy()

    def equiv(self, other, atol: float = 1e-10) -> bool:
        other_data = other.data if isinstance(other, Operator) else np.asarray(other, dtype=complex)
        if self.data.shape != other_data.shape:
            return False
        if np.allclose(self.data, other_data, atol=atol):
            return True
        nonzero = np.argwhere(np.abs(other_data) > atol)
        if nonzero.size == 0:
            return bool(np.allclose(self.data, other_data, atol=atol))
        row, col = nonzero[0]
        if abs(other_data[row, col]) <= atol:
            return False
        phase = self.data[row, col] / other_data[row, col]
        if abs(abs(phase) - 1.0) > atol:
            return False
        return bool(np.allclose(self.data, phase * other_data, atol=atol))

    def to_instruction(self, name: str = "unitary", label: str | None = None) -> Instruction:
        return Instruction(
            name=label or name,
            num_qubits=self.num_qubits,
            metadata={"matrix": self.to_matrix(), "source": "quantumbridge.information.Operator"},
        )

    def to_matrix(self) -> np.ndarray:
        return np.array(self.data, copy=True)

    def __matmul__(self, other: "Operator") -> "Operator":
        return self.compose(other)

    def __mul__(self, scalar) -> "Operator":
        if not isinstance(scalar, Number):
            return NotImplemented
        return Operator(self.data * scalar)

    def __rmul__(self, scalar) -> "Operator":
        return self.__mul__(scalar)

    def __truediv__(self, scalar) -> "Operator":
        if not isinstance(scalar, Number):
            return NotImplemented
        return Operator(self.data / scalar)

    def __add__(self, other) -> "Operator":
        other_data = other.data if isinstance(other, Operator) else np.asarray(other, dtype=complex)
        if self.data.shape != other_data.shape:
            raise ValueError("QuantumBridge Operator addition requires equal dimensions.")
        return Operator(self.data + other_data)

    def __sub__(self, other) -> "Operator":
        other_data = other.data if isinstance(other, Operator) else np.asarray(other, dtype=complex)
        if self.data.shape != other_data.shape:
            raise ValueError("QuantumBridge Operator subtraction requires equal dimensions.")
        return Operator(self.data - other_data)

    def __xor__(self, n: int) -> "Operator":
        return self.tensorpower(n)

    def __copy__(self) -> "Operator":
        return self.copy()

    def __deepcopy__(self, memo) -> "Operator":
        copied = Operator(deepcopy(self.data, memo))
        memo[id(self)] = copied
        return copied

    def __eq__(self, other) -> bool:
        try:
            return self.equiv(other)
        except Exception:
            return False
