# This file is independently implemented for QuantumBridge SDK.
# No source code from Qiskit or PennyLane was copied.

from itertools import product

import numpy as np
import pytest

from quantumbridge import Circuit, StatevectorDevice
from quantumbridge.information import DensityMatrix, Statevector, random_pauli, random_pauli_list
from quantumbridge.operators import Pauli, PauliList


def test_all_one_qubit_phase_products_equal_dense_multiplication():
    labels = [prefix + char for prefix in ("", "-i", "-", "i") for char in "IXYZ"]
    for left, right in product(labels, repeat=2):
        a, b = Pauli(left), Pauli(right)
        np.testing.assert_array_equal((a @ b).to_matrix(), a.to_matrix() @ b.to_matrix())
        np.testing.assert_array_equal(a.compose(b).to_matrix(), b.to_matrix() @ a.to_matrix())
    assert (Pauli("X") @ Pauli("Y")).to_label() == "iZ"
    assert Pauli("X").compose("Y").to_label() == "-iZ"
    assert Pauli("Z").multiply("X") == (1j, Pauli("Y"))


def test_multi_qubit_symplectic_order_phases_and_transforms():
    pauli = Pauli("-iXYZ")
    np.testing.assert_array_equal(pauli.z, [True, True, False])
    np.testing.assert_array_equal(pauli.x, [False, True, True])
    assert Pauli((pauli.z, pauli.x, pauli.phase)) == pauli
    assert pauli.dim == (8, 8)
    assert pauli.input_dims([0, 2]) == (2, 2)
    np.testing.assert_allclose(pauli.adjoint().to_matrix(), pauli.to_matrix().conj().T)
    np.testing.assert_allclose(pauli.conjugate().to_matrix(), pauli.to_matrix().conj())
    np.testing.assert_allclose(pauli.transpose().to_matrix(), pauli.to_matrix().T)
    assert pauli[0].to_label() == "Z"
    assert pauli[[2, 0]].to_label() == "ZX"
    assert pauli.delete(0).to_label() == "-iXY"
    assert pauli.insert(0, "iX").to_label() == "XYZX"
    for exponent in (-1, 0, 1, 2, 3, 4):
        np.testing.assert_array_equal(pauli.power(exponent).to_matrix(), np.linalg.matrix_power(pauli.to_matrix(), exponent))


def test_qargs_and_inplace_composition_preserve_phase():
    base = Pauli("iXYZ")
    operand = Pauli("-iYX")
    embedded = Pauli("-iYIX")
    np.testing.assert_array_equal(base.dot(operand, qargs=[0, 2]).to_matrix(), base.to_matrix() @ embedded.to_matrix())
    original = base.to_matrix()
    assert base.compose(operand, qargs=[0, 2], inplace=True) is base
    np.testing.assert_array_equal(base.to_matrix(), embedded.to_matrix() @ original)
    with pytest.raises(ValueError, match="distinct"):
        base.compose(operand, qargs=[1, 1])
    with pytest.raises(ValueError, match="width"):
        base.compose(Pauli("X"))
    np.testing.assert_array_equal(Pauli("XYZ").commutes(PauliList(["X", "Z"]), qargs=[0]), [False, True])


def test_pauli_list_broadcasting_and_cartesian_tensor():
    left = PauliList(["X", "Y"])
    right = PauliList(["Y", "Z"])
    assert left.dot(right).to_labels() == ["iZ", "iX"]
    assert left.compose(right).to_labels() == ["-iZ", "-iX"]
    assert left.dot(Pauli("Z")).to_labels() == ["-iY", "iX"]
    assert left.tensor(right).to_labels() == ["XY", "XZ", "YY", "YZ"]
    assert left.expand(right).to_labels() == ["YX", "YY", "ZX", "ZY"]
    with pytest.raises(ValueError, match="row counts"):
        left.dot(PauliList(["X", "Y", "Z"]))


def test_list_symplectic_validation_copy_and_phase_assignment():
    paulis = PauliList(["iXY", "-ZI"])
    cloned = PauliList.from_symplectic(paulis.z, paulis.x, paulis.phase)
    assert cloned == paulis
    clone = paulis.copy()
    clone.phase = [1, 0]
    clone[0] = "-XX"
    assert clone.to_labels() == ["-XX", "ZI"]
    assert paulis.to_labels() == ["iXY", "-ZI"]
    with pytest.raises(ValueError, match="shape"):
        PauliList.from_symplectic([[True]], [[False, True]])
    with pytest.raises(ValueError, match="phase"):
        PauliList.from_symplectic([[True]], [[False]], [0, 1])


