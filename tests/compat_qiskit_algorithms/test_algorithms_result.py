# This file is independently implemented for QuantumBridge SDK.
# No source code from Qiskit or PennyLane was copied.

from quantumbridge.compat.qiskit_algorithms.result_adapter import wrap_algorithms_result
from quantumbridge.schema import AlgorithmsResult


def test_algorithms_result_schema():
    result = wrap_algorithms_result({"algorithm": "VQE", "value": -1.0})
    assert isinstance(result, AlgorithmsResult)
    assert result.capability_level == 2