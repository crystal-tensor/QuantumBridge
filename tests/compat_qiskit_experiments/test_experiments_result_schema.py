# This file is independently implemented for QuantumBridge SDK.
# No source code from Qiskit or PennyLane was copied.

from quantumbridge.compat.qiskit_experiments.result_adapter import wrap_experiments_result
from quantumbridge.schema import RabiExperimentResult
from quantumbridge.schema.experiments_results import ExperimentsResult
from quantumbridge.compat.qiskit_experiments import run_rabi_experiment_native


def test_experiments_result_schema():
    result = wrap_experiments_result({"experiment": "offline"})
    assert isinstance(result, ExperimentsResult)
    assert result.capability_level == 2


def test_native_experiments_result_schema_roundtrip():
    result = run_rabi_experiment_native()
    payload = result.to_dict()
    restored = RabiExperimentResult.from_dict(payload)
    assert restored.validate() is True
    assert restored.to_dict()["workflow"] == "rabi_experiment_native"
    assert restored.to_json()
