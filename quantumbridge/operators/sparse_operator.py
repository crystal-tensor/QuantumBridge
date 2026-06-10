# Copyright 2026 QuantumBridge Contributors.
# Licensed under the Apache License, Version 2.0.
# This file is part of QuantumBridge SDK.
# This implementation is developed for the QuantumBridge native architecture.

from __future__ import annotations

from dataclasses import dataclass
from numbers import Number, Real
from typing import Iterable

from quantumbridge.utils.math import Hamiltonian, PauliString


@dataclass(frozen=True)
class SparsePauliOperator:
    terms: tuple[tuple[str, complex], ...]

    def __init__(self, terms: Iterable[tuple[str, Number]]):
        normalized = []
        for label, coeff in terms:
            label = label.upper()
            if any(ch not in "IXYZ" for ch in label):
                raise ValueError("QuantumBridge sparse Pauli labels may contain only I, X, Y, Z.")
            normalized.append((label, complex(coeff)))
        object.__setattr__(self, "terms", tuple(normalized))

    @classmethod
    def from_list(cls, terms: Iterable[tuple[str, Number]]) -> "SparsePauliOperator":
        return cls(terms)

    @classmethod
    def from_operator(cls, operator) -> "SparsePauliOperator":
        import numpy as np

        matrix = operator.data if hasattr(operator, "data") else np.asarray(operator, dtype=complex)
        if matrix.ndim != 2 or matrix.shape[0] != matrix.shape[1]:
            raise ValueError("QuantumBridge SparsePauliOperator.from_operator requires a square matrix.")
        dim = matrix.shape[0]
        if dim == 0 or dim & (dim - 1):
            raise ValueError("QuantumBridge operator dimension must be a power of two.")
        width = int(np.log2(dim))
        basis = ["I", "X", "Y", "Z"]
        terms = []
        for indices in np.ndindex(*(4,) * width):
            label = "".join(basis[index] for index in indices)
            pauli = SparsePauliOperator([(label, 1)]).matrix()
            coeff = np.trace(pauli.conj().T @ matrix) / dim
            if abs(coeff) > 1e-12:
                terms.append((label, coeff))
        return cls(terms)

    def to_list(self) -> list[tuple[str, complex]]:
        return list(self.terms)

    def to_hamiltonian(self) -> Hamiltonian:
        converted = []
        for label, coeff in self.terms:
            if abs(coeff.imag) > 1e-12:
                raise ValueError("QuantumBridge Hamiltonian conversion requires real Pauli coefficients.")
            pauli_terms = [(wire, char) for wire, char in enumerate(label) if char != "I"]
            converted.append((float(coeff.real), PauliString(pauli_terms)))
        return Hamiltonian(converted)

    def __add__(self, other: "SparsePauliOperator") -> "SparsePauliOperator":
        return SparsePauliOperator(self.terms + other.terms)

    def __mul__(self, scalar: Number) -> "SparsePauliOperator":
        return SparsePauliOperator((label, coeff * scalar) for label, coeff in self.terms)

    __rmul__ = __mul__

    def simplify(self, atol: float = 1e-12) -> "SparsePauliOperator":
        combined: dict[str, complex] = {}
        for label, coeff in self.terms:
            combined[label] = combined.get(label, 0j) + coeff
        return SparsePauliOperator((label, coeff) for label, coeff in combined.items() if abs(coeff) > atol)

    def adjoint(self) -> "SparsePauliOperator":
        return SparsePauliOperator((label, coeff.conjugate()) for label, coeff in self.terms)

    def tensor(self, other: "SparsePauliOperator") -> "SparsePauliOperator":
        return SparsePauliOperator((a + b, ca * cb) for a, ca in self.terms for b, cb in other.terms)

    def compose(self, other: "SparsePauliOperator") -> "SparsePauliOperator":
        from quantumbridge.information.operator import Operator

        return SparsePauliOperator.from_operator(Operator(self.matrix()) @ Operator(other.matrix()))

    def matrix(self):
        import numpy as np

        if not self.terms:
            return np.array([[0]], dtype=complex)
        width = len(self.terms[0][0])
        out = np.zeros((2 ** width, 2 ** width), dtype=complex)
        for label, coeff in self.terms:
            if len(label) != width:
                raise ValueError("QuantumBridge sparse Pauli terms must have equal label length.")
            pauli = PauliString([(wire, char) for wire, char in enumerate(label) if char != "I"])
            out += coeff * pauli.matrix(num_qubits=width)
        return out


SparsePauliOp = SparsePauliOperator
