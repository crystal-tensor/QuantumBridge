# This file is independently implemented for QuantumBridge SDK.
# No source code from Qiskit or PennyLane was copied.
"""Qiskit Addons optional adapter scaffold.

Design source: docs/compat/strategy/qiskit_ecosystem_coverage_strategy.md.
"""

from quantumbridge.compat.qiskit_addons.aqc_adapter import ADAPTER as aqc_adapter
from quantumbridge.compat.qiskit_addons.mpf_adapter import ADAPTER as mpf_adapter
from quantumbridge.compat.qiskit_addons.obp_adapter import ADAPTER as obp_adapter
from quantumbridge.compat.qiskit_addons.sqd_adapter import ADAPTER as sqd_adapter

__all__ = ["aqc_adapter", "mpf_adapter", "obp_adapter", "sqd_adapter"]
