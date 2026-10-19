# Independent QuantumBridge tests. Upstream SDKs are optional comparison oracles.

import numpy as np
import pytest

from quantumbridge import Circuit, MatrixProductStateDevice
from quantumbridge.compat.qiskit_adapter import circuit_from_qiskit
from quantumbridge.qml import QNode
from quantumbridge.utils.math import PauliX, PauliZ


@pytest.mark.parametrize("width", [3, 5])
def test_complex_entangled_state_and_probabilities_match_aer_mps(width):
    qiskit = pytest.importorskip("qiskit")
    qi = pytest.importorskip("qiskit.quantum_info")
    aer = pytest.importorskip("qiskit_aer")
    reference = qiskit.QuantumCircuit(width)
    reference.h(0)
    reference.t(width - 1)
    reference.ry(.7, width - 1)
    reference.cx(width - 1, 0)
    reference.unitary(qi.random_unitary(8, seed=width), [width - 1, 1, 0])
    native = circuit_from_qiskit(reference)
    reference.save_statevector()
    oracle = np.asarray(aer.AerSimulator(method="matrix_product_state").run(reference).result().get_statevector())
    permutation = [int(format(index, f"0{width}b")[::-1], 2) for index in range(1 << width)]
    expected = oracle[permutation]
    actual = MatrixProductStateDevice(cutoff=0).statevector(native)
    np.testing.assert_allclose(actual, expected, atol=2e-12)
    assert MatrixProductStateDevice().probabilities(native) == pytest.approx({format(i, f"0{width}b"): abs(value) ** 2 for i, value in enumerate(expected)}, abs=2e-12)


def test_dynamic_nonclifford_trajectories_match_aer_mps_counts():
    qiskit = pytest.importorskip("qiskit")
    aer = pytest.importorskip("qiskit_aer")
    reference = qiskit.QuantumCircuit(2, 2)
    reference.ry(.7, 0)
    reference.cx(0, 1)
    reference.measure(0, 0)
    with reference.if_test((reference.clbits[0], 1)):
        reference.ry(.8, 1)
    reference.reset(0)
    reference.measure(1, 1)
    native = circuit_from_qiskit(reference)
    counts = aer.AerSimulator(method="matrix_product_state").run(reference, shots=6000, seed_simulator=17).result().get_counts()
    exact = MatrixProductStateDevice().run(native).probabilities()
    for label, probability in exact.items():
        assert counts.get(label[::-1], 0) / 6000 == pytest.approx(probability, abs=.025)


def test_mps_qnode_measurements_match_pennylane_default_qubit():
    qml = pytest.importorskip("pennylane")

    def program(tape, theta):
        tape.ry(theta, 0)
        tape.cx(0, 3)
        tape.rz(.3, 3)
        tape.rx(.6, 1)
        return tape.state(), tape.density_matrix([3, 0]), tape.expval(PauliX(1)), tape.var(PauliZ(3))

    @qml.qnode(qml.device("default.qubit", wires=4))
    def reference(theta):
        qml.RY(theta, wires=0)
        qml.CNOT(wires=[0, 3])
        qml.RZ(.3, wires=3)
        qml.RX(.6, wires=1)
        return qml.state(), qml.density_matrix(wires=[3, 0]), qml.expval(qml.PauliX(1)), qml.var(qml.PauliZ(3))

    node = QNode(program, 4, device=MatrixProductStateDevice())
    for theta in (-1.3, 0., .7, 2.2):
        for actual, expected in zip(node(theta), reference(theta)):
            np.testing.assert_allclose(actual, expected, atol=2e-12)
