"""This is an experimental educational example.
It is not a production-grade chemistry calculation.
Results depend on basis set, ansatz, optimizer, simulator, and optional upstream dependencies.
QuantumBridge is independent and is not an official Qiskit project.
"""

from quantumbridge.chemistry import Molecule


mol = Molecule(["H", "H"], [(0, 0, 0), (0, 0, 0.7)])
for item in mol.bond_scan(0, 1, [0.5, 0.7, 0.9]):
    print(item.to_xyz())
