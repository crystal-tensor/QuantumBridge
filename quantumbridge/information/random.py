# Copyright 2026 QuantumBridge Contributors.
# Licensed under the Apache License, Version 2.0.
# This file is part of QuantumBridge SDK.
# This implementation is developed for the QuantumBridge native architecture.

from __future__ import annotations

import numpy as np

from quantumbridge.information.density_matrix import DensityMatrix
from quantumbridge.information.operator import Operator
from quantumbridge.information.statevector import Statevector


def _dimension(dims: int | tuple[int, ...] | list[int]) -> int:
    if isinstance(dims, int):
        dim = dims
    else:
        dim = int(np.prod(tuple(dims)))
    if dim <= 0:
        raise ValueError("QuantumBridge random dimensions must be positive.")
    return dim


def random_statevector(dims: int | tuple[int, ...] | list[int], seed: int | None = None) -> Statevector:
    dim = _dimension(dims)
    rng = np.random.default_rng(seed)
    vector = rng.normal(size=dim) + 1j * rng.normal(size=dim)
    return Statevector(vector, normalize=True)


def random_density_matrix(dims: int | tuple[int, ...] | list[int], seed: int | None = None, rank: int | None = None) -> DensityMatrix:
    dim = _dimension(dims)
    rank = dim if rank is None else int(rank)
    if not 1 <= rank <= dim:
        raise ValueError("QuantumBridge random_density_matrix rank must be between 1 and dimension.")
    rng = np.random.default_rng(seed)
    matrix = rng.normal(size=(dim, rank)) + 1j * rng.normal(size=(dim, rank))
    rho = matrix @ matrix.conj().T
    rho = rho / np.trace(rho)
    return DensityMatrix(rho)


def random_unitary(dims: int | tuple[int, ...] | list[int], seed: int | None = None) -> Operator:
    dim = _dimension(dims)
    rng = np.random.default_rng(seed)
    matrix = rng.normal(size=(dim, dim)) + 1j * rng.normal(size=(dim, dim))
    q, r = np.linalg.qr(matrix)
    phases = np.diag(r)
    phases = np.where(np.abs(phases) == 0, 1, phases / np.abs(phases))
    return Operator(q * phases)
