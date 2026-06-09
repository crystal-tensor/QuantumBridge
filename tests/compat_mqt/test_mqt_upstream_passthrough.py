from quantumbridge.compat.mqt import (
    run_upstream_ddsim_if_available,
    run_upstream_mqt_core_if_available,
    run_upstream_qmap_if_available,
)


def test_mqt_upstream_paths_are_clear_passthrough_or_unsupported():
    for result in (
        run_upstream_mqt_core_if_available(),
        run_upstream_ddsim_if_available(),
        run_upstream_qmap_if_available(),
    ):
        assert result.mode == "upstream_passthrough"
        assert result.production_ready is False
        assert result.metadata["cloud_access"] is False
        assert result.unsupported_reason or result.raw_type
