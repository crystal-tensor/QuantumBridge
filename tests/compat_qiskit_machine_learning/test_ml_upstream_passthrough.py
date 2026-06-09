from quantumbridge.compat.qiskit_machine_learning.upstream_adapter import (
    dependency_available,
    run_upstream_classifier_if_available,
    run_upstream_qnn_if_available,
    run_upstream_quantum_kernel_if_available,
    validate_ml_dependencies,
)


def test_upstream_dependency_report_has_no_cloud_or_token():
    report = validate_ml_dependencies()

    assert isinstance(report["available"], bool)
    assert report["cloud_access"] is False
    assert report["token_read"] is False
    assert report["hardware_access"] is False


def test_upstream_paths_run_or_clear_skip():
    results = [
        run_upstream_qnn_if_available(),
        run_upstream_quantum_kernel_if_available(),
        run_upstream_classifier_if_available(),
    ]

    for result in results:
        assert result.validate() is True
        assert result.mode == "upstream_passthrough"
        if not dependency_available():
            assert result.unsupported_reason
        else:
            assert result.raw_type
