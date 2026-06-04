# Copyright 2026 QuantumBridge Contributors.
# Licensed under the Apache License, Version 2.0.
# This file is part of QuantumBridge SDK.
# This implementation is developed for the QuantumBridge native architecture.

from __future__ import annotations

from dataclasses import dataclass
from numbers import Real
from typing import Iterable

from quantumbridge.utils.math import Hamiltonian, PauliString


@dataclass(frozen=True)
class SparsePauliOperator:
    terms: tuple[tuple[str, float], ...]

    def __init__(self, terms: Iterable[tuple[str, Real]]):
        normalized = []
        for label, coeff in terms:
            label = label.upper()
            if any(ch not in "IXYZ" for ch in label):
                raise ValueError("QuantumBridge sparse Pauli labels may contain only I, X, Y, Z.")
            normalized.append((label, float(coeff)))
        object.__setattr__(self, "terms", tuple(normalized))

    def to_hamiltonian(self) -> Hamiltonian:
        converted = []
        for label, coeff in self.terms:
            pauli_terms = [(wire, char) for wire, char in enumerate(label) if char != "I"]
            converted.append((coeff, PauliString(pauli_terms)))
        return Hamiltonian(converted)

    def __add__(self, other: "SparsePauliOperator") -> "SparsePauliOperator":
        return SparsePauliOperator(self.terms + other.terms)

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
