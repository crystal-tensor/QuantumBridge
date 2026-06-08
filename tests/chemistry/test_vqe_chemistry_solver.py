from quantumbridge.chemistry.ansatz import hardware_efficient_chemistry_ansatz
from quantumbridge.chemistry.solvers import VQEChemistrySolver, minimal_h2_qubit_hamiltonian


def test_vqe_chemistry_solver_smoke():
    solver = VQEChemistrySolver(hardware_efficient_chemistry_ansatz(2), [0.1, 0.2], steps=1)
    result = solver.solve(minimal_h2_qubit_hamiltonian())
    assert result.total_energy is not None
