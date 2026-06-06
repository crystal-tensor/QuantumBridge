# This file is independently implemented for QuantumBridge SDK.
# No source code from Qiskit or PennyLane was copied.
"""Qiskit Finance result schema adapter."""

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

from quantumbridge.compat.qiskit_finance.applications_adapter import ADAPTER
from quantumbridge.schema import FinanceResult


def wrap_finance_result(obj, metadata=None) -> FinanceResult:
    """Wrap a Qiskit Finance result in QuantumBridge FinanceResult schema."""
    return ADAPTER.make_result(FinanceResult, obj, metadata=metadata)