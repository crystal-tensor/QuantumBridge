from quantumbridge.chemistry import QubitHamiltonian
from quantumbridge.utils.math import PauliZ


def test_qubit_hamiltonian_matrix():
    matrix = QubitHamiltonian([(1.0, PauliZ(0))]).matrix()
    assert matrix.shape == (2, 2)
