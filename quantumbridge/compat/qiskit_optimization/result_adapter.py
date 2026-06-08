# This file is independently implemented for QuantumBridge SDK.
# No source code from Qiskit or PennyLane was copied.
"""Qiskit Optimization result schema adapter."""

import warnings

warnings.warn(
    "This adapter is a SCAFFOLD adapter. "
    "Full implementation is not yet available. "
    "This adapter only provides the Result schema wrapper. "
    "Level 0: inventory only; Level 1: passthrough; Level 2: schema wrapper. "
    "No native implementation or production parity is claimed.",
    UserWarning,
    stacklevel=2
)

from quantumbridge.compat.qiskit_optimization.applications_adapter import ADAPTER
from quantumbridge.schema import OptimizationResult


def wrap_optimization_result(obj, metadata=None) -> OptimizationResult:
    """Wrap a Qiskit Optimization result in QuantumBridge OptimizationResult schema."""
    return ADAPTER.make_result(OptimizationResult, obj, metadata=metadata)