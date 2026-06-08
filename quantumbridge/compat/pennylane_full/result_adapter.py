# This file is independently implemented for QuantumBridge SDK.
# No source code from Qiskit or PennyLane was copied.
"""PennyLane result schema adapter."""

from quantumbridge.compat.pennylane_full.qnode_adapter import ADAPTER
from quantumbridge.schema import PennyLaneResult


def wrap_pennylane_result(obj, metadata=None) -> PennyLaneResult:
    return ADAPTER.make_result(PennyLaneResult, obj, metadata=metadata)
