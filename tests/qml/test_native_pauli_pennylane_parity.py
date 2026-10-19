# This file is independently implemented for QuantumBridge SDK.
# No source code from PennyLane was copied.

import numpy as np
import pytest

pennylane = pytest.importorskip("pennylane")

from quantumbridge.operators import Pauli  # noqa: E402
from quantumbridge.qml import QNode  # noqa: E402


@pytest.mark.parametrize("label", ["XY", "-YZ", "ZZ"])
def test_same_native_observable_executes_in_qnode_and_pennylane(label):
    observable = Pauli(label)

    def native_circuit(tape, theta):
        tape.ry(theta, 0)
        tape.rx(0.22, 1)
        tape.cx(0, 1)
        return tape.expval(observable)

    native = QNode(native_circuit, num_qubits=2)

    @pennylane.qnode(pennylane.device("default.qubit", wires=2))
    def upstream(theta):
        pennylane.RY(theta, wires=0)
        pennylane.RX(0.22, wires=1)
        pennylane.CNOT(wires=[0, 1])
        return pennylane.expval(pennylane.Hermitian(observable.to_matrix(), wires=[0, 1]))

    for theta in (0.0, 0.37, 1.1):
        np.testing.assert_allclose(native(theta), upstream(theta), atol=1e-12)
