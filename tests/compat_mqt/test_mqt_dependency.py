from quantumbridge.compat.mqt import dependency_available, get_upstream_version, validate_mqt_dependencies


def test_mqt_dependency_report_is_offline_and_structured():
    report = validate_mqt_dependencies()

    assert "packages" in report
    assert report["cloud_access"] is False
    assert report["token_read"] is False
    assert report["hardware_access"] is False
    assert isinstance(dependency_available("mqt-core"), bool)
    assert get_upstream_version("mqt-core") is None or isinstance(get_upstream_version("mqt-core"), str)
