# This file is independently implemented for QuantumBridge SDK.
# No source code from Qiskit or PennyLane was copied.
"""Qiskit Dynamics result schema adapter."""

from quantumbridge.compat.qiskit_dynamics.solver_adapter import ADAPTER
from quantumbridge.schema import DynamicsResult


def wrap_dynamics_result(obj, metadata=None) -> DynamicsResult:
    return ADAPTER.make_result(DynamicsResult, obj, metadata=metadata)
