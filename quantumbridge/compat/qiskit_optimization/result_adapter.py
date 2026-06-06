# This file is independently implemented for QuantumBridge SDK.
# No source code from Qiskit or PennyLane was copied.
"""Qiskit Optimization result schema adapter."""

from quantumbridge.compat.qiskit_optimization.quadratic_program_adapter import ADAPTER
from quantumbridge.schema import OptimizationResult


def wrap_optimization_result(obj, metadata=None) -> OptimizationResult:
    return ADAPTER.make_result(OptimizationResult, obj, metadata=metadata)
