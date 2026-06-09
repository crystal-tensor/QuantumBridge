from quantumbridge.compat.qiskit_experiments import (
    run_rabi_experiment_native,
    run_ramsey_experiment_native,
    run_t1_experiment_native,
)


def test_experiment_fit_results_include_goodness_metadata():
    for result in (
        run_rabi_experiment_native(),
        run_t1_experiment_native(),
        run_ramsey_experiment_native(),
    ):
        assert "sse" in result.fit_parameters
        assert "rmse" in result.fit_parameters
        assert "r_squared" in result.fit_parameters
        assert result.fit_parameters["rmse"] >= 0
