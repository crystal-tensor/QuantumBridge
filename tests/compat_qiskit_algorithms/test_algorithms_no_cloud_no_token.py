# This file is independently implemented for QuantumBridge SDK.
# No source code from Qiskit Algorithms was copied.

from quantumbridge.compat.qiskit_algorithms import run_vqe_native, validate_algorithms_dependencies


def test_algorithms_paths_do_not_access_cloud_tokens_or_hardware():
    report = validate_algorithms_dependencies()
    result = run_vqe_native(parameter_grid=(0.0, 3.141592653589793))
    assert report["cloud_access"] is False
    assert report["token_read"] is False
    assert report["token_storage"] is False
    assert report["hardware_access"] is False
    assert result.provenance["cloud_access"] is False
    assert result.provenance["token_access"] is False
    assert result.provenance["hardware_access"] is False
