import pytest

from quantumbridge.compat.mitiq import (
    expectation_from_counts,
    linear_zero_noise_extrapolate,
    polynomial_zero_noise_extrapolate,
    scale_noise_model_educational,
)


def test_linear_extrapolation_recovers_zero_noise_intercept():
    assert linear_zero_noise_extrapolate([1.0, 2.0, 3.0], [0.9, 0.8, 0.7]) == pytest.approx(1.0)


def test_polynomial_extrapolation_works_on_deterministic_input():
    value = polynomial_zero_noise_extrapolate([1.0, 2.0, 3.0], [0.8, 0.2, -0.8], degree=2)
    assert value == pytest.approx(1.0)


def test_expectation_from_counts_supports_z_and_parity_observables():
    counts = {"00": 5, "11": 5}

    assert expectation_from_counts(counts, "ZZ") == 1.0
    assert expectation_from_counts(counts, "Z0") == 0.0
    assert expectation_from_counts(counts, "PARITY") == 1.0


def test_scale_noise_model_keeps_probability_bounds():
    scaled = scale_noise_model_educational({"type": "measurement_bitflip", "p": 0.6}, 3.0)

    assert scaled["p"] == 1.0
    assert scaled["production_ready"] is False
