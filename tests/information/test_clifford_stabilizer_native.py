# This file is independently implemented for QuantumBridge SDK.
# No source code from Qiskit was copied.

from itertools import product

import numpy as np
import pytest

from quantumbridge import Circuit
from quantumbridge.compat.qiskit_core.quantum_info_adapter import native_class
from quantumbridge.core.operations import Instruction
from quantumbridge.information import Clifford, Operator, StabilizerState, random_clifford
from quantumbridge.operators import Pauli, PauliList, SparsePauliOperator


def test_public_symbols_and_tableau_construction():
    assert native_class("StabilizerState") is StabilizerState
    assert native_class("random_clifford") is random_clifford
    h = Clifford.from_label("H")
    assert h.to_labels() == ["+Z", "+X"]
    assert h.dim == (2, 2)
    assert h.input_dims() == h.output_dims() == (2,)
    assert Clifford(h.tableau.tolist()) == h
    assert Clifford(h.tableau.astype(int).tolist(), copy=False) == h
    assert Clifford(h.symplectic_matrix) == h
    assert Clifford(h.to_dict()) == h
    assert Clifford.from_operator(h.to_operator()) == h
    assert Clifford(h.to_instruction()) == h
    assert Clifford(Pauli("-iY")) == Clifford.from_label("Y")
    np.testing.assert_array_equal(np.asarray(h), h.tableau)
    assert h.to_labels(array=True).tolist() == h.to_labels()
    copied = h.copy()
    copied.phase[0] = True
    assert copied != h
    assert copied.destab_phase[0]
    assert not h.destab_phase[0]
    assert copied.is_unitary()
    shared = Clifford(h, copy=False)
    assert np.shares_memory(shared.tableau, h.tableau)
    assert "destabilizer" in repr(h)


def test_explicit_large_gate_and_nonunitary_rejection():
    clifford = random_clifford(3, seed=17)
    matrix_gate = Circuit(3).append("unitary", (0, 1, 2), metadata={"matrix": clifford.to_matrix()})
    assert Clifford(matrix_gate) == clifford
    with pytest.raises(ValueError):
        Clifford(Circuit(1).append("unitary", (0,), metadata={"matrix": np.ones((2, 2))}))
    with pytest.raises(ValueError):
        Clifford(Circuit(1).append("reset", (0,)))


@pytest.mark.parametrize("n", [1, 2, 3, 4])
def test_tableau_synthesis_inverse_and_dense_images(n):
    for seed in range(7):
        clifford = random_clifford(n, seed=seed)
        assert clifford.is_unitary()
        assert Clifford(clifford.to_circuit()) == clifford
        assert clifford.compose(clifford.adjoint()) == Clifford.identity(n)
        assert clifford.adjoint().compose(clifford) == Clifford.identity(n)
        matrix = clifford.to_matrix()
        assert Clifford.from_matrix(matrix) == clifford
        assert Clifford.from_matrix(np.exp(0.31j) * matrix) == clifford
        assert clifford.conjugate() == Clifford.from_matrix(matrix.conj())
        assert clifford.transpose() == Clifford.from_matrix(matrix.T)
        for label in ("I" * n, "i" + "Y" * n, "-" + "X" * n):
            pauli = Pauli(label)
            np.testing.assert_allclose(
                clifford.conjugate_pauli(pauli).to_matrix(),
                matrix @ pauli.to_matrix() @ matrix.conj().T,
                atol=1e-12,
            )


def test_compose_tensor_power_and_subsystems():
    h, s = Clifford.from_label("H"), Clifford.from_label("S")
    assert h.compose(s) == Clifford(Circuit(1).h(0).s(0))
    assert h.dot(s) == h.compose(s, front=True) == Clifford(Circuit(1).s(0).h(0))
    assert (h @ s) == h.dot(s)
    assert h.tensor(s) == Clifford.from_label("HS")
    assert (h ^ s) == h.tensor(s)
    assert h.expand(s) == Clifford.from_label("SH")
    assert h.power(2) == Clifford.identity(1)
    assert s.power(3) == s.adjoint()
    assert s.power(7) == s.power(3)
    base = random_clifford(3, seed=97)
    small = random_clifford(2, seed=41)
    embedded = small._embedded([2, 0], 3)
    assert base.compose(small, qargs=[2, 0]) == base.compose(embedded)
    assert base.dot(small, qargs=[2, 0]) == base.dot(embedded)
    assert Pauli("XYZ").evolve(small, qargs=[2, 0], frame="s") == embedded.conjugate_pauli(Pauli("XYZ"))
    assert PauliList(["iXYZ", "ZYX"]).evolve(base).to_labels() == [Pauli(p).evolve(base).to_label() for p in ["iXYZ", "ZYX"]]
    empty = PauliList.from_symplectic(np.zeros((0, 3), bool), np.zeros((0, 3), bool))
    assert empty.evolve(base).num_qubits == 3
    assert empty.evolve(base).size == 0


