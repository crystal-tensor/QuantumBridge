from quantumbridge.compat.benchpress.upstream_adapter import run_upstream_benchpress_if_available


def test_upstream_benchpress_passthrough_boundary():
    result = run_upstream_benchpress_if_available()
    assert result.mode == "upstream_passthrough"
    assert result.native_implementation is False
    assert result.provenance["cloud_access"] is False
    assert result.provenance["hardware_access"] is False
