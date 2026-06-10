# This file is independently implemented for QuantumBridge SDK.
# No source code from Qiskit or PennyLane was copied.

import numpy as np

from quantumbridge import Circuit, StatevectorDevice
from quantumbridge.circuit_library import (
    amplitude_encoding,
    basis_state,
    efficient_su2,
    integer_comparator,
    qft,
    real_amplitudes,
    standard_gate,
    weighted_adder,
    zz_feature_map,
)
from quantumbridge.information import Operator


def test_standard_gate_factory_and_extended_circuit_gates_are_executable():
    sx = standard_gate("sx")
    np.testing.assert_allclose(Operator.from_circuit(sx.power(2)).to_matrix(), Operator.from_circuit(Circuit(1).x(0)).to_matrix())

    circuit = Circuit(2).x(0).crx(np.pi, 0, 1)
    probabilities = StatevectorDevice().probabilities(circuit)

    assert probabilities["11"] == 1.0


def test_rzz_inverse_and_qft_inverse_are_unitary_identities():
    rzz_identity = Circuit(2).rzz(0.3, 0, 1).compose(Circuit(2).rzz(0.3, 0, 1).inverse())
    np.testing.assert_allclose(Operator.from_circuit(rzz_identity).to_matrix(), np.eye(4), atol=1e-12)

    qft_identity = qft(3).compose(qft(3, inverse=True))
    np.testing.assert_allclose(Operator.from_circuit(qft_identity).to_matrix(), np.eye(8), atol=1e-12)


def test_data_preparation_builders_prepare_actual_states():
    state = StatevectorDevice().statevector(amplitude_encoding([1, 1j, 0, 0]))
    np.testing.assert_allclose(state, np.array([1 / np.sqrt(2), 1j / np.sqrt(2), 0, 0]), atol=1e-12)

    assert StatevectorDevice().probabilities(basis_state("101")) == {
        "000": 0.0,
        "001": 0.0,
        "010": 0.0,
        "011": 0.0,
        "100": 0.0,
        "101": 1.0,
        "110": 0.0,
        "111": 0.0,
    }


def test_template_builders_generate_executable_ansatz_and_feature_maps():
    ansatz = real_amplitudes(3, [[0.1, 0.2, 0.3], [0.4, 0.5, 0.6]], entanglement="circular")
    su2 = efficient_su2(2, [[0.1, 0.2, 0.3, 0.4]], entanglement="full")
    feature_map = zz_feature_map([0.1, 0.2, 0.3])

    assert ansatz.num_qubits == 3
    assert su2.num_qubits == 2
    assert feature_map.metadata["template"]["name"] == "zz_feature_map"
    np.testing.assert_allclose(np.linalg.norm(StatevectorDevice().statevector(ansatz)), 1.0, atol=1e-12)
    np.testing.assert_allclose(np.linalg.norm(StatevectorDevice().statevector(su2)), 1.0, atol=1e-12)
    np.testing.assert_allclose(np.linalg.norm(StatevectorDevice().statevector(feature_map)), 1.0, atol=1e-12)


def test_arithmetic_builders_are_reversible_and_executable():
    adder = weighted_adder(2, [1, 2], num_sum_qubits=2)
    circuit = Circuit(4).x(0).x(1).compose(adder)

    assert StatevectorDevice().probabilities(circuit)["1111"] == 1.0

    comparator = integer_comparator(2, 2)
    marked = Circuit(3).x(0).compose(comparator)
    unmarked = Circuit(3).x(1).compose(comparator)

    assert StatevectorDevice().probabilities(marked)["101"] == 1.0
    assert StatevectorDevice().probabilities(unmarked)["010"] == 1.0
