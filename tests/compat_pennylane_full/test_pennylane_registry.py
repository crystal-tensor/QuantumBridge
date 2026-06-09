# This file is independently implemented for QuantumBridge SDK.
# No source code from Qiskit or PennyLane was copied.

from quantumbridge.compat.pennylane_full.registry import get_registry_entry, list_public_api_registry, registry_counts


def test_pennylane_registry_lists_modules():
    registry = list_public_api_registry()
    assert registry
    assert registry_counts()
    if any(record.import_module == "pennylane" and record.name == "QNode" for record in registry):
        assert get_registry_entry("pennylane", "QNode") is not None
