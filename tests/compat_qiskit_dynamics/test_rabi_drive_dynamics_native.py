from quantumbridge.compat.qiskit_dynamics import run_rabi_drive_dynamics_native


def test_rabi_drive_returns_expectation_values():
    result = run_rabi_drive_dynamics_native()
    assert result.workflow == "rabi_drive_dynamics_native"
    assert set(result.expectation_values) == {"x", "y", "z"}
    assert len(result.final_state) == 2
    assert result.metadata["offline_only"] is True
