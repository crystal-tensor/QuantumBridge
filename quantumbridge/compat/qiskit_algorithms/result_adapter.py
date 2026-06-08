# This file is independently implemented for QuantumBridge SDK.
# No source code from Qiskit or PennyLane was copied.
"""Qiskit Algorithms result schema adapter."""

from quantumbridge.compat.qiskit_algorithms.grover_adapter import ADAPTER
from quantumbridge.schema import AlgorithmsResult


def wrap_algorithms_result(obj, metadata=None) -> AlgorithmsResult:
    return ADAPTER.make_result(AlgorithmsResult, obj, metadata=metadata)
