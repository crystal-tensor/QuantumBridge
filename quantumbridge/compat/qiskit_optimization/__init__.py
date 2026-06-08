# This file is independently implemented for QuantumBridge SDK.
# No source code from Qiskit or PennyLane was copied.
"""Qiskit Optimization optional adapter scaffold.

Design source: docs/compat/strategy/qiskit_optimization_compatibility_strategy.md.
"""

from quantumbridge.compat.qiskit_optimization.converter_adapter import ADAPTER as converter_adapter
from quantumbridge.compat.qiskit_optimization.optimizer_adapter import ADAPTER as optimizer_adapter
from quantumbridge.compat.qiskit_optimization.quadratic_program_adapter import ADAPTER as quadratic_program_adapter

__all__ = ["converter_adapter", "optimizer_adapter", "quadratic_program_adapter"]
