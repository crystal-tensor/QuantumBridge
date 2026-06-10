# Copyright 2026 QuantumBridge Contributors.
# Licensed under the Apache License, Version 2.0.
# This file is part of QuantumBridge SDK.
# This implementation is developed for the QuantumBridge native architecture.

from __future__ import annotations

import numpy as np

from typing import Union

from .statevector import Statevector


class DensityMatrix:
    def __init__(self, data):
        self.data = np.asarray(data, dtype=complex)
        if self.data.ndim != 2 or self.data.shape[0] != self.data.shape[1]:
            raise ValueError("QuantumBridge DensityMatrix data must be a square matrix.")
        dim = self.data.shape[0]
        if dim == 0 or dim & (dim - 1):
            raise ValueError("QuantumBridge DensityMatrix dimension must be a power of two.")

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
        from quantumbridge.utils.math import bit_at

        selected = tuple(range(self.num_qubits) if wires is None else wires)
        probs: dict[str, float] = {}
        diag = np.real_if_close(np.diag(self.data))
        for index, value in enumerate(diag):
            key = "".join(str(bit_at(index, wire, self.num_qubits)) for wire in selected)
            probs[key] = probs.get(key, 0.0) + float(np.real(value))
        return probs

    def expectation_value(self, observable) -> complex:
        matrix = observable.data if hasattr(observable, "data") else np.asarray(observable, dtype=complex)
        if matrix.shape != self.data.shape:
            raise ValueError("QuantumBridge observable dimension must match DensityMatrix dimension.")
        return np.trace(self.data @ matrix)

    def evolve(self, operator) -> "DensityMatrix":
        from quantumbridge.information.operator import Operator

        op = Operator.from_circuit(operator) if hasattr(operator, "operations") else operator
        matrix = op.data if isinstance(op, Operator) else np.asarray(op, dtype=complex)
        if matrix.shape != self.data.shape:
            raise ValueError("QuantumBridge evolution operator dimension must match DensityMatrix dimension.")
        return DensityMatrix(matrix @ self.data @ matrix.conj().T)
