# Copyright 2026 QuantumBridge Contributors.
# Licensed under the Apache License, Version 2.0.
"""Actual storage roots, views and independent copies own their leases."""

import gc
import weakref

import numpy as np
import pytest

from quantumbridge.execution import UnifiedExecutionLimits as Limits, UnifiedResourceLedger
from quantumbridge.execution.array_ownership import retained_array, retain_reservation
from quantumbridge.execution.array_reservations import ArrayReservation


def test_views_keep_one_owned_buffer_live_and_real_copy_has_its_own_lease():
    ledger = UnifiedResourceLedger(Limits(max_total_memory_bytes=64))
    array = retained_array(ledger, "owned", (4,), float, lambda: np.arange(4, dtype=float))
    reference = weakref.ref(array)
    view = array[1:].reshape(3, 1)
    copied = retained_array(ledger, "copied", array.shape, array.dtype, array.copy)
    assert ledger.receipt()["live_memory_bytes"] == 64
    del array
    gc.collect()
    assert reference() is not None and ledger.receipt()["live_memory_bytes"] == 64
    del view
    gc.collect()
    assert reference() is None and ledger.receipt()["live_memory_bytes"] == 32
    del copied
    gc.collect()
    receipt = ledger.receipt()
    assert receipt["live_memory_bytes"] == 0
    assert receipt["total_reserved_memory_bytes"] == receipt["total_released_memory_bytes"] == 64


def test_group_deduplicates_views_and_waits_for_the_last_distinct_root():
    ledger = UnifiedResourceLedger()
    reservation = ledger.reserve("native_result_group", memory_bytes=96)
    first, second = np.ones(4), np.zeros(8)
    alias = first[1:]
    retain_reservation(reservation, {"value": first, "aliases": (alias, first), "second": second})
    del first, second
    gc.collect()
    assert ledger.receipt()["live_memory_bytes"] == 96
    del alias
    gc.collect()
    assert ledger.receipt()["live_memory_bytes"] == 0
    reservation.release()
    assert ledger.receipt()["total_released_memory_bytes"] == 96


def test_no_array_group_releases_immediately_and_factory_failure_does_not_leak():
    ledger = UnifiedResourceLedger()
    reservation = ArrayReservation(ledger, "scalar", (), float)
    retain_reservation(reservation, {"external": 1.})
    assert ledger.receipt()["live_memory_bytes"] == 0
    def failed(): raise KeyboardInterrupt
    with pytest.raises(KeyboardInterrupt): retained_array(ledger, "failed", (8,), float, failed)
    assert ledger.receipt()["live_memory_bytes"] == 0


def test_borrowed_view_cannot_be_registered_as_a_new_owned_allocation():
    ledger = UnifiedResourceLedger()
    external = np.ones(4)
    with pytest.raises(RuntimeError, match="new owned storage"):
        retained_array(ledger, "not_a_copy", (4,), float, lambda: external[:])
    assert ledger.receipt()["live_memory_bytes"] == 0


def test_factory_is_not_called_when_live_retained_data_exhausts_cap():
    ledger = UnifiedResourceLedger(Limits(max_total_memory_bytes=32))
    first = retained_array(ledger, "first", (4,), float)
    with pytest.raises(MemoryError):
        retained_array(ledger, "second", (1,), float, lambda: pytest.fail("allocate before reservation"))
    assert ledger.receipt()["live_memory_bytes"] == 32
    del first
    gc.collect()
    assert ledger.receipt()["live_memory_bytes"] == 0
