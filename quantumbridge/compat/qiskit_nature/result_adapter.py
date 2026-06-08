# This file is independently implemented for QuantumBridge SDK.
# No source code from Qiskit or PennyLane was copied.
"""Chemistry result schema adapter."""

from quantumbridge.compat.qiskit_nature.nature_adapter import ADAPTER
from quantumbridge.schema import ChemistryResult


def wrap_chemistry_result(obj, metadata=None) -> ChemistryResult:
    return ADAPTER.make_result(ChemistryResult, obj, metadata=metadata)
