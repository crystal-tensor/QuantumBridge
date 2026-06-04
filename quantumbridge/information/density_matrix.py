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
