# This file is independently implemented for QuantumBridge SDK.
# No source code from Qiskit or PennyLane was copied.
"""Qiskit Metal design result schema adapter."""

from quantumbridge.compat.qiskit_metal.design_adapter import ADAPTER
from quantumbridge.schema import MetalDesignResult


def wrap_metal_result(obj, metadata=None) -> MetalDesignResult:
    return ADAPTER.make_result(MetalDesignResult, obj, metadata=metadata)
