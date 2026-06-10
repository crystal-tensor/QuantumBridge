# This file is independently implemented for QuantumBridge SDK.
# No source code from Qiskit or PennyLane was copied.

from math import sqrt

from quantumbridge.compat.pennylane_full.observables_adapter import describe_observable, get_observable, list_observables
from quantumbridge.qml import Hadamard, Hamiltonian, PauliX, PauliZ, QNode, SparseHamiltonian


def test_native_hamiltonian_observable_expectation():
    def program(tape):
        tape.ry(0.3, 0)
        return tape.expval(Hamiltonian([0.5, -0.25], [PauliZ(0), PauliX(0)]))

    expected = 0.5 * 0.955336489125606 - 0.25 * 0.29552020666134
    assert abs(QNode(program, 1)() - expected) < 1e-12


def test_native_hadamard_and_sparse_hamiltonian_expectation():
    def hadamard_program(tape):
        return tape.expval(Hadamard(0))

    def sparse_program(tape):
        tape.x(0)
        return tape.expval(SparseHamiltonian([("Z", 2), ("I", 0.5)]))

    assert abs(QNode(hadamard_program, 1)() - (1 / sqrt(2))) < 1e-12
    assert abs(QNode(sparse_program, 1)() + 1.5) < 1e-12


def test_observables_adapter_returns_native_factories():
    assert {"Hamiltonian", "SparseHamiltonian", "Hadamard"}.issubset(set(list_observables()))
    assert describe_observable("Hamiltonian")["native"] is True
    assert get_observable("PauliZ")(0).terms == ((0, "Z"),)
