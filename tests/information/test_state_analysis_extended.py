# This file is independently implemented for QuantumBridge SDK.
# No source code from Qiskit or PennyLane was copied.

import numpy as np

from quantumbridge.information import (
    DensityMatrix,
    Operator,
    Statevector,
    anti_commutator,
    commutator,
    concurrence,
    double_commutator,
    entanglement_of_formation,
    entropy,
    mutual_information,
    negativity,
    schmidt_decomposition,
    shannon_entropy,
    von_neumann_entropy,
)


def _bell_state():
    return Statevector(np.array([1, 0, 0, 1], dtype=complex) / np.sqrt(2))


def test_entropy_entanglement_and_negativity_for_bell_state():
    bell = _bell_state()
    rho = DensityMatrix.from_statevector(bell)

    assert abs(entropy(bell)) < 1e-12
    assert abs(von_neumann_entropy(rho)) < 1e-12
    assert abs(mutual_information(rho) - 2) < 1e-12
    assert abs(concurrence(bell) - 1) < 1e-12
    assert abs(concurrence(rho) - 1) < 1e-12
    assert abs(entanglement_of_formation(rho) - 1) < 1e-12
    assert abs(negativity(rho, [0]) - 0.5) < 1e-12


def test_separable_state_and_shannon_entropy():
    state = Statevector.from_label("01")

    assert mutual_information(state) == 0
    assert concurrence(state) == 0
    assert entanglement_of_formation(state) == 0
    assert negativity(state, [0]) == 0
    assert abs(shannon_entropy([0.5, 0.5]) - 1) < 1e-12


def test_schmidt_decomposition_reconstructs_complex_state():
    vector = np.array([1, 1j, -0.5, 0.25j], dtype=complex)
    vector /= np.linalg.norm(vector)
    decomposition = schmidt_decomposition(vector, [0])
    reconstructed = sum(
        value * np.kron(left.data, right.data)
        for value, left, right in decomposition
    )

    np.testing.assert_allclose(reconstructed, vector, atol=1e-12)
    assert abs(sum(value * value for value, _, _ in decomposition) - 1) < 1e-12


def test_operator_commutator_family():
    x = Operator.from_label("X")
    y = Operator.from_label("Y")
    z = Operator.from_label("Z")

    np.testing.assert_allclose(commutator(x, y).data, 2j * z.data, atol=1e-12)
    np.testing.assert_allclose(anti_commutator(x, y).data, np.zeros((2, 2)), atol=1e-12)
    np.testing.assert_allclose(
        double_commutator(x, y, z).data,
        np.zeros((2, 2)),
        atol=1e-12,
    )
