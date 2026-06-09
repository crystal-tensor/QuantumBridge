import pytest

from quantumbridge.schema.mqt_results import DDSIMLikeSimulationResult, MQTCompatibilityResult


def test_mqt_result_schema_roundtrips_complex_statevector():
    result = DDSIMLikeSimulationResult(
        workflow="demo",
        project="mqt-ddsim",
        mode="native_minimal",
        capability_level=3,
        production_ready=False,
        native_implementation=True,
        num_qubits=1,
        statevector=[1 + 0j, 0 + 0j],
        probabilities={"0": 1.0},
    )

    restored = DDSIMLikeSimulationResult.from_dict(result.to_dict())

    assert restored.statevector == [1 + 0j, 0 + 0j]
    assert restored.to_json()


def test_mqt_result_schema_rejects_production_ready_claim():
    with pytest.raises(ValueError):
        MQTCompatibilityResult(workflow="bad", production_ready=True)
