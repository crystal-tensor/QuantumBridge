from quantumbridge.compat.qos_uqci.upstream_adapter import run_upstream_qos_uqci_if_available


def test_qos_upstream_passthrough_reports_missing_dependency():
    result = run_upstream_qos_uqci_if_available(package_name="definitely_missing_qos_uqci")
    assert result.mode == "upstream_passthrough"
    assert result.capability_level == 0
    assert "not installed" in result.unsupported_reason
    assert result.provenance["cloud_access"] is False
