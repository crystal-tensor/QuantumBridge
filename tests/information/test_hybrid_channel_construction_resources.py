# Copyright 2026 QuantumBridge Contributors. Apache-2.0.
"""Normalization owns a separate buffer and releases it on all failure paths."""

from concurrent.futures import ThreadPoolExecutor
import gc
import importlib

import numpy as np
import pytest

from quantumbridge.core.classical import UnsupportedFeature
from quantumbridge.core.gate_limits import GateCircuitLimits, gate_circuit_scope
from quantumbridge.execution import UnifiedResourceLedger as Ledger, UnifiedExecutionLimits as Limits
from quantumbridge.execution.resource_context import ResourceScope
from quantumbridge.information import Operator, Kraus, SuperOp, Choi, PTM, Chi, Stinespring
from test_hybrid_channel_construction import source


REPRESENTATIONS = (Kraus, SuperOp, Choi, PTM, Chi, Stinespring)


@pytest.mark.parametrize("representation", [Kraus, Stinespring])
def test_hybrid_channel_exact_minus_one_snapshot_budget_and_retained_view(representation, monkeypatch):
    owner, high = source()
    owner.data.flags.writeable = False
    amount = owner.data.nbytes
    denied = Ledger(Limits(max_total_memory_bytes=amount - 1))
    with ResourceScope(denied), monkeypatch.context() as patch:
        patch.setattr(np, "empty", lambda *a, **k: pytest.fail("Denied normalization allocated"))
        with pytest.raises(MemoryError):representation(owner)
    assert denied.receipt()["live_memory_bytes"] == 0
    accepted = Ledger(Limits(max_total_memory_bytes=amount))
    with ResourceScope(accepted):channel = representation(owner)
    data = channel.data[0] if representation is Kraus else channel.data
    assert accepted.receipt()["live_memory_bytes"] == accepted.receipt()["peak_memory_bytes"] == amount
    assert not np.shares_memory(data, owner.data)
    np.testing.assert_array_equal(data, high)
    view = data[:, 0]
    del channel, data
    gc.collect()
    assert accepted.receipt()["live_memory_bytes"] == amount
    del view
    gc.collect()
    assert accepted.receipt()["live_memory_bytes"] == 0
    with ResourceScope(denied):recovered = Kraus(Operator(np.eye(2)))
    assert recovered.data[0].shape == (2, 2)


def test_source_and_normalized_channel_are_two_distinct_accounted_allocations():
    from quantumbridge.execution.array_ownership import copied_array
    owner, high = source()
    amount = owner.data.nbytes
    parent = Ledger(Limits(max_total_memory_bytes=2 * amount))
    child = Ledger(parent=parent)
    with ResourceScope(parent):owner.data = copied_array(owner.data, category="hybrid_source_snapshot")
    assert parent.receipt()["live_memory_bytes"] == amount
    with ResourceScope(child):channel = Kraus(owner)
    assert parent.receipt()["live_memory_bytes"] == 2 * amount
    assert child.receipt()["live_memory_bytes"] == amount
    np.testing.assert_array_equal(channel.data[0], high)
    assert not np.shares_memory(owner.data, channel.data[0])
    del channel
    gc.collect()
    assert child.receipt()["live_memory_bytes"] == 0
    assert parent.receipt()["live_memory_bytes"] == amount
    del owner
    gc.collect()
    assert parent.receipt()["live_memory_bytes"] == 0


@pytest.mark.parametrize("representation", REPRESENTATIONS)
@pytest.mark.parametrize("field", ["basis", "target_width", "shape", "dims", "dtype", "foreign_data", "nan", "inf", "width"])
def test_hybrid_channel_bad_source_refuses_before_numeric_allocation(representation, field, monkeypatch):
    class Foreign:
        def __eq__(self, other):pytest.fail("Foreign origin compared")
        def __array__(self, *a, **k):pytest.fail("Foreign buffer converted")
        def __index__(self):pytest.fail("Foreign dimension converted")
    owner, _ = source()
    if field == "basis":owner._public_matrix_basis = Foreign()
    elif field == "target_width":object.__setattr__(owner, "_literal_target_width", Foreign())
    elif field == "shape":owner.data = np.eye(4, dtype=complex)
    elif field == "dims":owner._input_dims = (Foreign(),)
    elif field == "dtype":owner.data = owner.data.real.copy()
    elif field == "foreign_data":owner.data = Foreign()
    elif field == "width":owner.num_qubits = 2
    else:owner.data[0, 0] = np.nan if field == "nan" else np.inf
    fields = owner.__dict__.copy()
    ledger = Ledger()
    with ResourceScope(ledger), monkeypatch.context() as patch:
        patch.setattr(np, "empty", lambda *a, **k: pytest.fail("Invalid channel source allocated"))
        with pytest.raises((ValueError, TypeError)):representation(owner)
    assert ledger.receipt()["live_memory_bytes"] == ledger.receipt()["peak_memory_bytes"] == 0
    assert all(owner.__dict__[key] is value for key, value in fields.items())