@pytest.mark.parametrize("bad", [
    np.zeros((2, 3), dtype=bool),
    [[1, 0, 2], [0, 1, 0]],
    [[1, 0, 0]],
    Circuit(1).t(0),
    Circuit(1).rx(0.1, 0),
    Circuit(1, 1).h(0).measure(0),
    Circuit(1, 1).x(0).c_if(0, 1),
    Instruction("h", 1, metadata={"condition": {"bits": [0], "value": 1}}),
])
def test_reject_invalid_or_nonunitary_cliffords(bad):
    with pytest.raises(ValueError):
        Clifford(bad)


def test_clifford_validation_and_zero_qubit_boundaries():
    for matrix in (np.ones((3, 3)), np.ones((2, 2)), np.array([1, 0]), np.diag([1, np.exp(0.2j)])):
        with pytest.raises(ValueError):
            Clifford.from_matrix(matrix)
    for action in (
        lambda: Clifford.identity(-1),
        lambda: Clifford.identity(1.5),
        lambda: Clifford.from_label("T"),
        lambda: Clifford.from_circuit(object()),
        lambda: Clifford.from_dict({"stabilizer": ["Z"], "destabilizer": []}),
        lambda: Clifford.from_dict({"stabilizer": ["Z"], "destabilizer": ["Z"]}),
        lambda: Clifford.from_label("H").power(0.5),
        lambda: Clifford.from_label("H").power(0),
        lambda: Clifford.from_label("H").power(-1),
        lambda: Clifford.identity(1).compose(Clifford.identity(2)),
        lambda: Clifford.identity(1).to_labels(mode="invalid"),
        lambda: Clifford.identity(2).compose(Clifford.identity(2), qargs=[0, 0]),
        lambda: Pauli("X").evolve(Clifford.identity(1), frame="invalid"),
        lambda: PauliList(["X"]).evolve(Clifford.identity(1), frame="invalid"),
    ):
        with pytest.raises((ValueError, TypeError)):
            action()
    empty = random_clifford(0, seed=0)
    assert empty.num_qubits == 0
    assert empty.to_dict() == {"stabilizer": [], "destabilizer": []}
    np.testing.assert_array_equal(empty.to_matrix(), [[1]])
    np.testing.assert_array_equal(StabilizerState(empty).to_statevector().data, [1])


def test_uniform_random_clifford_group_and_seed_contract():
    elements = {random_clifford(1, seed=seed).tableau.tobytes() for seed in range(200)}
    assert len(elements) == 24
    assert random_clifford(4, seed=72) == random_clifford(4, seed=72)
    assert random_clifford(4, seed=np.random.default_rng(72)) == random_clifford(4, seed=72)
    for invalid in (-1, 1.2):
        with pytest.raises(ValueError):
            random_clifford(invalid)


def test_stabilizer_bell_measurement_sampling_and_reset():
    bell = StabilizerState(Circuit(2).h(0).cx(0, 1))
    assert bell.is_valid()
    assert bell.dim == 4 and bell.dims() == (2, 2)
    assert bell.trace() == bell.purity() == 1
    assert bell.probabilities_dict() == {"00": 0.5, "11": 0.5}
    assert bell.probabilities_dict([1, 0], decimals=3) == bell.probabilities_dict()
    np.testing.assert_allclose(bell.probabilities([0]), [0.5, 0.5])
    for label in ("XX", "ZZ", "-YY"):
        assert bell.expectation_value(Pauli(label)) == 1
    assert bell.expectation_value(Pauli("iZZ")) == 1j
    assert bell.expectation_value(Pauli("X"), qargs=[1]) == 0
    observable = SparsePauliOperator.from_list([("XX", 0.2), ("YY", -0.3)])
    assert np.isclose(bell.expectation_value(observable), 0.5)
    bell.seed(8)
    counts = bell.sample_counts(100)
    bell.seed(8)
    assert counts == bell.sample_counts(100)
    assert set(counts) == {"00", "11"} and sum(counts.values()) == 100
    outcome, collapsed = bell.measure([0])
    assert collapsed.probabilities_dict() == {outcome * 2: 1.0}
    assert bell.probabilities_dict() == {"00": 0.5, "11": 0.5}
    assert bell.reset().probabilities_dict() == {"00": 1.0}
    assert StabilizerState(Circuit(2).x(1)).measure()[0] == "01"
    assert StabilizerState(Circuit(2).x(1)).measure([0, 1])[0] == "01"
    assert StabilizerState(Circuit(2).x(1)).measure([1, 0])[0] == "10"
    assert bell.sample_counts(0) == {}
    assert bell.sample_memory(0).size == 0
    assert "StabilizerState" in repr(bell)
    bell.seed(20)
    copied = bell.copy()
    np.testing.assert_array_equal(bell.sample_memory(10), copied.sample_memory(10))


