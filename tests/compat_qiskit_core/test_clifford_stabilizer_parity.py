# This file is independently implemented for QuantumBridge SDK.
# No source code from Qiskit was copied. Installed Qiskit is a test oracle only.

import numpy as np
import pytest

qi = pytest.importorskip("qiskit.quantum_info")
from qiskit import QuantumCircuit  # noqa: E402

from quantumbridge import Circuit  # noqa: E402
from quantumbridge.information import Clifford, StabilizerState, random_clifford  # noqa: E402
from quantumbridge.operators import Pauli, PauliList, SparsePauliOperator  # noqa: E402


@pytest.mark.parametrize("name", ["id", "h", "s", "sdg", "sx", "sxdg", "x", "y", "z"])
def test_standard_one_qubit_clifford_gates_match_qiskit(name):
    native = getattr(Circuit(1), name)(0)
    upstream = QuantumCircuit(1)
    getattr(upstream, name)(0)
    assert Clifford(native).to_labels() == qi.Clifford(upstream).to_labels()


@pytest.mark.parametrize("name", ["cx", "cy", "cz", "swap", "dcx", "ecr", "iswap"])
def test_standard_two_qubit_clifford_gates_match_qiskit(name):
    native = getattr(Circuit(2), name)(0, 1)
    upstream = QuantumCircuit(2)
    getattr(upstream, name)(1, 0)
    assert Clifford(native).to_labels() == qi.Clifford(upstream).to_labels()


@pytest.mark.parametrize("n", [1, 2, 3, 4])
def test_random_tableau_algebra_and_synthesis_match_qiskit(n):
    for seed in range(10):
        native = random_clifford(n, seed=seed)
        upstream = qi.Clifford(native.tableau)
        assert native.to_labels() == upstream.to_labels()
        assert native.to_dict() == upstream.to_dict()
        assert Clifford.from_dict(upstream.to_dict()) == native
        assert Clifford.from_matrix(upstream.to_matrix()) == native
        assert qi.Operator(native.to_matrix()).equiv(upstream.to_operator())
        assert Clifford(native.to_circuit()) == native
        for method in ("adjoint", "conjugate", "transpose"):
            assert getattr(native, method)().to_labels() == getattr(upstream, method)().to_labels()
        other = random_clifford(n, seed=seed + 500)
        qother = qi.Clifford(other.tableau)
        for front in (True, False):
            assert native.compose(other, front=front).to_labels() == upstream.compose(qother, front=front).to_labels()
        for exponent in (1, 2, 3, 5):
            assert native.power(exponent).to_labels() == upstream.power(exponent).to_labels()
        assert native.tensor(other).to_labels() == upstream.tensor(qother).to_labels()
        assert native.expand(other).to_labels() == upstream.expand(qother).to_labels()


@pytest.mark.parametrize("qargs", [[0, 1], [2, 0], [1, 2]])
def test_clifford_and_pauli_subsystem_order_match_qiskit(qargs):
    native = random_clifford(3, seed=17)
    small = random_clifford(2, seed=111)
    upstream, qsmall = qi.Clifford(native.tableau), qi.Clifford(small.tableau)
    for front in (False, True):
        assert native.compose(small, qargs=qargs, front=front).to_labels() == upstream.compose(qsmall, qargs=qargs, front=front).to_labels()
    labels = ["iXYZ", "-iYZX", "-ZZI", "III"]
    for frame in ("h", "s"):
        expected = qi.PauliList(labels).evolve(qsmall, qargs=qargs, frame=frame)
        assert PauliList(labels).evolve(small, qargs=qargs, frame=frame).to_labels() == expected.to_labels()
        for label in labels:
            assert Pauli(label).evolve(small, qargs=qargs, frame=frame).to_label() == qi.Pauli(label).evolve(qsmall, qargs=qargs, frame=frame).to_label()


