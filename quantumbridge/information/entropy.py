# Copyright 2026 QuantumBridge Contributors.
# Licensed under the Apache License, Version 2.0.
# This file is part of QuantumBridge SDK.
# This implementation is developed for the QuantumBridge native architecture.

import numpy as np


def von_neumann_entropy(density_matrix, base: float = 2.0) -> float:
    values = np.linalg.eigvalsh(np.asarray(density_matrix, dtype=complex))
    values = values[values > 1e-12]
    return float(-np.sum(values * np.log(values) / np.log(base)))

