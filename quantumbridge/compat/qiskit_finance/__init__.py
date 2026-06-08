# This file is independently implemented for QuantumBridge SDK.
# No source code from Qiskit or PennyLane was copied.
"""Qiskit Finance optional adapter scaffold.

Design source: docs/compat/strategy/qiskit_finance_compatibility_strategy.md.
"""

from quantumbridge.compat.qiskit_finance.applications_adapter import ADAPTER as applications_adapter
from quantumbridge.compat.qiskit_finance.circuits_adapter import ADAPTER as circuits_adapter
from quantumbridge.compat.qiskit_finance.data_provider_adapter import ADAPTER as data_provider_adapter
from quantumbridge.compat.qiskit_finance.uncertainty_adapter import ADAPTER as uncertainty_adapter

__all__ = ["applications_adapter", "circuits_adapter", "data_provider_adapter", "uncertainty_adapter"]
