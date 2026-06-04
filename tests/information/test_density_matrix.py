# Copyright 2026 QuantumBridge Contributors.
# Licensed under the Apache License, Version 2.0.
# This file is part of QuantumBridge SDK.
# This implementation is developed for the QuantumBridge native architecture.

from quantumbridge import Circuit
from quantumbridge.information import DensityMatrix


def test_density_matrix_from_circuit_has_unit_trace():
    rho = DensityMatrix.from_circuit(Circuit(1).h(0))
    assert rho.data.shape == (2, 2)
    assert abs(rho.trace() - 1.0) < 1e-12

