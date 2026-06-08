from quantumbridge.chemistry import ExactDiagonalizationSolver, QubitHamiltonian
from quantumbridge.utils.math import PauliZ


def test_exact_diagonalization_solver():
    result = ExactDiagonalizationSolver().solve(QubitHamiltonian([(1.0, PauliZ(0))]))
    assert result.electronic_energy == -1.0
