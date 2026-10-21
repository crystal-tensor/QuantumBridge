# Copyright 2026 QuantumBridge Contributors.
# Licensed under the Apache License, Version 2.0.
"""Physical snapshot allocation and request admission are distinct accounts."""

import gc
from concurrent.futures import ThreadPoolExecutor
from threading import Barrier
import weakref

import numpy as np
import pytest

from quantumbridge.core.classical import UnsupportedFeature
from quantumbridge.execution import UnifiedExecutionLimits as Limits, UnifiedResourceLedger as Ledger
from quantumbridge.execution.persistent_storage import PersistentStoragePool
from quantumbridge.execution.resource_context import ResourceScope, current_resources


def test_pool_rejects_before_copy_factory(monkeypatch):
    from quantumbridge.execution import array_ownership
    calls, original = [], array_ownership.retained_array
    def tracked(ledger, category, shape, dtype, factory):
        def copy():
            calls.append(shape)
            return factory()
        return original(ledger, category, shape, dtype, copy)
    monkeypatch.setattr(array_ownership, "retained_array", tracked)
    pool = PersistentStoragePool(Limits(max_total_memory_bytes=63))
    with pytest.raises(MemoryError): pool.freeze(np.ones(8))
    assert calls == []
    assert pool.receipt()["persistent_owned_bytes"] == 0
    assert pool.receipt()["new_physical_allocation_count"] == 0
    assert current_resources() is None


def test_pool_identity_alias_views_and_last_surviving_view():
    pool = PersistentStoragePool()
    array = np.arange(12, dtype=float).reshape(3, 4)
    owner = pool.freeze({"a": array, "alias": array, "transpose": array.T})
    first = owner.payload["a"]
    assert first is owner.payload["alias"]
    assert not np.shares_memory(first, owner.payload["transpose"])
    assert not first.flags.writeable
    with pytest.raises(ValueError): first[0, 0] = 9
    view = first[:, 1:]
    del first, owner
    gc.collect()
    assert pool.receipt()["persistent_owned_bytes"] == 96
    assert pool.receipt()["new_physical_allocation_count"] == 2
    assert pool.receipt()["live_physical_storage_count"] == 1
    np.testing.assert_array_equal(view, array[:, 1:])
    del view
    gc.collect()
    assert pool.receipt()["persistent_owned_bytes"] == 0


def test_shared_pool_sums_real_copies_and_recovers_after_owner_dies():
    pool = PersistentStoragePool(Limits(max_total_memory_bytes=128))
    source = np.ones(8)
    first, second = pool.freeze(source), pool.freeze(source)
    assert not np.shares_memory(first.payload, second.payload)
    with pytest.raises(MemoryError): pool.freeze(source)
    assert pool.receipt()["persistent_owned_bytes"] == 128
    assert pool.receipt()["new_physical_allocation_count"] == 2
    del first
    gc.collect()
    third = pool.freeze(source)
    assert pool.receipt()["persistent_owned_bytes"] == 128
    del second, third
    gc.collect()
    assert pool.receipt()["persistent_owned_bytes"] == 0


def test_partial_pool_copy_failure_follows_actual_error_lifetime():
    pool = PersistentStoragePool(Limits(max_total_memory_bytes=64))
    with pytest.raises(MemoryError) as failure:
        pool.freeze([np.ones(8), np.zeros(8)])
    assert pool.receipt()["persistent_owned_bytes"] == 64
    del failure
    gc.collect()
    assert pool.receipt()["persistent_owned_bytes"] == 0
    owner = pool.freeze(np.ones(8))
    assert owner.nbytes == 64


def test_foreign_and_subclass_copy_protocols_are_rejected_before_dispatch():
    calls = []
    class Foreign:
        def __deepcopy__(self, memo):
            calls.append("foreign")
            return self
    class Array(np.ndarray):
        def __deepcopy__(self, memo):
            calls.append("array")
            return np.asarray(self).copy()
    pool = PersistentStoragePool()
    for value in (Foreign(), np.ones(4).view(Array)):
        with pytest.raises(UnsupportedFeature): pool.freeze(value)
    assert calls == [] and pool.receipt()["persistent_owned_bytes"] == 0


def test_pool_policy_is_not_the_enclosing_request_cap():
    ledger, pool = Ledger(Limits(max_total_memory_bytes=1)), PersistentStoragePool()
    with ResourceScope(ledger) as scope:
        owner = pool.freeze(np.ones(8))
        assert current_resources() is scope
        assert ledger.receipt()["live_memory_bytes"] == 0
        with pytest.raises(MemoryError): owner.admit(scope)
        assert ledger.receipt()["live_memory_bytes"] == 0
    assert owner.nbytes == pool.receipt()["persistent_owned_bytes"] == 64
    assert current_resources() is None


