from quantumbridge.compat.torchquantum.dependency import dependency_available
from quantumbridge.compat.torchquantum.upstream_adapter import (
    run_upstream_torchquantum_if_available,
    wrap_upstream_torchquantum_result,
)


def test_upstream_torchquantum_passthrough_boundary():
    result = run_upstream_torchquantum_if_available()
    assert result.mode == "upstream_passthrough"
    assert result.upstream_package == "torchquantum"
    if not dependency_available():
        assert result.unsupported_reason
        assert result.capability_level == 0
    assert result.metadata["cloud_access"] is False


def test_wrap_upstream_torchquantum_result():
    result = wrap_upstream_torchquantum_result({"ok": True})
    assert result.raw_type == "dict"
    assert result.production_ready is False
