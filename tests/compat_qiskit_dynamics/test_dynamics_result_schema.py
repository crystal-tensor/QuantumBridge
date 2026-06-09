# This file is independently implemented for QuantumBridge SDK.
# No source code from Qiskit or PennyLane was copied.

from quantumbridge.compat.qiskit_dynamics.result_adapter import wrap_dynamics_result
from quantumbridge.schema import SingleQubitDynamicsResult
from quantumbridge.schema.dynamics_results import DynamicsResult
from quantumbridge.compat.qiskit_dynamics import run_z_precession_native


def test_dynamics_result_schema():
    result = wrap_dynamics_result({"time": [0.0], "state": [1.0]})
    assert isinstance(result, DynamicsResult)
    assert result.capability_level == 2


def test_native_dynamics_result_schema_roundtrip():
    result = run_z_precession_native()
    payload = result.to_dict()
    restored = SingleQubitDynamicsResult.from_dict(payload)
    assert restored.validate() is True
    assert restored.to_dict()["workflow"] == "z_precession_native"
    assert restored.to_json()
