# Copyright 2026 QuantumBridge Contributors.
# Licensed under the Apache License, Version 2.0.
# This file is part of QuantumBridge SDK.
# This implementation is developed for the QuantumBridge native architecture.

from pathlib import Path


def test_third_party_notices_present():
    text = Path("THIRD_PARTY_NOTICES.md").read_text()
    assert "Qiskit attribution" in text
    assert "PennyLane attribution" in text
    assert "Apache License 2.0" in text

