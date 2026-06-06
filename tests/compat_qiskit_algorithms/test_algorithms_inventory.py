# This file is independently implemented for QuantumBridge SDK.
# No source code from Qiskit or PennyLane was copied.

from quantumbridge.compat.qiskit_algorithms.grover_adapter import ADAPTER


def test_algorithms_inventory_and_version_contract():
    assert isinstance(ADAPTER.dependency_available(), bool)
    assert ADAPTER.get_upstream_version() is None or isinstance(ADAPTER.get_upstream_version(), str)
    assert ADAPTER.list_public_api_inventory()