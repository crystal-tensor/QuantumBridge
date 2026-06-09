import math

from quantumbridge.compat.qiskit_nature import run_h2_upstream_passthrough
from quantumbridge.schema.chemistry_results import UpstreamNatureResult


def test_h2_upstream_passthrough_runs_or_reports_missing_dependency():
    result = run_h2_upstream_passthrough()

    assert isinstance(result, UpstreamNatureResult)
    assert result.mode == "upstream_passthrough"
    assert result.upstream_package == "qiskit-nature"
    if result.unsupported_reason:
        assert "optional upstream dependency unavailable" in result.unsupported_reason
    else:
        assert result.raw_type
        assert math.isfinite(result.ground_state_energy)
        assert result.particle_count == 2
        assert result.provenance["cloud_access"] is False
