from quantumbridge.compat.qiskit_experiments import (
    native_dependency_available,
    run_upstream_experiments_if_available,
    validate_experiments_dependencies,
    wrap_upstream_experiments_result,
)


def test_upstream_experiments_path_runs_or_skips_cleanly():
    result = run_upstream_experiments_if_available()
    assert result.mode == "upstream_passthrough"
    assert result.provenance["cloud_access"] is False
    assert result.provenance["token_read"] is False
    assert result.provenance["hardware_access"] is False
    if not native_dependency_available():
        assert result.unsupported_reason


def test_wrap_upstream_experiments_result_metadata():
    result = wrap_upstream_experiments_result({"demo": True})
    assert result.raw_type == "dict"
    assert result.upstream_package == "qiskit-experiments"
    assert result.production_ready is False


def test_validate_experiments_dependencies_shape():
    report = validate_experiments_dependencies()
    assert report["dependency"] == "qiskit-experiments"
    assert report["cloud_access"] is False
