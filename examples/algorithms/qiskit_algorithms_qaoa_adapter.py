"""This is an experimental educational example.
It is not a production-grade chemistry calculation.
Results depend on basis set, ansatz, optimizer, simulator, and optional upstream dependencies.
QuantumBridge is independent and is not an official Qiskit project.
"""

from quantumbridge.algorithms.adapters import QiskitAlgorithmsAdapter


try:
    print(QiskitAlgorithmsAdapter().qaoa())
except ImportError as exc:
    print({"skipped": str(exc)})
