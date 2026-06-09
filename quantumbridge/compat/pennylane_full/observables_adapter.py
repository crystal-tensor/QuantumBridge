# This file is independently implemented for QuantumBridge SDK.
# No source code from Qiskit or PennyLane was copied.
"""PennyLane observable metadata scaffold."""

from quantumbridge.compat.pennylane_full.operations_adapter import ADAPTER, get_operation
from quantumbridge.compat.pennylane_full.warnings import adapter_metadata


OBSERVABLE_NAMES = ("PauliX", "PauliY", "PauliZ", "Identity", "Hadamard")

dependency_available = ADAPTER.dependency_available
get_upstream_version = ADAPTER.get_upstream_version
list_public_api_inventory = ADAPTER.list_public_api_inventory


def list_observables() -> list[str]:
    return list(OBSERVABLE_NAMES)


def describe_observable(name: str) -> dict:
    return {"name": name, "supported": name in OBSERVABLE_NAMES, **adapter_metadata()}


def get_observable(name: str):
    return get_operation(name)
