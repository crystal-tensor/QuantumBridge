# This file is independently implemented for QuantumBridge SDK.
# No source code from Qiskit or PennyLane was copied.

import numpy as np

from quantumbridge.information import (
    Chi,
    Choi,
    Kraus,
    Operator,
    PTM,
    Stinespring,
    SuperOp,
    average_gate_fidelity,
    gate_error,
    process_fidelity,
)


def _amplitude_damping(gamma=0.2):
    return Kraus(
        [
            np.diag([1, np.sqrt(1 - gamma)]),
            np.array([[0, np.sqrt(gamma)], [0, 0]], dtype=complex),
        ]
    )


def test_amplitude_damping_representations_and_roundtrips():
    gamma = 0.2
    channel = _amplitude_damping(gamma)
    expected_superop = np.array(
        [
            [1, 0, 0, gamma],
            [0, np.sqrt(1 - gamma), 0, 0],
            [0, 0, np.sqrt(1 - gamma), 0],
            [0, 0, 0, 1 - gamma],
        ],
        dtype=complex,
    )
    expected_choi = np.array(
        [
            [1, 0, 0, np.sqrt(1 - gamma)],
            [0, 0, 0, 0],
            [0, 0, gamma, 0],
            [np.sqrt(1 - gamma), 0, 0, 1 - gamma],
        ],
        dtype=complex,
    )
    expected_ptm = np.diag([1, np.sqrt(1 - gamma), np.sqrt(1 - gamma), 1 - gamma])
    expected_ptm[3, 0] = gamma

    np.testing.assert_allclose(SuperOp(channel).data, expected_superop, atol=1e-12)
    np.testing.assert_allclose(Choi(channel).data, expected_choi, atol=1e-12)
    np.testing.assert_allclose(PTM(channel).data, expected_ptm, atol=1e-12)

    for representation in (SuperOp, Choi, PTM, Chi, Stinespring):
        converted = representation(channel)
        np.testing.assert_allclose(SuperOp(converted).data, expected_superop, atol=1e-12)
        assert converted.dim == (2, 2)
        assert converted.num_qubits == 1
        assert converted.is_cp()
        assert converted.is_tp()
        assert converted.is_cptp()


def test_channel_composition_tensor_power_and_adjoint():
    x = SuperOp(Operator.from_label("X"))
    h = SuperOp(
        Operator(
            np.array([[1, 1], [1, -1]], dtype=complex) / np.sqrt(2)
        )
    )

    np.testing.assert_allclose(
        x.compose(h).data,
        SuperOp(Operator(h.to_operator().data @ x.to_operator().data)).data,
        atol=1e-12,
    )
    np.testing.assert_allclose(
        x.dot(h).data,
        SuperOp(Operator(x.to_operator().data @ h.to_operator().data)).data,
        atol=1e-12,
    )
    np.testing.assert_allclose(x.tensor(h).data, SuperOp(x.to_operator().tensor(h.to_operator())).data)
    np.testing.assert_allclose(x.expand(h).data, SuperOp(h.to_operator().tensor(x.to_operator())).data)
    np.testing.assert_allclose(x.power(2).data, np.eye(4), atol=1e-12)
    np.testing.assert_allclose(h.adjoint().data, h.data.conj().T, atol=1e-12)
    assert x.tensorpower(2).num_qubits == 2


def test_channel_subsystem_evolution_and_non_cp_detection():
    state = np.zeros(4, dtype=complex)
    state[2] = 1
    evolved = _amplitude_damping().evolve(state, qargs=[0])
    np.testing.assert_allclose(
        evolved.data,
        np.diag([0.2, 0, 0.8, 0]),
        atol=1e-12,
    )

    transpose_map = SuperOp(
        np.array(
            [
                [1, 0, 0, 0],
                [0, 0, 1, 0],
                [0, 1, 0, 0],
                [0, 0, 0, 1],
            ],
            dtype=complex,
        )
    )
    assert not transpose_map.is_cp()
    assert transpose_map.is_tp()
    assert not transpose_map.is_cptp()


def test_channel_fidelity_metrics_match_closed_form():
    gamma = 0.2
    channel = _amplitude_damping(gamma)
    expected_process = ((1 + np.sqrt(1 - gamma)) ** 2) / 4
    expected_average = (2 * expected_process + 1) / 3

    assert abs(process_fidelity(channel) - expected_process) < 1e-12
    assert abs(average_gate_fidelity(channel) - expected_average) < 1e-12
    assert abs(gate_error(channel) - (1 - expected_average)) < 1e-12
    assert process_fidelity(Operator.from_label("X"), Operator.from_label("X")) == 1.0
