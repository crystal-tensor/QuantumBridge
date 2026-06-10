# Copyright 2026 QuantumBridge Contributors.
# Licensed under the Apache License, Version 2.0.
# This file is part of QuantumBridge SDK.
# This implementation is developed for the QuantumBridge native architecture.

from __future__ import annotations

import numpy as np

from quantumbridge.core import Circuit
from quantumbridge.information.operator import Operator


class Clifford:
    """Small stabilizer-oriented Clifford wrapper for native H/S/CX workflows."""

    CLIFFORD_GATES = {"h", "s", "sdg", "x", "y", "z", "cx", "cz", "swap"}

    def __init__(self, data):
        if isinstance(data, Circuit):
            self._operator = Operator.from_circuit(data)
        elif isinstance(data, Operator):
            self._operator = Operator(data.data)
        else:
            self._operator = Operator(data)
        self.num_qubits = self._operator.num_qubits

    @classmethod
    def from_circuit(cls, circuit: Circuit) -> "Clifford":
        unsupported = [op.name for op in circuit.operations if op.name not in cls.CLIFFORD_GATES]
        if unsupported:
            raise ValueError(f"QuantumBridge Clifford supports only Clifford gates; unsupported: {unsupported!r}.")
        return cls(circuit)

    def to_operator(self) -> Operator:
        return Operator(self._operator.data)

    def to_matrix(self) -> np.ndarray:
        return self._operator.to_matrix()

    def compose(self, other: "Clifford", front: bool = False) -> "Clifford":
        return Clifford(self._operator.compose(other.to_operator(), front=front))

    def adjoint(self) -> "Clifford":
        return Clifford(self._operator.adjoint())

    def equiv(self, other, atol: float = 1e-10) -> bool:
        if isinstance(other, Clifford):
            other_op = other.to_operator()
        elif isinstance(other, Operator):
            other_op = other
        else:
            other_op = Operator(other)
        return self._operator.equiv(other_op, atol=atol)
