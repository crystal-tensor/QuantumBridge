# Copyright 2026 QuantumBridge Contributors.
# Licensed under the Apache License, Version 2.0.
# This file is part of QuantumBridge SDK.
# This implementation is developed for the QuantumBridge native architecture.

from __future__ import annotations

from numbers import Integral

import numpy as np

from quantumbridge.utils.math import pauli_matrix


_PHASE_FACTORS = (1, -1j, -1, 1j)
_PHASE_PREFIXES = ("", "-i", "-", "i")


def _validate_qargs(qargs, width: int, target_width: int) -> tuple[int, ...]:
    raw = tuple(qargs)
    if any(not isinstance(qarg, Integral) for qarg in raw):
        raise ValueError("QuantumBridge Pauli qargs must be integers.")
    selected = tuple(int(qarg) for qarg in raw)
    if len(selected) != width or len(set(selected)) != len(selected):
        raise ValueError("QuantumBridge Pauli qargs must be distinct and match the operand width.")
    if any(qarg < 0 or qarg >= target_width for qarg in selected):
        raise ValueError("QuantumBridge Pauli qargs are outside the target operator.")
    return selected


def _multiply_bodies(left: str, right: str) -> tuple[int, str]:
    phase = 0
    body = []
    for a, b in zip(left, right):
        if a == "I":
            body.append(b)
        elif b == "I":
            body.append(a)
        elif a == b:
            body.append("I")
        else:
            body.append(next(char for char in "XYZ" if char not in (a, b)))
            phase += 3 if (a, b) in (("X", "Y"), ("Y", "Z"), ("Z", "X")) else 1
    return phase % 4, "".join(body)


