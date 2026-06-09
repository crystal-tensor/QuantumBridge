from quantumbridge.compat.qos_uqci.dependency import validate_qos_uqci_dependencies


def test_qos_uqci_dependency_contract_is_offline():
    info = validate_qos_uqci_dependencies()
    assert info["required_by_default"] is False
    assert info["cloud_access"] is False
    assert info["token_read"] is False
    assert info["hardware_access"] is False
