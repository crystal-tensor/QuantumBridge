# This file is independently implemented for QuantumBridge SDK.
# No source code from Qiskit was copied.

from itertools import product

import numpy as np
import pytest

qi = pytest.importorskip("qiskit.quantum_info")

from quantumbridge.information import random_pauli, random_pauli_list  # noqa: E402
from quantumbridge.operators import Pauli, PauliList  # noqa: E402


def test_two_qubit_pauli_group_products_and_transforms_match_qiskit():
    labels = [phase + "".join(chars) for phase in ("", "-i", "-", "i") for chars in product("IXYZ", repeat=2)]
    native = [Pauli(label) for label in labels]
    upstream = [qi.Pauli(label) for label in labels]
    for a, qa in zip(native, upstream):
        np.testing.assert_array_equal(a.x, qa.x)
        np.testing.assert_array_equal(a.z, qa.z)
        np.testing.assert_array_equal(a.to_matrix(), qa.to_matrix())
        for method in ("adjoint", "transpose", "conjugate", "inverse"):
            assert getattr(a, method)().to_label() == getattr(qa, method)().to_label()
        for b, qb in zip(native, upstream):
            assert a.compose(b).to_label() == qa.compose(qb).to_label()
            assert (a @ b).to_label() == (qa @ qb).to_label()
            assert a.commutes(b) == qa.commutes(qb)


@pytest.mark.parametrize("qargs", [[0, 1], [2, 0], [1, 2]])
def test_subsystem_broadcasting_and_inplace_match_qiskit(qargs):
    a = ["iXYZ", "-ZZX", "-iYYI"]
    b = ["-iYX", "ZX", "iXY"]
    native, upstream = PauliList(a), qi.PauliList(a)
    for method in ("dot", "compose"):
        result = getattr(native, method)(PauliList(b), qargs=qargs)
        expected = getattr(upstream, method)(qi.PauliList(b), qargs=qargs)
        assert result.to_labels() == expected.to_labels()
        assert getattr(native.copy(), method)(PauliList(b), qargs=qargs, inplace=True) == result
    np.testing.assert_array_equal(native.commutes(PauliList(b), qargs=qargs), upstream.commutes(qi.PauliList(b), qargs=qargs))


def test_list_tensor_transforms_sort_unique_and_row_operations_match_qiskit():
    labels = ["-X", "Z", "iX", "I", "X", "-iI", "-X"]
    native, upstream = PauliList(labels), qi.PauliList(labels)
    assert native.tensor(PauliList(["iY", "Z"])).to_labels() == upstream.tensor(qi.PauliList(["iY", "Z"])).to_labels()
    for values in (["iY"], labels):
        assert native.expand(PauliList(values)).to_labels() == upstream.expand(qi.PauliList(values)).to_labels()
    for method in ("adjoint", "transpose", "conjugate", "inverse"):
        assert getattr(native, method)().to_labels() == getattr(upstream, method)().to_labels()
    for weight, phase in product((False, True), repeat=2):
        assert native.sort(weight=weight, phase=phase).to_labels() == upstream.sort(weight=weight, phase=phase).to_labels()
    actual = native.unique(return_index=True, return_counts=True)
    expected = upstream.unique(return_index=True, return_counts=True)
    assert actual[0].to_labels() == expected[0].to_labels()
    np.testing.assert_array_equal(actual[1], expected[1])
    np.testing.assert_array_equal(actual[2], expected[2])
    assert native.delete([0, 2]).to_labels() == upstream.delete([0, 2]).to_labels()
    assert native.insert(1, ["-iY"]).to_labels() == upstream.insert(1, qi.PauliList(["-iY"])).to_labels()
    np.testing.assert_array_equal(native.to_matrix(array=True), upstream.to_matrix(array=True))


def test_list_broadcast_commutation_and_symplectic_roundtrip_match_qiskit():
    labels = ["XI", "YY", "-ZZ", "iIZ", "-iXY"]
    native, upstream = PauliList(labels), qi.PauliList(labels)
    for method in ("compose", "dot"):
        assert getattr(native, method)(["YX"]).to_labels() == getattr(upstream, method)(qi.PauliList(["YX"])).to_labels()
    np.testing.assert_array_equal(native.commutes("YX"), upstream.commutes(qi.Pauli("YX")))
    np.testing.assert_array_equal(native.equiv("-XI"), upstream.equiv(qi.Pauli("-XI")))
    np.testing.assert_array_equal(native.commutes_with_all(["XX", "ZZ"]), upstream.commutes_with_all(qi.PauliList(["XX", "ZZ"])))
    np.testing.assert_array_equal(native.anticommutes_with_all(["XX", "ZZ"]), upstream.anticommutes_with_all(qi.PauliList(["XX", "ZZ"])))
    assert PauliList.from_symplectic(upstream.z, upstream.x, upstream.phase).to_labels() == labels
    native.phase = [0, 1, 2, 3, 0]
    upstream.phase = [0, 1, 2, 3, 0]
    assert native.to_labels() == upstream.to_labels()


@pytest.mark.parametrize("seed", [0, 1, 2, 11, 781])
def test_random_paulis_match_qiskit_exactly(seed):
    for phase in (False, True):
        assert random_pauli(3, group_phase=phase, seed=seed).to_label() == qi.random_pauli(3, group_phase=phase, seed=seed).to_label()
        assert random_pauli_list(3, size=7, phase=phase, seed=seed).to_labels() == qi.random_pauli_list(3, size=7, phase=phase, seed=seed).to_labels()
