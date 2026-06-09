from quantumbridge.compat.qiskit_machine_learning.examples import (
    run_kernel_classifier_example,
    run_qnn_classifier_example,
    run_quantum_kernel_example,
)


def test_ml_examples_return_native_and_optional_upstream_results():
    for runner in [run_quantum_kernel_example, run_kernel_classifier_example, run_qnn_classifier_example]:
        results = runner()
        assert results["native"].validate() is True
        assert results["upstream"].validate() is True
        assert results["native"].production_ready is False
