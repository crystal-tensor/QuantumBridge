# Copyright 2026 QuantumBridge Contributors.
# Licensed under the Apache License, Version 2.0.
"""Observe real ledgers without retaining their execution plans or arrays."""

import pytest

from quantumbridge.execution import UnifiedResourceLedger


@pytest.fixture
def derivative_accounts(monkeypatch):
    accounts = []
    original = UnifiedResourceLedger.__init__
    def capture(self, *args, **kwargs):
        original(self, *args, **kwargs)
        accounts.append(self)
    monkeypatch.setattr(UnifiedResourceLedger, "__init__", capture)
    return accounts
