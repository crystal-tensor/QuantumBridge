# Copyright 2026 QuantumBridge Contributors. Apache-2.0.
"""Channel origin admission precedes data callbacks, copies and publication."""

import gc

import numpy as np
import pytest

import quantumbridge as qb
from quantumbridge.core.classical import UnsupportedFeature
from quantumbridge.execution import UnifiedResourceLedger as Ledger, UnifiedExecutionLimits as Limits
from quantumbridge.execution.resource_context import ResourceScope
from quantumbridge.information import Kraus, SuperOp, Choi, PTM, Chi, Stinespring


@pytest.mark.parametrize("representation", [Kraus, SuperOp, Choi, PTM, Chi, Stinespring])
@pytest.mark.parametrize("field", ["basis", "dimension", "data"])
def test_forged_native_channel_fields_refuse_before_numeric_callbacks(representation, field, monkeypatch):
    class Foreign:
        def __array__(self, *a, **k):pytest.fail("Foreign channel array conversion")
        def __eq__(self, other):pytest.fail("Foreign origin comparison")
    channel = representation(qb.Circuit(2).h(0).cx(0, 1))
    if field == "basis":object.__setattr__(channel, "_public_matrix_basis", Foreign())
    elif field == "dimension":channel._input_dim = Foreign()
    elif representation is Kraus:channel._left = (Foreign(),)
    else:channel.data = Foreign()
    ledger = Ledger()
    with ResourceScope(ledger), monkeypatch.context() as patch:
        patch.setattr(np, "empty", lambda *a, **k: pytest.fail("Forged owner allocated"))
        with pytest.raises((ValueError, TypeError)):channel.to_operator()
    assert ledger.receipt()["live_memory_bytes"] == 0


def test_foreign_channel_subclass_property_is_never_dispatched():
    class Foreign(Kraus):
        @property
        def data(self):pytest.fail("Foreign channel property")
    value = object.__new__(Foreign)
    for operation in (Kraus, SuperOp, lambda x: Kraus.to_operator(x)):
        with pytest.raises(UnsupportedFeature):operation(value)


def test_channel_operator_copy_exact_budget_and_public_snapshot_retained_lifetime(monkeypatch):
    channel = Kraus(qb.Circuit(2).h(0).s(1).cx(0, 1))
    channel.data[0].flags.writeable = False
    expected = channel.data[0].copy()
    amount = expected.nbytes
    failed = Ledger(Limits(max_total_memory_bytes=amount - 1))
    with ResourceScope(failed), monkeypatch.context() as patch:
        patch.setattr(np, "empty", lambda *a, **k: pytest.fail("Denied channel copy allocated"))
        with pytest.raises(MemoryError):channel.to_operator()
    assert failed.receipt()["live_memory_bytes"] == 0
    parent = Ledger(Limits(max_total_memory_bytes=2 * amount))
    child = Ledger(parent=parent)
    with ResourceScope(child):
        operator = channel.to_operator()
        assert child.receipt()["live_memory_bytes"] == amount
        public = operator.as_qiskit_operator()
    assert parent.receipt()["live_memory_bytes"] == 2 * amount
    np.testing.assert_array_equal(operator.data, expected)
    views = operator.data[:, 0], public.data[:, 0]
    del operator, public
    gc.collect()
    assert parent.receipt()["live_memory_bytes"] == 2 * amount
    del views
    gc.collect()
    assert child.receipt()["live_memory_bytes"] == parent.receipt()["live_memory_bytes"] == 0
    with ResourceScope(failed):recovered = Kraus(qb.Circuit(1)).to_operator()
    assert recovered.data.shape == (2, 2)


def test_channel_origin_is_readonly_and_not_an_arithmetic_mode():
    channel = Kraus(qb.Circuit(2).h(0))
    with pytest.raises(AttributeError):channel._public_matrix_basis = "unresolved"
    operator = channel.to_operator()
    assert operator.arithmetic_convention == "native"
    assert "_arithmetic_convention" not in operator.__dict__


def test_channel_copy_failure_does_not_publish_partial_origin_or_retain_buffers(monkeypatch):
    import importlib
    module = importlib.import_module("quantumbridge.information.channels")
    channel = Kraus(qb.Circuit(2).h(0).cx(0, 1))
    before = channel.data[0].copy()
    original = module._matrix_group
    ledger = Ledger()
    def fail_after_copy(*args, **kwargs):
        copied = original(*args, **kwargs)
        assert copied[0] is not channel.data[0]
        raise RuntimeError("channel copy fault")
    with monkeypatch.context() as patch:
        patch.setattr(module, "_matrix_group", fail_after_copy)
        try:
            with ResourceScope(ledger):channel.copy()
        except RuntimeError as error:assert str(error) == "channel copy fault"
        else:pytest.fail("Channel injection was not reached")
    gc.collect()
    assert ledger.receipt()["live_memory_bytes"] == 0
    np.testing.assert_array_equal(channel.data[0], before)
    assert channel.__dict__["_public_matrix_basis"] == "native"
    with ResourceScope(ledger):recovered = channel.copy()
    assert recovered.__dict__["_public_matrix_basis"] == "native"
