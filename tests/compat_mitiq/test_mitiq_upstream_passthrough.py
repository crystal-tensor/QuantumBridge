from quantumbridge.compat.mitiq import (
    dependency_available,
    run_readout_mitigation_upstream_if_available,
    run_zne_upstream_if_available,
    wrap_upstream_mitiq_result,
)
from quantumbridge.schema.error_mitigation_results import UpstreamMitiqResult


def test_upstream_mitiq_path_skips_clearly_when_missing_or_requires_executor_when_present():
    result = run_zne_upstream_if_available()

    assert isinstance(result, UpstreamMitiqResult)
    assert result.validate() is True
    assert result.mode == "upstream_passthrough"
    if dependency_available():
        assert "executor" in (result.unsupported_reason or "")
    else:
        assert "unavailable" in (result.unsupported_reason or "")


def test_upstream_readout_path_is_explicit():
    result = run_readout_mitigation_upstream_if_available()

    assert result.validate() is True
    assert result.metadata["cloud_access"] is False
    assert result.metadata["token_read"] is False
    assert result.metadata["hardware_access"] is False


def test_wrap_upstream_mitiq_result_sets_provenance():
    result = wrap_upstream_mitiq_result({"value": 1.0}, workflow="manual_wrap")

    assert result.workflow == "manual_wrap"
    assert result.provenance["upstream_source_copied"] is False
