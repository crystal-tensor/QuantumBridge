# Copyright 2026 QuantumBridge Contributors.
# Licensed under the Apache License, Version 2.0.
# This file is part of QuantumBridge SDK.
# This implementation is developed for the QuantumBridge native architecture.

from __future__ import annotations

import numpy as np


def _as_matrix(obj) -> np.ndarray:
    return np.asarray(obj.data if hasattr(obj, "data") else obj, dtype=complex)


def _matrix_sqrt_psd(matrix: np.ndarray) -> np.ndarray:
    values, vectors = np.linalg.eigh((matrix + matrix.conj().T) / 2)
    values = np.clip(values.real, 0.0, None)
    return vectors @ np.diag(np.sqrt(values)) @ vectors.conj().T


def purity(state) -> float:
    matrix = _as_matrix(state)
    if matrix.ndim == 1:
        return float(np.real_if_close(np.vdot(matrix, matrix) ** 2))
    return float(np.real_if_close(np.trace(matrix @ matrix)))


def trace_distance(a, b) -> float:
    delta = _as_matrix(a) - _as_matrix(b)
    singular_values = np.linalg.svd(delta, compute_uv=False)
    return float(0.5 * np.sum(singular_values))


def process_fidelity(channel_a, channel_b=None) -> float:
    a = _as_matrix(channel_a)
    b = np.eye(a.shape[0], dtype=complex) if channel_b is None else _as_matrix(channel_b)
    if a.shape != b.shape:
        raise ValueError("QuantumBridge process_fidelity requires equal dimensions.")
    dim = a.shape[0]
    return float(abs(np.trace(a.conj().T @ b)) ** 2 / (dim * dim))


def average_gate_fidelity(channel, target=None) -> float:
    matrix = _as_matrix(channel)
    dim = matrix.shape[0]
    return float((dim * process_fidelity(matrix, target) + 1) / (dim + 1))


def state_fidelity_general(a, b) -> float:
    from quantumbridge.information.density_matrix import DensityMatrix
    from quantumbridge.information.statevector import Statevector

    if isinstance(a, Statevector) and isinstance(b, Statevector):
        return float(abs(np.vdot(a.data, b.data)) ** 2)
    rho = DensityMatrix.from_statevector(a).data if isinstance(a, Statevector) else _as_matrix(a)
    sigma = DensityMatrix.from_statevector(b).data if isinstance(b, Statevector) else _as_matrix(b)
    root = _matrix_sqrt_psd(rho)
    inner = root @ sigma @ root
    return float(np.real_if_close(np.trace(_matrix_sqrt_psd(inner)) ** 2))
