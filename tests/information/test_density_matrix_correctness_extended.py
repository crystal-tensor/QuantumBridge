# Copyright 2026 QuantumBridge Contributors.
# Licensed under the Apache License, Version 2.0.
# This file is part of QuantumBridge SDK.
# This implementation is developed for the QuantumBridge native architecture.

import numpy as np
import pytest

from quantumbridge import Circuit
from quantumbridge.information import DensityMatrix, Statevector, partial_trace, state_fidelity, von_neumann_entropy


def test_density_matrix_pure_state_trace_partial_trace_fidelity_entropy():
    state = Statevector.from_circuit(Circuit(2).h(0).cx(0, 1))
    rho = DensityMatrix.from_statevector(state)
    reduced = partial_trace(rho.data, keep=(0,), num_qubits=2)
    assert abs(rho.trace() - 1.0) < 1e-12
    np.testing.assert_allclose(reduced, np.eye(2) / 2, atol=1e-12)
    assert abs(state_fidelity([1, 0], [1, 0]) - 1.0) < 1e-12
    assert abs(von_neumann_entropy(np.eye(2) / 2) - 1.0) < 1e-12


def test_density_matrix_simple_mixed_state_and_invalid_dimensions():
    mixed = DensityMatrix(np.eye(2) / 2)
    assert abs(mixed.trace() - 1.0) < 1e-12
    with pytest.raises(ValueError, match="square"):
        DensityMatrix(np.ones((2, 3)))
    with pytest.raises(ValueError, match="power of two"):
        DensityMatrix(np.eye(3))

