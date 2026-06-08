# This file is independently implemented for QuantumBridge SDK.
# No source code from Qiskit or PennyLane was copied.

from quantumbridge.compat.qiskit_dynamics.result_adapter import wrap_dynamics_result
from quantumbridge.schema import DynamicsResult


def test_dynamics_result_schema():
    result = wrap_dynamics_result({"time": [0.0], "state": [1.0]})
    assert isinstance(result, DynamicsResult)
    assert result.capability_level == 2