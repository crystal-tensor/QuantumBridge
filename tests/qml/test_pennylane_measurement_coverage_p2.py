from quantumbridge.qml import QNode


def test_qnode_probs_and_state_measurements():
    def probs_program(tape):
        tape.h(0)
        return tape.probs()

    def state_program(tape):
        tape.x(0)
        return tape.state()

    assert set(QNode(probs_program, 1)()) == {"0", "1"}
    assert abs(QNode(state_program, 1)()[1] - 1) < 1e-12
