from quantumbridge.compat.qiskit_machine_learning import (
    run_kernel_classifier_native,
    run_qnn_classifier_native,
    run_quantum_kernel_native,
)


def test_ml_warnings_and_provenance_disclaim_full_replacement_and_high_risk_use():
    for result in [run_quantum_kernel_native(), run_kernel_classifier_native(), run_qnn_classifier_native()]:
        warning_text = " ".join(result.warnings)
        assert "not a full Qiskit Machine Learning replacement" in warning_text
        assert "not production machine learning software" in warning_text
        assert "high-risk automated decisions" in warning_text
        assert result.production_ready is False
        assert result.provenance["official_endorsement"] is False
        assert result.provenance["source_code_copied"] is False
