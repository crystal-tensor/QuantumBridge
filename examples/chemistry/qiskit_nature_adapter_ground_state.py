"""This is an experimental educational example.
It is not a production-grade chemistry calculation.
Results depend on basis set, ansatz, optimizer, simulator, and optional upstream dependencies.
QuantumBridge is independent and is not an official Qiskit project.
"""

from quantumbridge.chemistry.adapters import QiskitNatureDriverAdapter


try:
    print(QiskitNatureDriverAdapter().run().to_dict())
except ImportError as exc:
    print({"skipped": str(exc)})