class Pauli:
    """A multi-qubit Pauli with an explicit phase exponent: (-i)**phase."""

    def __init__(self, data):
        if isinstance(data, Pauli):
            self._body = data._body
            self._phase = data.phase
        elif isinstance(data, str):
            phase = 0
            body = data
            for prefix, exponent in (("-i", 1), ("+i", 3), ("i", 3), ("-", 2), ("+", 0)):
                if body.startswith(prefix):
                    body = body[len(prefix):]
                    phase = exponent
                    break
            body = body.upper()
            if any(char not in "IXYZ" for char in body):
                raise ValueError("QuantumBridge Pauli labels may contain only I, X, Y, Z and a phase prefix.")
            self._body = body
            self._phase = phase
        elif isinstance(data, tuple) and len(data) in (2, 3):
            z = np.asarray(data[0], dtype=bool)
            x = np.asarray(data[1], dtype=bool)
            if z.ndim != 1 or z.shape != x.shape:
                raise ValueError("QuantumBridge Pauli symplectic arrays must have equal one-dimensional shape.")
            chars = ["Y" if zb and xb else "Z" if zb else "X" if xb else "I" for zb, xb in zip(z, x)]
            self._body = "".join(reversed(chars))
            self.phase = data[2] if len(data) == 3 else 0
        else:
            raise TypeError("QuantumBridge Pauli requires a label, Pauli, or (z, x, phase) tuple.")

    @property
    def label(self) -> str:
        return self.to_label()

    @property
    def phase(self) -> int:
        return self._phase

    @phase.setter
    def phase(self, value) -> None:
        if not isinstance(value, Integral):
            raise ValueError("QuantumBridge Pauli phase must be an integer.")
        self._phase = int(value) % 4

    @property
    def num_qubits(self) -> int:
        return len(self._body)

    @property
    def dim(self) -> tuple[int, int]:
        dimension = 1 << self.num_qubits
        return dimension, dimension

    @property
    def z(self) -> np.ndarray:
        return np.array([char in "ZY" for char in reversed(self._body)], dtype=bool)

    @z.setter
    def z(self, value) -> None:
        updated = Pauli((value, self.x, self.phase))
        if updated.num_qubits != self.num_qubits:
            raise ValueError("QuantumBridge Pauli z array must preserve the operator width.")
        self._body = updated._body

    @property
    def x(self) -> np.ndarray:
        return np.array([char in "XY" for char in reversed(self._body)], dtype=bool)

    @x.setter
    def x(self, value) -> None:
        updated = Pauli((self.z, value, self.phase))
        if updated.num_qubits != self.num_qubits:
            raise ValueError("QuantumBridge Pauli x array must preserve the operator width.")
        self._body = updated._body

    def input_dims(self, qargs=None) -> tuple[int, ...]:
        if qargs is None:
            return (2,) * self.num_qubits
        selected = tuple(qargs)
        _validate_qargs(selected, len(selected), self.num_qubits)
        return (2,) * len(selected)

    output_dims = input_dims

    def copy(self) -> "Pauli":
        return Pauli(self)

    def to_label(self) -> str:
        return _PHASE_PREFIXES[self.phase] + self._body

    def to_matrix(self, sparse: bool = False):
        matrix = np.array([[_PHASE_FACTORS[self.phase]]], dtype=complex)
        for char in self._body:
            matrix = np.kron(matrix, pauli_matrix(char))
        if sparse:
            from scipy.sparse import csr_matrix

            return csr_matrix(matrix)
        return matrix

    def _embedded(self, qargs, target_width: int) -> "Pauli":
        selected = _validate_qargs(qargs, self.num_qubits, target_width)
        chars = ["I"] * target_width
        for offset, qarg in enumerate(selected):
            chars[target_width - 1 - qarg] = self._body[self.num_qubits - 1 - offset]
        result = Pauli("".join(chars))
        result.phase = self.phase
        return result

    def compose(self, other, qargs=None, front: bool = False, inplace: bool = False) -> "Pauli":
        operand = other if isinstance(other, Pauli) else Pauli(other)
        if qargs is not None:
            operand = operand._embedded(qargs, self.num_qubits)
        if self.num_qubits != operand.num_qubits:
            raise ValueError("QuantumBridge Pauli composition requires equal widths unless qargs are provided.")
        left, right = (self, operand) if front else (operand, self)
        local_phase, body = _multiply_bodies(left._body, right._body)
        result = self if inplace else Pauli(body)
        phase = (self.phase + operand.phase + local_phase) % 4
        result._body = body
        result.phase = phase
        return result

    def dot(self, other, qargs=None, inplace: bool = False) -> "Pauli":
        return self.compose(other, qargs=qargs, front=True, inplace=inplace)

    def multiply(self, other) -> tuple[complex, "Pauli"]:
        """Return the legacy (global phase, phase-free Pauli) product."""
        result = self.dot(other)
        return _PHASE_FACTORS[result.phase], Pauli(result._body)

    def tensor(self, other) -> "Pauli":
        operand = other if isinstance(other, Pauli) else Pauli(other)
        result = Pauli(self._body + operand._body)
        result.phase = self.phase + operand.phase
        return result

    def expand(self, other) -> "Pauli":
        return Pauli(other).tensor(self)

    def commutes(self, other, qargs=None):
        from quantumbridge.operators.pauli_list import PauliList

        if isinstance(other, PauliList):
            return np.array([self.commutes(pauli, qargs=qargs) for pauli in other], dtype=bool)
        operand = other if isinstance(other, Pauli) else Pauli(other)
        if qargs is not None:
            operand = operand._embedded(qargs, self.num_qubits)
        if self.num_qubits != operand.num_qubits:
            raise ValueError("QuantumBridge Pauli commutation requires equal operand widths.")
        parity = sum(a != b and a != "I" and b != "I" for a, b in zip(self._body, operand._body))
        return parity % 2 == 0

    def anticommutes(self, other, qargs=None):
        return np.logical_not(self.commutes(other, qargs=qargs))

    def adjoint(self) -> "Pauli":
        result = self.copy()
        result.phase = -self.phase
        return result

    inverse = adjoint

    def conjugate(self) -> "Pauli":
        result = self.copy()
        result.phase = -self.phase + 2 * self._body.count("Y")
        return result

    def transpose(self) -> "Pauli":
        result = self.copy()
        result.phase = self.phase + 2 * self._body.count("Y")
        return result

    def power(self, n: int) -> "Pauli":
        if not isinstance(n, Integral):
            raise ValueError("QuantumBridge Pauli power requires an integer.")
        result = Pauli(self._body if n % 2 else "I" * self.num_qubits)
        result.phase = self.phase * int(n)
        return result

    def equiv(self, other) -> bool:
        return self._body == Pauli(other)._body

    def delete(self, qubits) -> "Pauli":
        indices = np.atleast_1d(qubits).tolist()
        selected = _validate_qargs(indices, len(indices), self.num_qubits)
        remaining = "".join(char for index, char in enumerate(self._body) if self.num_qubits - 1 - index not in selected)
        result = Pauli(remaining)
        result.phase = self.phase
        return result

    def insert(self, qubits, value) -> "Pauli":
        operand = value if isinstance(value, Pauli) else Pauli(value)
        if not isinstance(qubits, Integral) or not 0 <= qubits <= self.num_qubits:
            raise ValueError("QuantumBridge Pauli insertion index is outside the operator.")
        split = self.num_qubits - int(qubits)
        result = Pauli(self._body[:split] + operand._body + self._body[split:])
        result.phase = self.phase + operand.phase
        return result

    def to_instruction(self):
        from quantumbridge.information.operator import Operator

        return Operator(self.to_matrix()).to_instruction(name=self.to_label())

    def __getitem__(self, key) -> "Pauli":
        indices = np.atleast_1d(np.arange(self.num_qubits)[key]).tolist()
        body = "".join(self._body[self.num_qubits - 1 - index] for index in reversed(indices))
        return Pauli(body)

    def __len__(self) -> int:
        return self.num_qubits

    def __matmul__(self, other) -> "Pauli":
        return self.dot(other)

    def __xor__(self, other) -> "Pauli":
        return self.tensor(other)

    def __mul__(self, scalar) -> "Pauli":
        for phase, factor in enumerate(_PHASE_FACTORS):
            if scalar == factor:
                result = self.copy()
                result.phase = self.phase + phase
                return result
        raise ValueError("QuantumBridge Pauli scalar must be one of 1, -1, 1j, -1j.")

    __rmul__ = __mul__

    def __neg__(self) -> "Pauli":
        return -1 * self

    def __eq__(self, other) -> bool:
        if not isinstance(other, (str, Pauli)):
            return False
        try:
            operand = Pauli(other)
        except (ValueError, TypeError):
            return False
        return self._body == operand._body and self.phase == operand.phase

    def __repr__(self) -> str:
        return f"Pauli({self.to_label()!r})"
