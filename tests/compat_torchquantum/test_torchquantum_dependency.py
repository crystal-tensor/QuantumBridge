from quantumbridge.compat.torchquantum.dependency import (
    dependency_available,
    validate_torchquantum_dependencies,
)


def test_torchquantum_dependency_contract():
    info = validate_torchquantum_dependencies()
    assert info["package"] == "torchquantum"
    assert info["available"] is dependency_available()
    assert info["required_by_default"] is False
    assert info["cloud_access"] is False
    assert info["token_read"] is False
    assert info["hardware_access"] is False
