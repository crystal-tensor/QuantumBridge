from quantumbridge.compat.benchpress.dependency import validate_benchpress_dependencies


def test_benchpress_dependency_contract_is_offline():
    report = validate_benchpress_dependencies()
    assert report["cloud_required"] is False
    assert report["credentials_required"] is False
    assert report["hardware_required"] is False
    assert report["production_ready"] is False
