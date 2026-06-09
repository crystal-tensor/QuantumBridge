from quantumbridge.compat.quafu.upstream_adapter import run_upstream_pyquafu_if_available


def test_quafu_upstream_passthrough_reports_missing_dependency():
    result = run_upstream_pyquafu_if_available(package_name="definitely_missing_pyquafu")
    assert result.mode == "upstream_passthrough"
    assert result.capability_level == 0
    assert "not installed" in result.unsupported_reason
    assert result.provenance["hardware_access"] is False
