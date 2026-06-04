# Copyright 2026 QuantumBridge Contributors.
# Licensed under the Apache License, Version 2.0.
# This file is part of QuantumBridge SDK.
# This implementation is developed for the QuantumBridge native architecture.

import numpy as np

from quantumbridge import Circuit, StatevectorDevice
from quantumbridge.operators import Pauli, PauliString, SparsePauliOperator
from quantumbridge.utils.math import Hamiltonian, PauliZ


def test_p1_operator_hamiltonian_coverage():
    phase, pauli = Pauli("Z") @ Pauli("X")
    assert phase == 1j
    assert pauli.label == "Y"
    assert PauliString([(0, "I")]).matrix().shape == (2, 2)
    ham = Hamiltonian([(1, PauliZ(0))]) + 2 * Hamiltonian([(0.5, PauliZ(0))])
    assert len(ham.terms) == 2
    value = StatevectorDevice().expectation(Circuit(1), ham)
    assert abs(value - 2.0) < 1e-12
    sparse = SparsePauliOperator([("ZI", 1), ("IX", 0.5)])
    matrix = sparse.matrix()
    assert matrix.shape == (4, 4)
    np.testing.assert_allclose(matrix, matrix.conj().T)

