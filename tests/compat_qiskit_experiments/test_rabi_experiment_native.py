from quantumbridge.compat.qiskit_experiments import (
    fit_rabi_oscillation_native,
    generate_rabi_synthetic_data,
    run_rabi_experiment_native,
)


def test_native_rabi_experiment_runs():
    result = run_rabi_experiment_native(seed=7)
    assert result.workflow == "rabi_experiment_native"
    assert result.mode == "native_minimal"
    assert result.native_implementation is True
    assert result.production_ready is False
    assert result.hardware_calibration is False
    assert result.fit_parameters["frequency"] > 0


def test_rabi_fit_returns_finite_parameters():
    data = generate_rabi_synthetic_data(seed=7)
    fit = fit_rabi_oscillation_native(data)
    assert fit["frequency"] > 0
    assert fit["contrast"] > 0
    assert fit["rmse"] >= 0
