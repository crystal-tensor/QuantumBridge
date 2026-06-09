from quantumbridge.compat.mitiq import (
    dependency_available,
    get_upstream_version,
    validate_mitiq_dependencies,
)


def test_mitiq_dependency_report_is_explicit_and_offline():
    report = validate_mitiq_dependencies()

    assert report["upstream_package"] == "mitiq"
    assert report["available"] is dependency_available()
    assert report["upstream_version"] == get_upstream_version()
    assert report["cloud_access"] is False
    assert report["token_read"] is False
    assert report["hardware_access"] is False
    assert report["warnings"]
