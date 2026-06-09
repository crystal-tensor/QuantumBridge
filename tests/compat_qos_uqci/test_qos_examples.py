from quantumbridge.compat.qos_uqci.examples import (
    run_qos_uqci_bell_job_example,
    run_qos_uqci_mock_runtime_example,
)


def test_qos_examples_return_job_and_result():
    job = run_qos_uqci_bell_job_example()
    runtime = run_qos_uqci_mock_runtime_example()
    assert job["job_spec"]["target"] == "qos_uqci"
    assert runtime["result"].counts
