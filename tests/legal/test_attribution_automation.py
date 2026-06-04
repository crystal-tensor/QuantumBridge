# Copyright 2026 QuantumBridge Contributors.
# Licensed under the Apache License, Version 2.0.
# This file is part of QuantumBridge SDK.
# This implementation is developed for the QuantumBridge native architecture.

from quantumbridge.legal import validate_attribution_files


def test_attribution_validator_reports_required_files():
    checks = validate_attribution_files(".")
    assert all(checks.values())

