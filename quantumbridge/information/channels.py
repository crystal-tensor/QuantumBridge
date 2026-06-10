# Copyright 2026 QuantumBridge Contributors.
# Licensed under the Apache License, Version 2.0.
# This file is part of QuantumBridge SDK.
# This implementation is developed for the QuantumBridge native architecture.

from __future__ import annotations

import numpy as np

from quantumbridge.information.density_matrix import DensityMatrix
from quantumbridge.information.operator import Operator


class Kraus:
    """Kraus representation of a quantum channel."""

    def __init__(self, data):
        self.data = tuple(np.asarray(op, dtype=complex) for op in data)
        if not self.data:
            raise ValueError("QuantumBridge Kraus channel requires at least one operator.")
        shape = self.data[0].shape
        if len(shape) != 2:
            raise ValueError("QuantumBridge Kraus operators must be matrices.")
        for op in self.data:
            if op.shape != shape:
                raise ValueError("QuantumBridge Kraus operators must have equal shape.")

    @classmethod
    def from_channel(cls, channel) -> "Kraus":
        if isinstance(channel, Kraus):
            return channel
        if hasattr(channel, "kraus"):
            return cls(channel.kraus())
        return cls([Operator(channel).data])

    def is_cptp(self, atol: float = 1e-10) -> bool:
        dim = self.data[0].shape[1]
        total = sum(op.conj().T @ op for op in self.data)
        return bool(np.allclose(total, np.eye(dim), atol=atol))

    def compose(self, other: "Kraus", front: bool = False) -> "Kraus":
        other = Kraus.from_channel(other)
        if front:
            return Kraus(a @ b for a in other.data for b in self.data)
        return Kraus(a @ b for a in self.data for b in other.data)

    def tensor(self, other: "Kraus") -> "Kraus":
        other = Kraus.from_channel(other)
        return Kraus(np.kron(a, b) for a in self.data for b in other.data)

    def evolve(self, state) -> DensityMatrix:
        rho = state.data if isinstance(state, DensityMatrix) else np.asarray(state, dtype=complex)
        if rho.ndim == 1:
            rho = np.outer(rho, rho.conj())
        out = sum(op @ rho @ op.conj().T for op in self.data)
        return DensityMatrix(out)

    def to_superop(self) -> "SuperOp":
        return SuperOp(sum(np.kron(op.conj(), op) for op in self.data))


class SuperOp:
    """Column-vectorized superoperator representation."""

    def __init__(self, data):
        self.data = np.asarray(data, dtype=complex)
        if self.data.ndim != 2 or self.data.shape[0] != self.data.shape[1]:
            raise ValueError("QuantumBridge SuperOp data must be square.")

    @classmethod
    def from_operator(cls, operator) -> "SuperOp":
        matrix = operator.data if isinstance(operator, Operator) else Operator(operator).data
        return cls(np.kron(matrix.conj(), matrix))

    def compose(self, other: "SuperOp", front: bool = False) -> "SuperOp":
        other = other if isinstance(other, SuperOp) else SuperOp(other)
        if self.data.shape != other.data.shape:
            raise ValueError("QuantumBridge SuperOp compose requires equal dimensions.")
        return SuperOp(other.data @ self.data if front else self.data @ other.data)

    def evolve(self, state) -> DensityMatrix:
        rho = state.data if isinstance(state, DensityMatrix) else np.asarray(state, dtype=complex)
        if rho.ndim == 1:
            rho = np.outer(rho, rho.conj())
        dim = rho.shape[0]
        vec = rho.reshape(-1, order="F")
        out = (self.data @ vec).reshape((dim, dim), order="F")
        return DensityMatrix(out)


class Choi:
    """Choi matrix representation generated from a SuperOp or Kraus channel."""

    def __init__(self, data):
        self.data = np.asarray(data, dtype=complex)
        if self.data.ndim != 2 or self.data.shape[0] != self.data.shape[1]:
            raise ValueError("QuantumBridge Choi data must be square.")

    @classmethod
    def from_channel(cls, channel) -> "Choi":
        superop = channel if isinstance(channel, SuperOp) else Kraus.from_channel(channel).to_superop()
        dim2 = superop.data.shape[0]
        dim = int(np.sqrt(dim2))
        reshaped = superop.data.reshape(dim, dim, dim, dim)
        choi = np.transpose(reshaped, (0, 2, 1, 3)).reshape(dim2, dim2)
        return cls(choi)


class Chi(Choi):
    """Minimal chi-like process matrix alias for native channel workflows."""
