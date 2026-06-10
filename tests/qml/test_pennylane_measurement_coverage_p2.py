import numpy as np

from quantumbridge.qml import PauliZ, QNode


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
