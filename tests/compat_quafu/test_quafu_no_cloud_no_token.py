from quantumbridge.compat.quafu.examples import quafu_bell_circuit
from quantumbridge.compat.quafu.job_adapter import build_quafu_job_spec
from quantumbridge.compat.quafu.mock_backend import run_quafu_mock_backend


def test_quafu_paths_do_not_access_cloud_tokens_or_hardware():
    spec = build_quafu_job_spec(quafu_bell_circuit())
    result = run_quafu_mock_backend(spec)
    for payload in (spec, result.metadata, result.provenance):
        assert payload["cloud_access"] is False
        assert payload["token_read"] is False
        assert payload["hardware_access"] is False
