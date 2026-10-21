# Copyright 2026 QuantumBridge Contributors.
# Licensed under the Apache License, Version 2.0.
"""Defensive Result buffers have independent storage and real owner lifetimes."""

import gc
import weakref

import numpy as np
import pytest

from quantumbridge.core.classical import UnsupportedFeature
from quantumbridge.execution import UnifiedExecutionLimits as Limits, UnifiedResourceLedger as Ledger
from quantumbridge.execution.array_ownership import retained_array, storage_ledger
from quantumbridge.execution.resource_context import ResourceScope
from quantumbridge.providers.job import Job
from quantumbridge.results.result import Result


@pytest.fixture(params=[("state", "statevector", (4,)), ("density", "density_matrix", (4, 4))])
def payload(request):
    field, accessor, shape = request.param
    data = np.arange(np.prod(shape), dtype=float).reshape(shape).astype(complex)
    data += 1j * data[::-1]
    return field, accessor, data


def test_accessor_rejects_before_copy_allocation(payload, monkeypatch):
    field, accessor, data = payload
    result = Result(**{field: data})
    monkeypatch.setattr(np, "empty", lambda *a, **k: pytest.fail("Result copied before admission"))
    ledger = Ledger(Limits(max_total_memory_bytes=data.nbytes - 1))
    with ResourceScope(ledger), pytest.raises(MemoryError):
        getattr(result, accessor)()
    assert ledger.receipt()["live_memory_bytes"] == 0


def test_repeated_copies_deny_then_recover_after_last_view_dies(payload):
    field, accessor, data = payload
    result = Result(**{field: data})
    ledger = Ledger(Limits(max_total_memory_bytes=2 * data.nbytes))
    with ResourceScope(ledger):
        first, second = getattr(result, accessor)(), getattr(result, accessor)()
        np.testing.assert_array_equal(first, data)
        np.testing.assert_array_equal(second, data)
        assert not np.shares_memory(first, second)
        assert ledger.receipt()["live_memory_bytes"] == 2 * data.nbytes
        view = first.reshape(-1)[::2]
        del first
        gc.collect()
        with pytest.raises(MemoryError):getattr(result, accessor)()
        del view
        gc.collect()
        recovered = getattr(result, accessor)()
        assert ledger.receipt()["live_memory_bytes"] == 2 * data.nbytes
    del second, recovered
    gc.collect()
    assert ledger.receipt()["live_memory_bytes"] == 0


def test_copy_outside_scope_follows_source_storage_account(payload):
    field, accessor, data = payload
    ledger = Ledger(Limits(max_total_memory_bytes=2 * data.nbytes))
    source = retained_array(ledger, "source", data.shape, data.dtype)
    np.copyto(source, data)
    result = Result(**{field: source})
    copied = getattr(result, accessor)()
    assert storage_ledger(copied) is ledger
    assert ledger.receipt()["live_memory_bytes"] == 2 * data.nbytes
    with pytest.raises(MemoryError):getattr(result, accessor)()
    del copied
    gc.collect()
    recovered = getattr(result, accessor)()
    np.testing.assert_array_equal(recovered, data)
    del source, result, recovered
    gc.collect()
    assert ledger.receipt()["live_memory_bytes"] == 0


def test_explicit_request_copies_into_its_own_account(payload):
    field, accessor, data = payload
    source_ledger, destination_ledger = Ledger(), Ledger()
    source = retained_array(source_ledger, "source", data.shape, data.dtype)
    np.copyto(source, data)
    result = Result(**{field: source})
    with ResourceScope(destination_ledger):copied = getattr(result, accessor)()
    assert storage_ledger(copied) is destination_ledger
    assert source_ledger.receipt()["live_memory_bytes"] == data.nbytes
    assert destination_ledger.receipt()["live_memory_bytes"] == data.nbytes
    del result, source
    gc.collect()
    assert source_ledger.receipt()["live_memory_bytes"] == 0
    np.testing.assert_array_equal(copied, data)
    del copied
    gc.collect()
    assert destination_ledger.receipt()["live_memory_bytes"] == 0


def test_escaped_job_result_view_survives_all_producers(payload):
    field, accessor, data = payload
    ledger = Ledger()
    source = retained_array(ledger, "job_source", data.shape, data.dtype)
    np.copyto(source, data)
    result = Result(**{field: source})
    job = Job("local-result-resource-test", result=result)
    result_reference, job_reference = weakref.ref(result), weakref.ref(job)
    with ResourceScope(ledger):copied = getattr(job.result(), accessor)()
    escaped = copied.reshape(-1)[1:]
    del copied, source, result, job
    gc.collect()
    assert result_reference() is job_reference() is None
    assert ledger.receipt()["live_memory_bytes"] == data.nbytes
    np.testing.assert_array_equal(escaped, data.reshape(-1)[1:])
    del escaped
    gc.collect()
    receipt = ledger.receipt()
    assert receipt["live_memory_bytes"] == 0
    assert receipt["total_reserved_memory_bytes"] == receipt["total_released_memory_bytes"]


def test_strided_result_copy_is_independent_and_preserves_complex_dtype(payload):
    field, accessor, data = payload
    source = data[::-1]
    result = Result(**{field: source})
    ledger = Ledger()
    with ResourceScope(ledger):copied = getattr(result, accessor)()
    assert copied.dtype == data.dtype
    np.testing.assert_array_equal(copied, source)
    copied.flat[0] = 123 + 456j
    assert source.flat[0] != copied.flat[0]
    assert ledger.receipt()["live_memory_bytes"] == copied.nbytes


def test_foreign_copy_protocol_rejected_before_dispatch(payload):
    field, accessor, _ = payload
    class Foreign:
        def copy(self):pytest.fail("Opaque Result copy protocol dispatched")
        def __array__(self, *a, **k):pytest.fail("Opaque Result array protocol dispatched")
    result = Result(**{field: Foreign()})
    with ResourceScope(Ledger()), pytest.raises(UnsupportedFeature):getattr(result, accessor)()


def test_array_subclass_copy_hook_not_dispatched(payload):
    field, accessor, data = payload
    class Subclass(np.ndarray):
        def copy(self, *a, **k):pytest.fail("Result ndarray subclass hook dispatched")
    result = Result(**{field: data.view(Subclass)})
    ledger = Ledger()
    with ResourceScope(ledger):copied = getattr(result, accessor)()
    assert type(copied) is np.ndarray
    np.testing.assert_array_equal(copied, data)
    assert ledger.receipt()["live_memory_bytes"] == data.nbytes


def test_failed_fill_releases_copy_ticket_and_next_access_recovers(payload, monkeypatch):
    field, accessor, data = payload
    result, ledger = Result(**{field: data}), Ledger()
    def failure(*a, **k):raise RuntimeError("injected Result fill failure")
    with monkeypatch.context() as patch:
        patch.setattr(np, "copyto", failure)
        with ResourceScope(ledger), pytest.raises(RuntimeError, match="injected Result"):
            getattr(result, accessor)()
    gc.collect()
    assert ledger.receipt()["live_memory_bytes"] == 0
    with ResourceScope(ledger):copied = getattr(result, accessor)()
    np.testing.assert_array_equal(copied, data)
    assert ledger.receipt()["live_memory_bytes"] == data.nbytes


@pytest.mark.parametrize("accessor", ["statevector", "density_matrix"])
def test_absent_result_remains_none_without_reservation(accessor):
    ledger = Ledger(Limits(max_total_memory_bytes=0))
    with ResourceScope(ledger):assert getattr(Result(), accessor)() is None
    assert ledger.receipt()["total_reserved_memory_bytes"] == 0
