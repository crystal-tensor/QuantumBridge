# Copyright 2026 QuantumBridge Contributors.
# Licensed under the Apache License, Version 2.0.
# This file is part of QuantumBridge SDK.
# This implementation is developed for the QuantumBridge native architecture.

from math import cos, pi

import numpy as np
import pytest

from quantumbridge import Circuit, Hamiltonian, StatevectorDevice
from quantumbridge.operators import Pauli, PauliString, SparsePauliOperator


def test_pauli_multiplication_pauli_string_matrix_and_tensor():
    phase, product = Pauli("X") @ Pauli("Y")
    assert phase == 1j
    assert product.label == "Z"
    matrix = PauliString([(0, "X"), (1, "Z")]).matrix(num_qubits=2)
    assert matrix.shape == (4, 4)
    tensor = PauliString([(0, "X")]).tensor(PauliString([(1, "Z")]))
    assert tensor.terms == ((0, "X"), (1, "Z"))


def test_hamiltonian_sparse_addition_coefficients_and_invalid_label():
    circuit = Circuit(1).ry(pi / 3, 0)
    hamiltonian = Hamiltonian([(2.0, PauliString([(0, "Z")]))])
    value = StatevectorDevice().expectation(circuit, hamiltonian)
    assert abs(value - 2.0 * cos(pi / 3)) < 1e-10
    summed = SparsePauliOperator([("Z", 1.0)]) + SparsePauliOperator([("X", 0.5)])
    assert summed.terms == (("Z", 1.0), ("X", 0.5))
    with pytest.raises(ValueError, match="labels"):
        Pauli("A")
    with pytest.raises(ValueError, match="only I, X, Y, Z"):
        SparsePauliOperator([("A", 1.0)])

