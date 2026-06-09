from quantumbridge.compat.quafu.dependency import validate_quafu_dependencies


def test_quafu_dependency_contract_is_offline():
    info = validate_quafu_dependencies()
    assert info["required_by_default"] is False
    assert info["cloud_access"] is False
    assert info["token_read"] is False
    assert info["hardware_access"] is False
