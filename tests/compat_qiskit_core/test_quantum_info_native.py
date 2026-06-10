# This file is independently implemented for QuantumBridge SDK.
# No source code from Qiskit was copied.

import numpy as np

from quantumbridge import Circuit
from quantumbridge.compat.qiskit_core.quantum_info_adapter import get_native_quantum_info_symbols, native_class
from quantumbridge.information import (
    Choi,
    Clifford,
    DensityMatrix,
    Kraus,
    Operator,
    Statevector,
    SuperOp,
    average_gate_fidelity,
    process_fidelity,
    purity,
    random_density_matrix,
    random_statevector,
    random_unitary,
    state_fidelity_general,
    trace_distance,
)
from quantumbridge.operators import PauliList, SparsePauliOp, SparsePauliOperator


def test_native_quantum_info_symbols_are_callable():
    symbols = get_native_quantum_info_symbols()
    assert symbols["Statevector"] is Statevector
    assert symbols["DensityMatrix"] is DensityMatrix
    assert symbols["Operator"] is Operator
    assert symbols["Kraus"] is Kraus
    assert symbols["SuperOp"] is SuperOp
    assert symbols["Choi"] is Choi
    assert symbols["Clifford"] is Clifford
    assert symbols["random_statevector"] is random_statevector
    assert symbols["random_density_matrix"] is random_density_matrix
    assert symbols["random_unitary"] is random_unitary
    assert symbols["trace_distance"] is trace_distance
    assert symbols["average_gate_fidelity"] is average_gate_fidelity
    assert symbols["SparsePauliOp"] is SparsePauliOperator
    assert native_class("PauliList") is PauliList


def test_statevector_density_matrix_operator_core_methods():
    plus = Statevector.from_label("0").evolve(Operator.from_label("X")).evolve(Circuit(1).h(0))
    assert plus.num_qubits == 1
    assert plus.is_valid()
    assert set(plus.probabilities()) == {"0", "1"}
    assert abs(plus.expectation_value(Operator.from_label("Z"))) < 1e-12

    rho = DensityMatrix.from_statevector(plus)
    assert rho.is_valid()
    assert abs(rho.purity() - 1.0) < 1e-12
    assert abs(rho.evolve(Operator.from_label("X")).expectation_value(Operator.from_label("X")) + 1.0) < 1e-12

    h = Operator.from_circuit(Circuit(1).h(0))
    assert h.is_unitary()
    np.testing.assert_allclose(h.power(2).to_matrix(), np.eye(2), atol=1e-12)
    np.testing.assert_allclose(h.adjoint().compose(h).to_matrix(), np.eye(2), atol=1e-12)


def test_pauli_list_sparse_pauli_op_core_methods():
    paulis = PauliList(["XI", "ZZ"])
    assert paulis.size == 2
    assert paulis.num_qubits == 2
    assert paulis.to_labels() == ["XI", "ZZ"]
    assert len(paulis.to_matrix()) == 2
    assert paulis.compose(PauliList(["XI"])).to_labels() == ["II", "YZ"]

    op = SparsePauliOp.from_list([("Z", 1), ("Z", -1), ("X", 0.5)]).simplify()
    assert op.to_list() == [("X", 0.5 + 0j)]
    np.testing.assert_allclose(op.matrix(), np.array([[0, 0.5], [0.5, 0]], dtype=complex))

    dense = SparsePauliOperator.from_operator(Operator.from_label("Z"))
    assert dense.simplify().to_list() == [("Z", 1 + 0j)]


def test_random_states_metrics_channels_and_clifford_are_callable():
    state = random_statevector(2, seed=11)
    assert state.is_valid()
    np.testing.assert_allclose(state.data, random_statevector(2, seed=11).data)

    rho = random_density_matrix(2, seed=12, rank=1)
    assert rho.is_valid()
    assert abs(purity(rho) - 1.0) < 1e-10

    unitary = random_unitary(2, seed=13)
    assert unitary.is_unitary()
    assert abs(process_fidelity(unitary, unitary) - 1.0) < 1e-10
    assert abs(average_gate_fidelity(unitary, unitary) - 1.0) < 1e-10
    assert abs(state_fidelity_general(state, state) - 1.0) < 1e-10
    assert trace_distance(Statevector.from_label("0").to_operator(), Statevector.from_label("1").to_operator()) == 1.0

    identity_channel = Kraus([np.eye(2)])
    assert identity_channel.is_cptp()
    evolved = identity_channel.evolve(Statevector.from_label("0").data)
    np.testing.assert_allclose(evolved.data, Statevector.from_label("0").to_operator().data)

    superop = SuperOp.from_operator(Operator.from_label("X"))
    flipped = superop.evolve(Statevector.from_label("0").data)
    assert flipped.probabilities() == {"0": 0.0, "1": 1.0}

    choi = Choi.from_channel(identity_channel)
    assert choi.data.shape == (4, 4)

    h = Clifford.from_circuit(Circuit(1).h(0))
    assert h.to_operator().is_unitary()
    assert h.compose(h).equiv(Operator(np.eye(2)))

    with np.testing.assert_raises(ValueError):
        Clifford.from_circuit(Circuit(1).rx(0.125, 0))
