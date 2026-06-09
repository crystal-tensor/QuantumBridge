from quantumbridge.compat.qiskit_experiments import (
    fit_t1_decay_native,
    generate_t1_synthetic_data,
    run_t1_experiment_native,
)


def test_native_t1_experiment_runs():
    result = run_t1_experiment_native(seed=7)
    assert result.workflow == "t1_experiment_native"
    assert result.mode == "native_minimal"
    assert result.fit_parameters["t1"] > 0
    assert result.hardware_calibration is False


def test_t1_fit_returns_positive_parameter():
    data = generate_t1_synthetic_data(seed=7)
    fit = fit_t1_decay_native(data)
    assert fit["t1"] > 0
    assert fit["rmse"] >= 0
