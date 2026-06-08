# Copyright 2026 QuantumBridge Contributors.
# Licensed under the Apache License, Version 2.0.
# This file is independently implemented for QuantumBridge SDK.
# No source code from Qiskit or PennyLane was copied.
# Design source: docs/roadmap/p2_upstream_integration_strategy_v0.1.md.

from __future__ import annotations

import numpy as np

from quantumbridge.utils.math import Hamiltonian, PauliString


class QubitHamiltonian:
    def __init__(self, terms):
        self.hamiltonian = terms if isinstance(terms, Hamiltonian) else Hamiltonian(terms)

    @property
    def terms(self):
        return self.hamiltonian.terms

    def to_quantumbridge(self) -> Hamiltonian:
        return self.hamiltonian

    def matrix(self, num_qubits: int | None = None) -> np.ndarray:
        if num_qubits is None:
            num_qubits = 1 + max((wire for _, pauli in self.terms for wire, _ in pauli.terms), default=0)
        out = np.zeros((1 << num_qubits, 1 << num_qubits), dtype=complex)
        for coeff, pauli in self.terms:
            out += coeff * pauli.matrix(num_qubits)
        return out

    @classmethod
    def from_pauli_terms(cls, terms):
        return cls([(coeff, PauliString(paulis)) for coeff, paulis in terms])
