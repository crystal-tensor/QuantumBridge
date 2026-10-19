# Independent QuantumBridge tests. No PennyLane source or tests copied.

import numpy as np
import pytest

from quantumbridge import DensityMatrixDevice
from quantumbridge.qml import QNode
from quantumbridge.utils.math import PauliX, PauliZ


def test_native_mixed_qnode_returns_a_density_matrix_for_state():
    def program(tape, theta):
        tape.ry(theta, 0)
        tape.amplitude_damping(.3, 0)
        return tape.state(), tape.expval(PauliZ(0)), tape.var(PauliZ(0)), tape.probs()

    theta = .7
    state, ev, variance, probs = QNode(program, 1, device=DensityMatrixDevice())(theta)
    expected_z = .3 + .7 * np.cos(theta)
    assert state.shape == (2, 2)
    assert np.trace(state) == pytest.approx(1)
    assert ev == pytest.approx(expected_z)
    assert variance == pytest.approx(1 - expected_z ** 2)
    assert probs["0"] == pytest.approx((1 + expected_z) / 2)
    eps = 1e-6
    function = QNode(lambda tape, angle: (tape.ry(angle, 0), tape.amplitude_damping(.3, 0), tape.expval(PauliZ(0)))[-1], 1, device=DensityMatrixDevice())
    derivative = (function(theta + eps) - function(theta - eps)) / (2 * eps)
    assert derivative == pytest.approx(-.7 * np.sin(theta), abs=1e-8)


def test_native_mixed_qnode_sampling_channels_and_reduced_states():
    def program(tape):
        tape.x(0)
        tape.amplitude_damping(.4, 0)
        tape.bit_flip(.1, 1)
        tape.phase_flip(.2, 0)
        tape.phase_damping(.1, 1)
        tape.depolarizing(.3, 1)
        return tape.density_matrix(wires=[0]), tape.counts(wires=[0], shots=2000, seed=12)

    matrix, counts = QNode(program, 2, device=DensityMatrixDevice())()
    np.testing.assert_allclose(matrix, np.diag([.4, .6]), atol=1e-12)
    assert abs(counts.get("0", 0) / 2000 - .4) < .04


def test_native_mixed_qnode_classical_shadows_use_noisy_state():
    def program(tape):
        tape.h(0)
        tape.amplitude_damping(.4, 0)
        return tape.shadow_expval(PauliX(0), shots=4000, seed=31)

    assert QNode(program, 1, device=DensityMatrixDevice())() == pytest.approx(np.sqrt(.6), abs=.08)


def test_native_mixed_qnode_matches_installed_pennylane_default_mixed():
    qml = pytest.importorskip("pennylane")

    def native_program(tape, theta):
        tape.ry(theta, 0)
        tape.rz(.4, 0)
        tape.cx(0, 1)
        tape.amplitude_damping(.3, 1)
        tape.phase_damping(.2, 0)
        return tape.state(), tape.expval(PauliZ(1)), tape.var(PauliX(0)), tape.density_matrix([1, 0])

    device = qml.device("default.mixed", wires=2)

    @qml.qnode(device)
    def reference(theta):
        qml.RY(theta, wires=0)
        qml.RZ(.4, wires=0)
        qml.CNOT(wires=[0, 1])
        qml.AmplitudeDamping(.3, wires=1)
        qml.PhaseDamping(.2, wires=0)
        return qml.state(), qml.expval(qml.PauliZ(1)), qml.var(qml.PauliX(0)), qml.density_matrix(wires=[1, 0])

    native = QNode(native_program, 2, device=DensityMatrixDevice())
    for theta in (-.8, 0., .3, 1.4):
        actual, expected = native(theta), reference(theta)
        for left, right in zip(actual, expected):
            np.testing.assert_allclose(left, right, atol=1e-12)
