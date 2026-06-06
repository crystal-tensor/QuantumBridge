# This file is independently implemented for QuantumBridge SDK.
# No source code from Qiskit or PennyLane was copied.
"""Qiskit Experiments result schema adapter."""

from quantumbridge.compat.qiskit_experiments.experiments_adapter import ADAPTER
from quantumbridge.schema import ExperimentsResult


def wrap_experiments_result(obj, metadata=None) -> ExperimentsResult:
    return ADAPTER.make_result(ExperimentsResult, obj, metadata=metadata)
