# This file is independently implemented for QuantumBridge SDK.
# No source code from Qiskit or PennyLane was copied.

from quantumbridge.compat.pennylane_full.inventory import list_public_api_inventory, inventory_summary


def test_pennylane_full_inventory_records_required_fields():
    records = list_public_api_inventory(max_items_per_module=10)
    assert records
    payload = records[0].to_dict()
    for key in (
        "module",
        "name",
        "object_type",
        "importable",
        "callable",
        "quantumbridge_level",
        "adapter",
        "upstream_required",
        "supported",
        "unsupported_reason",
        "risk",
        "notes",
    ):
        assert key in payload


def test_pennylane_full_inventory_summary_counts():
    summary = inventory_summary(list_public_api_inventory(max_items_per_module=5))
    assert summary["api_count"] >= 0
    assert summary["level_0"] >= 0
    assert summary["unsupported"] >= 0
