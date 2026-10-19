import numpy as np
import pytest

from quantumbridge.qml import ClassicalShadowResult, Hamiltonian, PauliX, PauliZ, QNode


def test_qnode_probs_and_state_measurements():
    def probs_program(tape):
        tape.h(0)
        return tape.probs()

    def state_program(tape):
        tape.x(0)
        return tape.state()

    assert set(QNode(probs_program, 1)()) == {"0", "1"}
    assert abs(QNode(state_program, 1)()[1] - 1) < 1e-12


def test_qnode_sample_counts_variance_and_density_matrix_measurements():
    def variance_program(tape):
        tape.ry(0.4, 0)
        return tape.var(PauliZ(0))

    def sample_program(tape):
        tape.x(0)
        return tape.sample(wires=[0], shots=3, seed=7)

    def counts_program(tape):
        tape.x(0)
        return tape.counts(wires=[0], shots=4, seed=9)

    def density_matrix_program(tape):
        tape.x(0)
        return tape.density_matrix()

    assert abs(QNode(variance_program, 1)() - np.sin(0.4) ** 2) < 1e-12
    assert QNode(sample_program, 1)() == ["1", "1", "1"]
    assert QNode(counts_program, 1)() == {"1": 4}
    np.testing.assert_allclose(QNode(density_matrix_program, 1)(), [[0, 0], [0, 1]])


def test_qnode_multiple_measurements_preserve_return_order():
    def program(tape):
        tape.h(0)
        return tape.expval(PauliZ(0)), tape.var(PauliZ(0)), tape.probs(wires=[0])

    expval, variance, probs = QNode(program, 1)()

    assert abs(expval) < 1e-12
    assert abs(variance - 1.0) < 1e-12
    assert set(probs) == {"0", "1"}
    assert abs(probs["0"] - 0.5) < 1e-12
    assert abs(probs["1"] - 0.5) < 1e-12


def test_qnode_density_matrix_accepts_subset_wires():
    def program(tape):
        tape.h(0)
        tape.cx(0, 1)
        return tape.density_matrix(wires=[0])

    np.testing.assert_allclose(QNode(program, 2)(), [[0.5, 0.0], [0.0, 0.5]], atol=1e-12)


def test_qnode_classical_shadow_and_shadow_expval_are_callable():
    def shadow_program(tape):
        tape.h(0)
        return tape.classical_shadow(wires=[0], shots=5, seed=11)

    def shadow_expval_program(tape):
        tape.ry(0.4, 0)
        return tape.shadow_expval(PauliZ(0), shots=4000, seed=13, k=5)

    shadow = QNode(shadow_program, 1)()

    assert isinstance(shadow, ClassicalShadowResult)
    assert shadow.bits.shape == (5, 1)
    assert shadow.recipes.shape == (5, 1)
    assert shadow.wires == (0,)
    assert set(shadow.recipes.ravel()).issubset({0, 1, 2})
    assert abs(QNode(shadow_expval_program, 1)() - np.cos(0.4)) < 0.08


def test_shadow_expval_supports_hamiltonians_and_observable_batches():
    observable = Hamiltonian([0.5, -0.25], [PauliZ(0), PauliX(0)])

    def program(tape):
        tape.ry(0.3, 0)
        return tape.shadow_expval([observable, PauliZ(0)], shots=6000, seed=91)

    values = QNode(program, 1)()
    expected = np.asarray([0.5 * np.cos(0.3) - 0.25 * np.sin(0.3), np.cos(0.3)])
    np.testing.assert_allclose(values, expected, atol=0.08)


@pytest.mark.parametrize(
    ("measurement", "message"),
    [
        (lambda tape: tape.sample(wires=[0]), "positive integer number of shots"),
        (lambda tape: tape.probs(wires=[1]), "must be in"),
        (lambda tape: tape.density_matrix(wires=[0, 0]), "must be unique"),
    ],
)
def test_measurements_validate_shots_and_wires(measurement, message):
    with pytest.raises(ValueError, match=message):
        QNode(lambda tape: measurement(tape), 1)()
