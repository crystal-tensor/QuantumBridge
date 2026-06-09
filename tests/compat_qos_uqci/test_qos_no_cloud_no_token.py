from quantumbridge.compat.qos_uqci.examples import qos_uqci_bell_circuit
from quantumbridge.compat.qos_uqci.job_spec import build_qos_uqci_job_spec
from quantumbridge.compat.qos_uqci.mock_runtime import run_qos_uqci_mock_runtime


def test_qos_paths_do_not_access_cloud_tokens_or_hardware():
    spec = build_qos_uqci_job_spec(qos_uqci_bell_circuit())
    result = run_qos_uqci_mock_runtime(spec)
    for payload in (spec, result.metadata, result.provenance):
        assert payload["cloud_access"] is False
        assert payload["token_read"] is False
        assert payload["hardware_access"] is False
