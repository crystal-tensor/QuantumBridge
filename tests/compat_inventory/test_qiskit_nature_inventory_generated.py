from pathlib import Path


def test_qiskit_nature_inventory_generated():
    text = Path("docs/compat/qiskit_nature_public_api_inventory.md").read_text()
    assert "Qiskit Nature Public API Inventory" in text
    assert "No upstream source" in text
    assert "Mode" in text
