# This file is independently implemented for QuantumBridge SDK.
# No source code from Qiskit or PennyLane was copied.
"""Qiskit Algorithms eigensolver passthrough scaffold."""

from quantumbridge.ecosystem.registry import EcosystemAdapter

ADAPTER = EcosystemAdapter(
    "qiskit-algorithms",
    "qiskit-algorithms",
    ("qiskit_algorithms.eigensolvers",),
    "qiskit-algorithms",
    "qiskit_algorithms_eigensolvers",
)
