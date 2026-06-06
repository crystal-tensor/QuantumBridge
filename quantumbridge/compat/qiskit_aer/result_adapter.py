# This file is independently implemented for QuantumBridge SDK.
# No source code from Qiskit or PennyLane was copied.
"""Qiskit Aer result schema adapter."""

from quantumbridge.compat.qiskit_aer.aer_adapter import ADAPTER
from quantumbridge.schema import AerResult


def wrap_aer_result(obj, metadata=None) -> AerResult:
    return ADAPTER.make_result(AerResult, obj, metadata=metadata)
