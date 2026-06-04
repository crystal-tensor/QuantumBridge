# Copyright 2026 QuantumBridge Contributors.
# Licensed under the Apache License, Version 2.0.
# This file is part of QuantumBridge SDK.
# This implementation is developed for the QuantumBridge native architecture.

import numpy as np


def partial_trace(density_matrix, keep: tuple[int, ...], num_qubits: int):
    rho = np.asarray(density_matrix, dtype=complex).reshape([2] * (2 * num_qubits))
    trace_out = [wire for wire in range(num_qubits) if wire not in keep]
    for wire in reversed(trace_out):
        rho = np.trace(rho, axis1=wire, axis2=wire + rho.ndim // 2)
    dim = 2 ** len(keep)
    return rho.reshape((dim, dim))

