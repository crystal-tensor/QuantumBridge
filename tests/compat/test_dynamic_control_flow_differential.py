# Independent black-box comparisons through optional public SDK APIs.

import numpy as np
import pytest

from quantumbridge import Circuit, Parameter, StatevectorDevice, DensityMatrixDevice, MatrixProductStateDevice
from quantumbridge.core.classical import bit, register
from quantumbridge.qml import QNode
from quantumbridge.utils.math import PauliZ


def qiskit_modules():
    return pytest.importorskip("qiskit"), pytest.importorskip("qiskit_aer")


def density_from_aer(circuit):
    aer = pytest.importorskip("qiskit_aer")
    reference = circuit.copy()
    reference.save_density_matrix()
    result = aer.AerSimulator(method="density_matrix").run(reference, shots=16000, seed_simulator=41).result()
    matrix = np.asarray(result.data(0)["density_matrix"])
    width = circuit.num_qubits
    permutation = [int(format(index, f"0{width}b")[::-1], 2) for index in range(1 << width)]
    return matrix[np.ix_(permutation, permutation)], result


def test_for_loop_parameter_binding_matches_public_qiskit_aer():
    qiskit, _ = qiskit_modules()
    from qiskit.circuit import Parameter as QParameter
    i, theta = QParameter("i"), QParameter("theta")
    body = qiskit.QuantumCircuit(1)
    body.ry(i * .2 + theta, 0)
    reference = qiskit.QuantumCircuit(1)
    reference.for_loop(range(3), i, body, [0], [])
    expected, _ = density_from_aer(reference.assign_parameters({theta: .1}))
    index, angle = Parameter("i"), Parameter("theta")
    native = Circuit(1).for_loop(range(3), index, Circuit(1).ry(index * .2 + angle, 0)).bind({angle: .1})
    for device in (StatevectorDevice(), DensityMatrixDevice(), MatrixProductStateDevice()):
        np.testing.assert_allclose(device.density_matrix(native), expected, atol=1e-10)


def test_while_measurement_feedback_matches_aer_classical_registers():
    qiskit, aer = qiskit_modules()
    reference = qiskit.QuantumCircuit(1, 1)
    reference.x(0)
    reference.measure(0, 0)
    with reference.while_loop((reference.clbits[0], 1)):
        reference.x(0)
        reference.measure(0, 0)
    counts = aer.AerSimulator().run(reference, shots=100, seed_simulator=4).result().get_counts()
    native = Circuit(1, 1).x(0).measure(0, 0).while_loop(bit(0), Circuit(1, 1).x(0).measure(0, 0))
    assert counts == {"0": 100}
    assert MatrixProductStateDevice().run_shots(native, shots=100, seed=4).counts() == counts


def test_switch_default_and_case_match_aer_statistics():
    qiskit, aer = qiskit_modules()
    reference = qiskit.QuantumCircuit(2, 2)
    reference.h(0)
    reference.measure(0, 0)
    with reference.switch(reference.clbits[0]) as case:
        with case(0): reference.x(1)
        with case(case.DEFAULT): reference.h(1)
    reference.measure(1, 1)
    native = Circuit(2, 2).h(0).measure(0, 0).switch(bit(0), {0: Circuit(2, 2).x(1)}, Circuit(2, 2).h(1)).measure(1, 1)
    exact = DensityMatrixDevice().run(native).probabilities()
    counts = aer.AerSimulator().run(reference, shots=12000, seed_simulator=9).result().get_counts()
    for label, probability in exact.items():
        assert counts.get(label[::-1], 0) / 12000 == pytest.approx(probability, abs=.02)


def test_boolean_classical_expression_matches_aer_feedback():
    qiskit, _ = qiskit_modules()
    from qiskit.circuit.classical import expr
    reference = qiskit.QuantumCircuit(3, 2)
    reference.h(0)
    reference.x(1)
    reference.measure(0, 0)
    reference.measure(1, 1)
    condition = expr.bit_xor(reference.clbits[0], reference.clbits[1])
    with reference.if_test(condition): reference.x(2)
    expected, _ = density_from_aer(reference)
    native = Circuit(3, 2).h(0).x(1).measure(0, 0).measure(1, 1).if_else(bit(0) ^ bit(1), Circuit(3, 2).x(2))
    np.testing.assert_allclose(DensityMatrixDevice().density_matrix(native), expected, atol=.015)


def test_pennylane_measure_and_cond_expectations_match_native_qnode():
    qml = pytest.importorskip("pennylane")
    @qml.qnode(qml.device("default.qubit", wires=3))
    def reference(angle):
        qml.RY(angle, wires=0)
        outcome = qml.measure(0)
        qml.cond(outcome, qml.PauliX)(wires=1)
        return qml.expval(qml.PauliZ(0)), qml.expval(qml.PauliZ(1)), qml.probs(wires=[1])
    def program(tape, angle):
        tape.ry(angle, 0)
        outcome = tape.measure(0)
        tape.cond(outcome, lambda branch: branch.x(1))
        return tape.expval(PauliZ(0)), tape.expval(PauliZ(1)), tape.probs([1])
    for angle in (-.4, .7, 1.5):
        expected = reference(angle)
        for device in (StatevectorDevice(), DensityMatrixDevice(), MatrixProductStateDevice()):
            first, second, probabilities = QNode(program, 2, device=device)(angle)
            np.testing.assert_allclose([first, second], expected[:2], atol=1e-10)
            np.testing.assert_allclose([probabilities["0"], probabilities["1"]], expected[2], atol=1e-10)


def test_pennylane_midcircuit_reset_and_conditional_rotation_match():
    qml = pytest.importorskip("pennylane")
    @qml.qnode(qml.device("default.qubit", wires=3))
    def reference():
        qml.Hadamard(0)
        outcome = qml.measure(0, reset=True)
        qml.cond(outcome, qml.RX)(.4, wires=1)
        return qml.expval(qml.PauliZ(0)), qml.expval(qml.PauliZ(1))
    def program(tape):
        tape.h(0)
        outcome = tape.measure(0, reset=True)
        tape.cond(outcome, lambda branch: branch.rx(.4, 1))
        return tape.expval(PauliZ(0)), tape.expval(PauliZ(1))
    np.testing.assert_allclose(QNode(program, 2, device=MatrixProductStateDevice())(), reference(), atol=1e-10)
