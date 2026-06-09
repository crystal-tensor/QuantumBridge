from quantumbridge.compat.qiskit_dynamics import run_z_precession_native


def test_dynamics_native_path_has_no_cloud_token_or_hardware_access():
    result = run_z_precession_native()
    assert result.provenance["cloud_access"] is False
    assert result.provenance["token_read"] is False
    assert result.provenance["hardware_access"] is False
    assert result.hardware_calibration is False
