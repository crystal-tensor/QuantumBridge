"""This is an experimental educational example.
It is not a production-grade chemistry calculation.
Results depend on basis set, ansatz, optimizer, simulator, and optional upstream dependencies.
QuantumBridge is independent and is not an official Qiskit project.
"""

from quantumbridge.chemistry import Molecule


mol = Molecule(["O", "H", "H"], [(0, 0, 0), (0.758, 0, 0.504), (-0.758, 0, 0.504)])
print({"status": "example-only", "molecule": mol.to_xyz()})