@pytest.mark.parametrize("representation", REPRESENTATIONS)
def test_hybrid_channel_caps_and_foreign_subclasses_refuse_before_copy(representation, monkeypatch):
    class Foreign(Operator):
        @property
        def data(self):pytest.fail("Foreign Operator data property")
    owner, _ = source()
    foreign = object.__new__(Foreign)
    ledger = Ledger()
    with ResourceScope(ledger), monkeypatch.context() as patch:
        patch.setattr(np, "empty", lambda *a, **k: pytest.fail("Denied channel owner allocated"))
        with pytest.raises(UnsupportedFeature):representation(foreign)
        with gate_circuit_scope(GateCircuitLimits(max_matrix_dimension=4)):
            with pytest.raises(MemoryError):representation(owner)
    assert ledger.receipt()["live_memory_bytes"] == ledger.receipt()["peak_memory_bytes"] == 0


@pytest.mark.parametrize("representation", REPRESENTATIONS)
def test_fault_after_normalization_releases_snapshot_without_publishing_channel(representation, monkeypatch):
    module = importlib.import_module("quantumbridge.information.channels")
    owner, high = source()
    owner.data.flags.writeable = False
    before = owner.data.copy()
    original = module._operator_data
    ledger = Ledger()
    def fail_after_snapshot(*a, **k):
        snapshot = original(*a, **k)
        assert not np.shares_memory(snapshot, owner.data)
        assert ledger.receipt()["live_memory_bytes"] == owner.data.nbytes
        raise RuntimeError("normalized snapshot fault")
    with monkeypatch.context() as patch:
        patch.setattr(module, "_operator_data", fail_after_snapshot)
        try:
            with ResourceScope(ledger):representation(owner)
        except RuntimeError as error:assert str(error) == "normalized snapshot fault"
        else:pytest.fail("Snapshot fault was not reached")
    gc.collect()
    assert ledger.receipt()["live_memory_bytes"] == 0
    np.testing.assert_array_equal(owner.data, before)
    assert owner.__dict__["_public_matrix_basis"] == "hybrid"
    with ResourceScope(ledger):recovered = representation(owner)
    np.testing.assert_allclose(recovered.to_superop().data, np.kron(high.conj(), high), atol=3e-12, rtol=0)


def test_readonly_hybrid_channel_concurrent_children_keep_independent_leases():
    owner, high = source()
    owner.data.flags.writeable = False
    before = owner.data.copy()
    amount = owner.data.nbytes
    parent = Ledger(Limits(max_total_memory_bytes=3 * amount))
    children = [Ledger(parent=parent) for _ in range(3)]
    def execute(ledger):
        with ResourceScope(ledger):return Kraus(owner)
    with ThreadPoolExecutor(max_workers=3) as pool:results = list(pool.map(execute, children))
    assert parent.receipt()["live_memory_bytes"] == 3 * amount
    for index, result in enumerate(results):
        np.testing.assert_array_equal(result.data[0], high)
        assert children[index].receipt()["live_memory_bytes"] == amount
        assert not np.shares_memory(result.data[0], owner.data)
        assert result.__dict__["_public_matrix_basis"] == "native"
        with pytest.raises(AttributeError):result._public_matrix_basis = "hybrid"
    assert not np.shares_memory(results[0].data[0], results[1].data[0])
    del result, results
    gc.collect()
    assert parent.receipt()["live_memory_bytes"] == 0
    np.testing.assert_array_equal(owner.data, before)


def test_hybrid_channel_fault_inside_permutation_releases_first_snapshot(monkeypatch):
    module = importlib.import_module("quantumbridge.information.operator")
    owner, high = source()
    owner.data.flags.writeable = False
    before = owner.data.copy()
    ledger = Ledger()
    with monkeypatch.context() as patch:
        patch.setattr(module, "_bits_to_index", lambda *a: (_ for _ in ()).throw(RuntimeError("channel permutation fault")))
        try:
            with ResourceScope(ledger):Kraus(owner)
        except RuntimeError as error:assert str(error) == "channel permutation fault"
        else:pytest.fail("Permutation fault was not reached")
    gc.collect()
    assert ledger.receipt()["peak_memory_bytes"] == owner.data.nbytes
    assert ledger.receipt()["live_memory_bytes"] == 0
    np.testing.assert_array_equal(owner.data, before)
    assert owner.__dict__["_public_matrix_basis"] == "hybrid"
    with ResourceScope(ledger):recovered = Kraus(owner)
    np.testing.assert_array_equal(recovered.data[0], high)
