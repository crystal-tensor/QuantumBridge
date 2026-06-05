# This file is independently implemented for QuantumBridge SDK.
# No source code from Qiskit or PennyLane was copied.
"""Qiskit core optional adapter scaffold.

Design source: docs/compat/strategy/qiskit_ecosystem_coverage_strategy.md.
"""

from quantumbridge.compat.qiskit_core.circuit_adapter import ADAPTER as circuit_adapter
from quantumbridge.compat.qiskit_core.primitives_adapter import ADAPTER as primitives_adapter
from quantumbridge.compat.qiskit_core.quantum_info_adapter import ADAPTER as quantum_info_adapter
from quantumbridge.compat.qiskit_core.result_adapter import ADAPTER as result_adapter
from quantumbridge.compat.qiskit_core.transpiler_adapter import ADAPTER as transpiler_adapter

__all__ = [
    "circuit_adapter",
    "primitives_adapter",
    "quantum_info_adapter",
    "result_adapter",
    "transpiler_adapter",
]
