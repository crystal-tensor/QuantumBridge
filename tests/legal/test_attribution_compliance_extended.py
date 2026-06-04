# Copyright 2026 QuantumBridge Contributors.
# Licensed under the Apache License, Version 2.0.
# This file is part of QuantumBridge SDK.
# This implementation is developed for the QuantumBridge native architecture.

from pathlib import Path


def test_attribution_compliance_files_and_adapter_ledger_entries():
    required = [
        "THIRD_PARTY_NOTICES.md",
        "LICENSES/Apache-2.0.txt",
        "LICENSES/QISKIT_LICENSE.txt",
        "LICENSES/PENNYLANE_LICENSE.txt",
        "docs/migration/source_migration_ledger.md",
    ]
    for path in required:
        assert Path(path).is_file()

    ledger = Path("docs/migration/source_migration_ledger.md").read_text()
    for path in [
        "quantumbridge/__init__.py",
        "quantumbridge/compat/__init__.py",
        "quantumbridge/compat/qiskit_adapter.py",
        "quantumbridge/compat/pennylane_adapter.py",
        "quantumbridge/legal/attribution.py",
    ]:
        assert path in ledger
    assert "Adapter Integration" in ledger


def test_source_files_that_mention_upstream_are_recorded_in_ledger():
    ledger = Path("docs/migration/source_migration_ledger.md").read_text()
    for path in Path("quantumbridge").rglob("*.py"):
        text = path.read_text()
        if any(term in text for term in ["qiskit", "Qiskit", "pennylane", "PennyLane"]):
            assert str(path) in ledger


def test_no_adapter_file_claims_clean_room():
    for path in Path("quantumbridge/compat").glob("*.py"):
        text = path.read_text()
        assert "clean-room" not in text.lower()
