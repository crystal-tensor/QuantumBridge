from quantumbridge.compat.qiskit_machine_learning import (
    run_kernel_classifier_native,
    run_qnn_classifier_native,
    run_quantum_kernel_native,
)


def test_native_ml_workflows_do_not_access_cloud_tokens_or_hardware():
    for result in [run_quantum_kernel_native(), run_kernel_classifier_native(), run_qnn_classifier_native()]:
        assert result.metadata["cloud_access"] is False
        assert result.metadata["token_read"] is False
        assert result.metadata["hardware_access"] is False
        assert result.provenance["cloud_access"] is False
        assert result.provenance["token_read"] is False
        assert result.provenance["hardware_access"] is False