def test_stabilizer_list_constraints_and_dense_conversion():
    state = StabilizerState.from_stabilizer_list(["-ZZ", "XX"])
    assert state.probabilities_dict() == {"01": 0.5, "10": 0.5}
    assert state.equiv(StabilizerState(Circuit(2).h(0).cx(0, 1).x(1)))
    assert state.equiv(StabilizerState.from_stabilizer_list(["XX", "-YY"])) is False
    assert state.equiv(StabilizerState.from_stabilizer_list(["XX", "YY"]))
    assert state.equiv(Circuit(2).h(0).cx(0, 1).x(0))
    assert not state.equiv(StabilizerState(Circuit(1)))
    partial = StabilizerState.from_stabilizer_list(["-ZZ"], allow_underconstrained=True)
    assert partial.expectation_value(Pauli("-ZZ")) == 1
    redundant = StabilizerState.from_stabilizer_list(["XX", "-ZZ", "YY"], allow_redundant=True)
    assert redundant.equiv(state)
    vector = state.to_statevector().data
    np.testing.assert_allclose(state.to_density_matrix().data, np.outer(vector, vector.conj()), atol=1e-12)
    assert state.to_operator().equiv(state.clifford.to_operator())
    assert state.conjugate().equiv(state)
    assert state.tensor(StabilizerState(Circuit(1).h(0))).equiv(state.expand(StabilizerState(Circuit(1).h(0)))) is False
    for labels, options in (
        ([], {}), (["iX"], {}), (["X", "ZZ"], {}), (["XX", "ZI"], {}),
        (["ZZ"], {}), (["ZZ", "ZZ"], {}), (["ZZ", "-ZZ"], {"allow_redundant": True}),
    ):
        with pytest.raises(ValueError):
            StabilizerState.from_stabilizer_list(labels, **options)
    with pytest.raises(ValueError):
        state.expectation_value(Pauli("X"))
    with pytest.raises(ValueError):
        state.probabilities([0, 0])
    for shots in (-1, 1.5):
        with pytest.raises(ValueError):
            state.sample_counts(shots)


def test_stabilizer_expectations_and_evolution_against_dense_native():
    for seed in range(4):
        state = StabilizerState(random_clifford(3, seed=seed))
        vector = state.to_statevector()
        for symbols in product("IXYZ", repeat=3):
            observable = Pauli("".join(symbols))
            assert np.isclose(state.expectation_value(observable), vector.expectation_value(observable))
        evolved = state.evolve(Clifford.from_label("HS"), qargs=[2, 0])
        assert evolved.equiv(StabilizerState(state.clifford.compose(Clifford.from_label("HS"), qargs=[2, 0])))


def test_large_stabilizer_workflow_never_builds_a_dense_matrix(monkeypatch):
    def reject_dense(*args, **kwargs):
        raise AssertionError("Dense simulation entered a tableau-only workflow")

    monkeypatch.setattr(Clifford, "to_matrix", reject_dense)
    monkeypatch.setattr(Operator, "from_circuit", reject_dense)
    size = 64
    circuit = Circuit(size).h(0)
    for wire in range(1, size):
        circuit.cx(0, wire)
    clifford = Clifford(circuit)
    assert clifford.tableau.nbytes == 2 * size * (2 * size + 1)
    assert Clifford(clifford.to_circuit()) == clifford
    state = StabilizerState(clifford)
    assert state.expectation_value(Pauli("X" * size)) == 1
    assert state.probabilities_dict() == {"0" * size: 0.5, "1" * size: 0.5}
    state.seed(37)
    counts = state.sample_counts(8)
    assert set(counts) <= {"0" * size, "1" * size}
    assert sum(counts.values()) == 8
    assert state.reset().probabilities_dict() == {"0" * size: 1.0}


def test_large_random_clifford_synthesis_without_dense_unitary(monkeypatch):
    monkeypatch.setattr(Clifford, "to_matrix", lambda *args: pytest.fail("Unexpected dense unitary"))
    clifford = random_clifford(16, seed=42)
    assert Clifford(clifford.to_circuit()) == clifford
    assert clifford.compose(clifford.adjoint()) == Clifford.identity(16)


def test_redundant_and_underconstrained_random_generators():
    for width in (3, 5, 8):
        state = StabilizerState(random_clifford(width, seed=width))
        generators = state.clifford.to_labels(mode="S")
        redundant = StabilizerState.from_stabilizer_list(
            list(reversed(generators)) + generators[:2], allow_redundant=True,
        )
        assert redundant.equiv(state)
        completed = StabilizerState.from_stabilizer_list(generators[:2], allow_underconstrained=True)
        assert completed.is_valid()
        assert all(completed.expectation_value(Pauli(label)) == 1 for label in generators[:2])
