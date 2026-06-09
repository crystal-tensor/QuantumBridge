import pytest

from quantumbridge.schema.error_mitigation_results import (
    ErrorMitigationResult,
    ReadoutMitigationResult,
    ZNEResult,
)


def test_zne_result_schema_round_trips():
    result = ZNEResult(
        workflow="zne_native",
        mode="native_minimal",
        capability_level=3,
        production_ready=False,
        native_implementation=True,
        observable="Z0",
        shots=16,
        noise_scales=[1.0, 2.0],
        noisy_expectation_values=[0.8, 0.7],
        mitigated_expectation_value=0.9,
        warnings=["demo"],
        provenance={"cloud_access": False},
    )

    restored = ZNEResult.from_dict(result.to_dict())

    assert restored.to_json()
    assert restored.mitigated_expectation_value == 0.9


def test_readout_result_schema_validates_normalized_probabilities():
    result = ReadoutMitigationResult(
        workflow="readout_mitigation_native",
        mode="native_minimal",
        capability_level=3,
        production_ready=False,
        mitigated_probabilities={"0": 0.25, "1": 0.75},
    )

    assert result.validate() is True


def test_error_mitigation_schema_rejects_production_ready_claim():
    with pytest.raises(ValueError):
        ErrorMitigationResult(
            workflow="bad",
            mode="native_minimal",
            capability_level=3,
            production_ready=True,
        )
