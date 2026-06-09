from quantumbridge.compat.mitiq import (
    bell_circuit,
    compare_noisy_and_mitigated_expectation,
    create_expectation_executor_from_aer_native,
    run_noisy_expectation_native,
    run_zne_native,
)
from quantumbridge.schema.error_mitigation_results import (
    ErrorMitigationComparisonResult,
    ZNEResult,
)


def test_native_zne_actually_runs_and_returns_finite_mitigation():
    result = run_zne_native(bell_circuit(), observable="ZZ", shots=128, seed=5)

    assert isinstance(result, ZNEResult)
    assert result.validate() is True
    assert result.workflow == "zne_native"
    assert result.native_implementation is True
    assert result.production_ready is False
    assert len(result.noise_scales) == len(result.noisy_expectation_values) == 3
    assert result.mitigated_expectation_value is not None
    assert -1.2 <= result.mitigated_expectation_value <= 1.2
    assert result.ideal_expectation_value == 1.0
    assert result.noisy_counts


def test_noisy_expectation_executor_uses_stage9f_simulator():
    sample = run_noisy_expectation_native(
        bell_circuit(), observable="ZZ", noise_scale=2.0, shots=64, seed=8
    )
    executor = create_expectation_executor_from_aer_native(
        bell_circuit(), observable="ZZ", shots=64, seed=8
    )

    assert sample.noisy_expectation_values
    assert -1.0 <= executor(2.0) <= 1.0
    assert sample.metadata["cloud_access"] is False


def test_native_zne_comparison_result():
    comparison = compare_noisy_and_mitigated_expectation(
        bell_circuit(), observable="ZZ", shots=64, seed=3
    )

    assert isinstance(comparison, ErrorMitigationComparisonResult)
    assert comparison.mode == "comparison"
    assert comparison.data["mitigation_delta"] is not None
