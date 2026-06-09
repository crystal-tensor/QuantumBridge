from quantumbridge.compat.qos_uqci.examples import qos_uqci_bell_circuit
from quantumbridge.compat.qos_uqci.job_spec import build_qos_uqci_job_spec, validate_qos_uqci_job_spec


def test_qos_uqci_job_spec_validates():
    spec = build_qos_uqci_job_spec(qos_uqci_bell_circuit(), shots=128, seed=21)
    assert validate_qos_uqci_job_spec(spec)
    assert spec["target"] == "qos_uqci"
    assert spec["execution_mode"] == "offline_mock"
    assert spec["cloud_access"] is False