def test_native_circuit_wire_conversion_matches_qiskit_generators():
    native = Circuit(3).h(0).s(1).sx(2).cx(2, 0).cz(0, 1).sdg(2).swap(1, 2).y(0)
    upstream = QuantumCircuit(3)
    upstream.h(2)
    upstream.s(1)
    upstream.sx(0)
    upstream.cx(0, 2)
    upstream.cz(2, 1)
    upstream.sdg(0)
    upstream.swap(1, 0)
    upstream.y(2)
    assert Clifford(native).to_labels() == qi.Clifford(upstream).to_labels()
    assert qi.Operator(Clifford(native).to_matrix()).equiv(qi.Operator(upstream))


@pytest.mark.parametrize("n", [1, 2, 3, 4])
def test_stabilizer_probabilities_expectations_and_projective_measurement(n):
    for seed in range(10):
        native = StabilizerState(random_clifford(n, seed=seed))
        upstream = qi.StabilizerState(qi.Clifford(native.clifford.tableau))
        for qargs in (None, [0], list(reversed(range(n)))):
            np.testing.assert_allclose(native.probabilities(qargs), upstream.probabilities(qargs), atol=1e-12)
            assert native.probabilities_dict(qargs) == upstream.probabilities_dict(qargs)
        for label in ("X" * n, "Y" * n, "Z" * n, "i" + "X" * n):
            assert np.isclose(native.expectation_value(Pauli(label)), upstream.expectation_value(qi.Pauli(label)))
        terms = [("X" * n, 0.5), ("Z" * n, -0.2)]
        assert np.isclose(native.expectation_value(SparsePauliOperator.from_list(terms)), upstream.expectation_value(qi.SparsePauliOp.from_list(terms)))
        assert qi.state_fidelity(native.to_statevector().data, upstream.clifford.to_matrix()[:, 0]) == pytest.approx(1)
        assert qi.Operator(native.to_operator().data).equiv(upstream.to_operator())
        assert native.conjugate().equiv(StabilizerState(Clifford(upstream.conjugate().clifford.tableau)))
        native.seed(seed)
        outcome, collapsed = native.measure()
        assert upstream.probabilities_dict()[outcome] > 0
        assert collapsed.probabilities_dict() == {outcome: 1.0}
        assert collapsed.is_valid()
        assert native.reset().probabilities_dict() == {"0" * n: 1.0}
        assert StabilizerState.from_stabilizer_list(upstream.clifford.to_labels(mode="S")).equiv(native)


def test_stabilizer_tensor_evolve_and_partial_reset_match_qiskit():
    native = StabilizerState(random_clifford(3, seed=75))
    upstream = qi.StabilizerState(qi.Clifford(native.clifford.tableau))
    small = random_clifford(2, seed=53)
    qsmall = qi.Clifford(small.tableau)
    for qargs in ([2, 0], [0, 1]):
        result = native.evolve(small, qargs=qargs)
        reference = upstream.evolve(qsmall, qargs=qargs)
        assert result.equiv(StabilizerState(Clifford(reference.clifford.tableau)))
    other = StabilizerState(small)
    qother = qi.StabilizerState(qsmall)
    assert native.tensor(other).probabilities_dict() == upstream.tensor(qother).probabilities_dict()
    assert native.expand(other).probabilities_dict() == upstream.expand(qother).probabilities_dict()
    assert native.reset([1]).probabilities_dict([1]) == {"0": 1.0}


@pytest.mark.parametrize("labels", [["ZZ", "XX"], ["-ZZ", "YY"], ["IIZ", "IZI", "ZII"], ["XY", "YZ"]])
def test_stabilizer_list_completion_matches_qiskit_state(labels):
    native = StabilizerState.from_stabilizer_list(labels)
    upstream = qi.StabilizerState.from_stabilizer_list(labels)
    vector = upstream.clifford.to_matrix()[:, 0]
    np.testing.assert_allclose(native.to_density_matrix().data, np.outer(vector, vector.conj()), atol=1e-12)
