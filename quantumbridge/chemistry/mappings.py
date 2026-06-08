# Copyright 2026 QuantumBridge Contributors.
# Licensed under the Apache License, Version 2.0.
# This file is independently implemented for QuantumBridge SDK.
# No source code from Qiskit or PennyLane was copied.
# Design source: docs/roadmap/p2_upstream_integration_strategy_v0.1.md.

from __future__ import annotations

from quantumbridge.utils.math import Hamiltonian, PauliString

from .fermion import FermionicOp
from .qubit_hamiltonian import QubitHamiltonian


class JordanWignerMapper:
    mode = "Native Core"

    def map(self, operator: FermionicOp) -> QubitHamiltonian:
        terms = []
        for label, coeff in operator.terms:
            tokens = label.split()
            if label in {"", "I"}:
                terms.append((float(coeff.real), PauliString([])))
            elif len(tokens) == 2 and tokens[0].startswith("+_") and tokens[1].startswith("-_") and tokens[0][2:] == tokens[1][2:]:
                wire = int(tokens[0][2:])
                terms.append((0.5 * float(coeff.real), PauliString([])))
                terms.append((-0.5 * float(coeff.real), PauliString([(wire, "Z")])))
            elif len(tokens) == 1 and tokens[0].startswith("+_"):
                wire = int(tokens[0][2:])
                terms.append((0.5 * float(coeff.real), PauliString([(wire, "X")])))
                terms.append((-0.5 * float(coeff.imag or 1.0), PauliString([(wire, "Y")])))
            elif len(tokens) == 1 and tokens[0].startswith("-_"):
                wire = int(tokens[0][2:])
                terms.append((0.5 * float(coeff.real), PauliString([(wire, "X")])))
                terms.append((0.5 * float(coeff.imag or 1.0), PauliString([(wire, "Y")])))
            else:
                raise ValueError(f"QuantumBridge minimal Jordan-Wigner mapper does not support fermion label {label!r}.")
        return QubitHamiltonian(Hamiltonian(terms))


class ParityMapper:
    status = "planned"

    def map(self, operator):
        raise NotImplementedError("QuantumBridge ParityMapper is planned for a later P2 issue.")


class BravyiKitaevMapper:
    status = "planned"

    def map(self, operator):
        raise NotImplementedError("QuantumBridge BravyiKitaevMapper is planned for a later P2 issue.")
