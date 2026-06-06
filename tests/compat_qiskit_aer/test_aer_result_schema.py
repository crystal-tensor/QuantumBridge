# This file is independently implemented for QuantumBridge SDK.
# No source code from Qiskit or PennyLane was copied.

from quantumbridge.compat.qiskit_aer.result_adapter import wrap_aer_result
from quantumbridge.schema import AerResult


def test_aer_result_schema():
    result = wrap_aer_result({"counts": {"0": 10}})
    assert isinstance(result, AerResult)
    assert result.capability_level == 2