from pathlib import Path


def test_qiskit_algorithms_inventory_exists():
    text = Path("docs/compat/qiskit_algorithms_public_api_inventory.md").read_text()
    assert "Qiskit Algorithms Public API Inventory" in text
    assert "No upstream source" in text
