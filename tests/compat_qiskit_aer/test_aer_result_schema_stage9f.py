# This file is independently implemented for QuantumBridge SDK.
# No source code from Qiskit Aer was copied.

import pytest

from quantumbridge.compat.qiskit_aer import wrap_aer_result
from quantumbridge.schema import AerResult
from quantumbridge.schema.aer_results import StatevectorSimulationResult


def test_aer_result_schema_round_trips_complex_statevector():
    result = StatevectorSimulationResult(
        workflow="statevector_simulator_native",
        backend="statevector",
        mode="native_minimal",
        capability_level=3,
        production_ready=False,
        native_implementation=True,
        num_qubits=1,
        final_statevector=[1 + 0j, 0 + 0j],
        probabilities={"0": 1.0},
        warnings=["demo"],
        provenance={"cloud_access": False},
    )

    payload = result.to_dict()
    restored = StatevectorSimulationResult.from_dict(payload)

    assert restored.final_statevector == [1 + 0j, 0 + 0j]
    assert restored.to_json()


def test_wrap_aer_result_uses_stage9f_schema():
    result = wrap_aer_result({"counts": {"0": 10}}, metadata={"shots": 10})
    assert isinstance(result, AerResult)
    assert result.capability_level == 2
    assert result.counts == {"0": 10}
    assert result.production_ready is False


def test_aer_result_rejects_production_ready_claim():
    with pytest.raises(ValueError):
        AerResult(
            workflow="bad",
            backend="qasm",
            mode="native_minimal",
            capability_level=3,
            production_ready=True,
        )
