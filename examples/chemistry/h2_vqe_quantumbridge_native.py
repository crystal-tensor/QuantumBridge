"""This is an experimental educational example.
It is not a production-grade chemistry calculation.
Results depend on basis set, ansatz, optimizer, simulator, and optional upstream dependencies.
QuantumBridge is independent and is not an official Qiskit project.
"""

from quantumbridge.chemistry import ExactDiagonalizationSolver, Molecule
from quantumbridge.chemistry.solvers import minimal_h2_qubit_hamiltonian


mol = Molecule(["H", "H"], [(0, 0, 0), (0, 0, 0.735)])
result = ExactDiagonalizationSolver().solve(minimal_h2_qubit_hamiltonian(), molecule=mol, nuclear_repulsion_energy=0.7151043390810812)
print(result.to_dict())
