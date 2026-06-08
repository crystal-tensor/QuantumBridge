from quantumbridge.chemistry import ExactDiagonalizationSolver, Molecule
from quantumbridge.chemistry.solvers import minimal_h2_qubit_hamiltonian


def test_h2_minimal_workflow_native():
    mol = Molecule(["H", "H"], [(0, 0, 0), (0, 0, 0.735)])
    result = ExactDiagonalizationSolver().solve(minimal_h2_qubit_hamiltonian(), molecule=mol, nuclear_repulsion_energy=0.7151043390810812)
    assert result.total_energy < 0