def test_resident_dedup_is_request_local_and_not_new_array_observation():
    pool, ledger = PersistentStoragePool(), Ledger()
    owner = pool.freeze(np.ones(8))
    with ResourceScope(ledger) as outer:
        owner.admit(outer)
        with ResourceScope(ledger) as inner:
            owner.admit(inner)
            receipt = ledger.receipt()
            assert receipt["request_resident_charge_bytes"] == 64
            assert receipt["request_new_allocation_reserved_bytes"] == 0
            assert receipt["observed_array_bytes"] == {}
            assert receipt["local_resident_storage_count"] == 1
        assert ledger.receipt()["request_resident_charge_bytes"] == 64
    receipt = ledger.receipt()
    assert receipt["live_memory_bytes"] == 0
    assert receipt["total_resident_charge_bytes"] == receipt["total_released_resident_charge_bytes"] == 64
    assert pool.receipt()["persistent_owned_bytes"] == 64


def test_new_request_with_same_ledger_does_not_dedup_previous_admission():
    pool, ledger = PersistentStoragePool(), Ledger()
    owner = pool.freeze(np.ones(8))
    with ResourceScope(ledger) as outer:
        owner.admit(outer)
        with ResourceScope(ledger, new_request=True) as inner:
            owner.admit(inner)
            assert ledger.receipt()["request_resident_charge_bytes"] == 128
        assert ledger.receipt()["request_resident_charge_bytes"] == 64
    assert ledger.receipt()["live_memory_bytes"] == 0
    assert pool.receipt()["new_physical_allocation_count"] == 1


def test_resident_parent_cap_failure_is_atomic_and_never_refunds_work():
    pool = PersistentStoragePool()
    owner = pool.freeze([np.ones(8), np.ones(4)])
    parent = Ledger(Limits(max_total_memory_bytes=100, max_derivative_work=5))
    child = Ledger(parent=parent)
    parent.consume(derivative_work=4, shots=7)
    with parent.reserve("other", memory_bytes=8), ResourceScope(child) as scope:
        with pytest.raises(MemoryError): owner.admit(scope)
        assert child.receipt()["live_memory_bytes"] == 0
        assert child.receipt()["local_resident_storage_count"] == 0
        assert parent.receipt()["live_memory_bytes"] == 8
    with ResourceScope(child) as scope:
        owner.admit(scope)
        child.consume(derivative_work=1)
        assert parent.receipt()["live_memory_bytes"] == 96
    assert parent.receipt()["live_memory_bytes"] == 0
    assert parent.receipt()["consumed_derivative_work"] == 5
    assert parent.receipt()["consumed_shots"] == 7
    with pytest.raises(MemoryError): child.consume(derivative_work=1)


def test_resident_release_retains_physical_storage_until_lease_dies():
    pool, ledger = PersistentStoragePool(), Ledger()
    owner = pool.freeze(np.ones(8))
    reference = weakref.ref(owner.payload)
    lease = ledger.borrow_resident(owner.roots)
    del owner
    gc.collect()
    assert reference() is not None
    lease.release()
    lease.release()
    gc.collect()
    assert reference() is None
    assert ledger.receipt()["live_memory_bytes"] == pool.receipt()["persistent_owned_bytes"] == 0
    with pytest.raises(ValueError): lease.__enter__()


def test_concurrent_requests_charge_shared_kernel_independently():
    pool, ledger = PersistentStoragePool(), Ledger(Limits(max_total_memory_bytes=128))
    owner = pool.freeze(np.ones(8))
    both = Barrier(2)
    def request(_):
        with ResourceScope(ledger, new_request=True) as scope:
            owner.admit(scope)
            both.wait(timeout=10)
            resident = ledger.receipt()["request_resident_charge_bytes"]
            both.wait(timeout=10)
            assert current_resources() is scope
            return resident
    with ThreadPoolExecutor(max_workers=2) as executor:
        assert list(executor.map(request, range(2))) == [128, 128]
    assert ledger.receipt()["live_memory_bytes"] == 0
    assert ledger.receipt()["peak_resident_charge_bytes"] == 128
    assert pool.receipt()["persistent_owned_bytes"] == 64
    assert pool.receipt()["new_physical_allocation_count"] == 1


@pytest.mark.parametrize("bad", [lambda: np.ones(1), lambda: np.ones(2)[1:]])
def test_resident_rejects_mutable_or_nonroot_arrays(bad):
    array = bad()
    if array.base is not None: array.flags.writeable = False
    ledger = Ledger()
    with pytest.raises(ValueError): ledger.borrow_resident((array,))
    assert ledger.receipt()["live_memory_bytes"] == 0
