from quantumbridge.compat.qiskit_experiments import (
    fit_ramsey_native,
    generate_ramsey_synthetic_data,
    run_ramsey_experiment_native,
)


def test_native_ramsey_experiment_runs():
    result = run_ramsey_experiment_native(seed=7)
    assert result.workflow == "ramsey_experiment_native"
    assert result.mode == "native_minimal"
    assert result.fit_parameters["detuning"] > 0
    assert result.fit_parameters["t2star"] > 0
    assert result.hardware_calibration is False


def test_ramsey_fit_returns_finite_metadata():
    data = generate_ramsey_synthetic_data(seed=7)
    fit = fit_ramsey_native(data)
    assert fit["detuning"] > 0
    assert fit["t2star"] > 0
    assert fit["rmse"] >= 0
