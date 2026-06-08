# This file is independently implemented for QuantumBridge SDK.
# No source code from Qiskit or PennyLane was copied.
"""Qiskit IBM Runtime optional adapter scaffold.

Design source: docs/compat/strategy/qiskit_ecosystem_coverage_strategy.md.
"""

from quantumbridge.compat.qiskit_runtime.backend_adapter import ADAPTER as backend_adapter
from quantumbridge.compat.qiskit_runtime.job_adapter import ADAPTER as job_adapter
from quantumbridge.compat.qiskit_runtime.runtime_adapter import ADAPTER as runtime_adapter

__all__ = ["backend_adapter", "job_adapter", "runtime_adapter"]
