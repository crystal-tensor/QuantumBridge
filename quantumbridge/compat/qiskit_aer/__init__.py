# This file is independently implemented for QuantumBridge SDK.
# No source code from Qiskit or PennyLane was copied.
"""Qiskit Aer optional adapter scaffold.

Design source: docs/compat/strategy/qiskit_aer_compatibility_strategy.md.
"""

from quantumbridge.compat.qiskit_aer.aer_adapter import ADAPTER as aer_adapter
from quantumbridge.compat.qiskit_aer.noise_adapter import ADAPTER as noise_adapter

__all__ = ["aer_adapter", "noise_adapter"]
