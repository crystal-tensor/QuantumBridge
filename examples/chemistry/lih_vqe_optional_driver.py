"""This is an experimental educational example.
It is not a production-grade chemistry calculation.
Results depend on basis set, ansatz, optimizer, simulator, and optional upstream dependencies.
QuantumBridge is independent and is not an official Qiskit project.
"""

from quantumbridge.chemistry import Molecule


mol = Molecule(["Li", "H"], [(0, 0, 0), (0, 0, 1.6)])
print({"status": "example-only", "molecule": mol.to_xyz()})
