# This file is independently implemented for QuantumBridge SDK.
# No source code from Qiskit or PennyLane was copied.

from quantumbridge.compat.qiskit_experiments.result_adapter import wrap_experiments_result
from quantumbridge.schema import ExperimentsResult


def test_experiments_result_schema():
    result = wrap_experiments_result({"experiment": "offline"})
    assert isinstance(result, ExperimentsResult)
    assert result.capability_level == 2