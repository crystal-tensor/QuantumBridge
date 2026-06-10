# This file is independently implemented for QuantumBridge SDK.
# No source code from Qiskit or PennyLane was copied.

import numpy as np

from quantumbridge.information import Operator, Statevector
from quantumbridge.operators import PauliList, SparsePauliOperator


def test_pauli_list_symplectic_commutation_weight_and_sorting():
    paulis = PauliList(["XI", "YZ", "II"])

    z, x = paulis.to_symplectic()
    np.testing.assert_array_equal(z, [[False, False], [True, True], [False, False]])
    np.testing.assert_array_equal(x, [[True, False], [True, False], [False, False]])
    np.testing.assert_array_equal(paulis.weight(), [1, 2, 0])
    np.testing.assert_array_equal(paulis.commutes(PauliList(["ZI", "IX"])), [[False, True], [False, False], [True, True]])
    assert paulis.sort(weight=True).to_labels() == ["II", "XI", "YZ"]
    assert paulis.delete([1]).to_labels() == ["XI", "II"]
    assert paulis.insert(1, PauliList(["ZZ"])).to_labels() == ["XI", "ZZ", "YZ", "II"]


def test_sparse_pauli_direct_compose_preserves_phase():
    x = SparsePauliOperator.from_list([("X", 1)])
    y = SparsePauliOperator.from_list([("Y", 1)])
    z = SparsePauliOperator.from_list([("Z", 1)])

    assert x.compose(y).simplify().to_list() == [("Z", 1j)]
    assert y.compose(x).simplify().to_list() == [("Z", -1j)]
    assert x.compose(y).commutator(y.compose(x)).simplify().to_list() == []
    assert x.power(2).simplify().to_list() == [("I", 1 + 0j)]
    np.testing.assert_allclose((x @ y).matrix(), Operator.from_label("X").to_matrix() @ Operator.from_label("Y").to_matrix())
    assert z.expectation_value(Statevector.from_label("0")) == 1


def test_sparse_pauli_qargs_compose_tensor_expand_and_operator_conversion():
    base = SparsePauliOperator.from_list([("II", 1)])
    x = SparsePauliOperator.from_list([("X", 1)])
    z = SparsePauliOperator.from_list([("Z", 2)])

    assert base.compose(x, qargs=[1]).to_list() == [("IX", 1 + 0j)]
    assert x.tensor(z).to_list() == [("XZ", 2 + 0j)]
    assert x.expand(z).to_list() == [("ZX", 2 + 0j)]
    np.testing.assert_allclose(x.tensor(z).to_operator().to_matrix(), Operator.from_label("XZ").to_matrix() * 2)
    assert (x + x - x).simplify().to_list() == [("X", 1 + 0j)]
    assert (2 * x / 2).equiv(x)
