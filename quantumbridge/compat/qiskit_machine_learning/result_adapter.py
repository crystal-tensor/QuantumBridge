# This file is independently implemented for QuantumBridge SDK.
# No source code from Qiskit or PennyLane was copied.
"""Qiskit Machine Learning result schema adapter."""

from quantumbridge.compat.qiskit_machine_learning.qnn_adapter import ADAPTER
from quantumbridge.schema import MLResult


def wrap_ml_result(obj, metadata=None) -> MLResult:
    return ADAPTER.make_result(MLResult, obj, metadata=metadata)
