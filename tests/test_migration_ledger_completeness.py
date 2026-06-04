# Copyright 2026 QuantumBridge Contributors.
# Licensed under the Apache License, Version 2.0.
# This file is part of QuantumBridge SDK.
# This implementation is developed for the QuantumBridge native architecture.

from pathlib import Path


def test_migration_ledger_completeness():
    text = Path("docs/migration/source_migration_ledger.md").read_text()
    assert "quantumbridge/compat/qiskit_adapter.py" in text
    assert "quantumbridge/compat/pennylane_adapter.py" in text
    assert "No Source Port with Attribution was performed" in text

