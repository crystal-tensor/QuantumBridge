# This file is independently implemented for QuantumBridge SDK.
# No source code from Qiskit or PennyLane was copied.

from quantumbridge.compat.pennylane_full.result_adapter import wrap_pennylane_result
from quantumbridge.schema import PennyLaneResult


def test_pennylane_result_schema():
    result = wrap_pennylane_result({"probabilities": [1.0, 0.0]})
    assert isinstance(result, PennyLaneResult)
    assert result.capability_level == 2