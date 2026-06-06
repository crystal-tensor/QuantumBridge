# This file is independently implemented for QuantumBridge SDK.
# No source code from Qiskit or PennyLane was copied.
"""Qiskit Finance result schema adapter."""

from quantumbridge.compat.qiskit_finance.applications_adapter import ADAPTER
from quantumbridge.schema import FinanceResult


def wrap_finance_result(obj, metadata=None) -> FinanceResult:
    return ADAPTER.make_result(FinanceResult, obj, metadata=metadata)
