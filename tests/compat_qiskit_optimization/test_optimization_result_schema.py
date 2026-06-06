# This file is independently implemented for QuantumBridge SDK.
# No source code from Qiskit or PennyLane was copied.

from quantumbridge.compat.qiskit_optimization.result_adapter import wrap_optimization_result
from quantumbridge.schema import OptimizationResult


def test_optimization_result_schema():
    result = wrap_optimization_result({"objective": 1.0})
    assert isinstance(result, OptimizationResult)
    assert result.capability_level == 2