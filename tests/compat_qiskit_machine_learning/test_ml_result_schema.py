# This file is independently implemented for QuantumBridge SDK.
# No source code from Qiskit or PennyLane was copied.

from quantumbridge.compat.qiskit_machine_learning.result_adapter import wrap_ml_result
from quantumbridge.schema import MLResult


def test_ml_result_schema():
    result = wrap_ml_result({"prediction": [0, 1]})
    assert isinstance(result, MLResult)
    assert result.capability_level == 2