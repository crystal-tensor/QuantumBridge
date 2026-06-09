from quantumbridge.compat.qiskit_dynamics import run_z_precession_native


def test_z_precession_returns_time_series_and_final_state():
    result = run_z_precession_native()
    assert result.mode == "native_minimal"
    assert len(result.time_points) == len(result.expectation_values["x"])
    assert len(result.final_state) == 2
    assert result.production_ready is False
