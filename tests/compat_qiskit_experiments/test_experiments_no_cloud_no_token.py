from quantumbridge.compat.qiskit_experiments import run_rabi_experiment_native


def test_experiments_native_path_has_no_cloud_token_or_hardware_access():
    result = run_rabi_experiment_native()
    assert result.provenance["cloud_access"] is False
    assert result.provenance["token_read"] is False
    assert result.provenance["hardware_access"] is False
    assert result.provenance["hardware_calibration"] is False