def test_empty_lists_preserve_width_after_selection_and_deletion():
    paulis = PauliList(["XX", "ZY"])
    empty = paulis.delete([0, 1])
    assert empty.shape == (0, 2)
    assert empty.to_matrix(array=True).shape == (0, 4, 4)
    assert empty.copy().shape == (0, 2)
    assert paulis[[]].shape == (0, 2)


def test_commutation_sort_unique_and_valid_groups():
    paulis = PauliList(["XX", "YY", "ZZ", "IX", "ZI", "iXX", "XX"])
    np.testing.assert_array_equal(paulis.commutes("XX"), [True, True, True, True, False, True, True])
    np.testing.assert_array_equal(paulis.commutes_with_all(["XX", "YY"]), [0, 1, 2, 5, 6])
    unique, indices, counts = paulis.unique(return_index=True, return_counts=True)
    assert unique.to_labels() == ["XX", "YY", "ZZ", "IX", "ZI", "iXX"]
    np.testing.assert_array_equal(indices, [0, 1, 2, 3, 4, 5])
    np.testing.assert_array_equal(counts, [2, 1, 1, 1, 1, 1])
    assert PauliList(["-X", "Z", "iX", "I", "X", "-iI"]).sort().to_labels() == ["I", "-iI", "X", "-X", "iX", "Z"]
    for qubit_wise in (False, True):
        groups = paulis.group_commuting(qubit_wise=qubit_wise)
        assert sorted(label for group in groups for label in group.to_labels()) == sorted(paulis.to_labels())
        for group in groups:
            for a, b in product(group, repeat=2):
                assert a.commutes(b)
                if qubit_wise:
                    assert all(x == y or x == "I" or y == "I" for x, y in zip(a._body, b._body))


def test_seeded_pauli_generation_including_generator_and_empty():
    assert random_pauli(3, group_phase=True, seed=11).to_label() == "iZZI"
    assert random_pauli_list(3, size=4, seed=11).to_labels() == ["-iYIX", "-YYI", "iXXY", "-iYII"]
    first = random_pauli_list(3, size=4, phase=False, seed=np.random.default_rng(11))
    second = random_pauli_list(3, size=4, phase=False, seed=11)
    assert first == second
    assert random_pauli_list(3, size=0, seed=11).shape == (0, 3)
    with pytest.raises(ValueError, match="non-negative"):
        random_pauli(-1)


def test_zero_qubit_phase_operators_roundtrip_and_tensor():
    for label in ("", "i", "-i", "-"):
        pauli = Pauli(label)
        assert pauli.num_qubits == 0
        assert Pauli(pauli.to_label()) == pauli
        assert PauliList([pauli]).shape == (1, 0)
        np.testing.assert_array_equal(pauli.tensor("X").to_matrix(), pauli.to_matrix()[0, 0] * Pauli("X").to_matrix())
    assert Pauli("-iX").delete(0).to_label() == "-i"


def test_native_paulis_execute_on_statevector_density_matrix_and_instruction():
    state = Statevector.from_circuit(Circuit(2).ry(0.37, 0).rx(0.22, 1).cx(0, 1))
    observable = Pauli("-XY")
    expected = np.vdot(state.data, observable.to_matrix() @ state.data)
    assert state.expectation_value(observable) == pytest.approx(expected)
    density = DensityMatrix.from_statevector(state)
    assert density.expectation_value(observable) == pytest.approx(expected)
    np.testing.assert_allclose(state.evolve(observable).data, observable.to_matrix() @ state.data)
    np.testing.assert_allclose(density.evolve(observable).data, observable.to_matrix() @ density.data @ observable.to_matrix().conj().T)
    circuit = Circuit(2).append(Pauli("-IX").to_instruction(), [0, 1])
    np.testing.assert_allclose(Statevector.from_circuit(circuit).data, [0, -1, 0, 0])
    assert StatevectorDevice().expectation(Circuit(2).h(0).cx(0, 1), Pauli("-XX")) == pytest.approx(-1)
