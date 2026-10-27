# Copyright 2026 QuantumBridge Contributors. Apache-2.0.
"""Scaled tangents retain existing array leases and reject before allocation."""

import gc

import numpy as np
import pytest

from quantumbridge.execution import UnifiedExecutionLimits as Limits, UnifiedResourceLedger as Ledger
from quantumbridge.execution import mps_arrays as arrays
from quantumbridge.execution.array_ownership import native_storage_bytes
from quantumbridge.execution.resource_context import ResourceScope
from quantumbridge.information import MatrixProductState
from quantumbridge.information.mps_tangent import MPSTangent
from quantumbridge.utils.math import gate_matrix


def test_complete_chain_copy_admission_precedes_the_first_allocation(monkeypatch):
    source = MatrixProductState.zero(100)
    ledger = Ledger(Limits(max_total_memory_bytes=source.tensor_bytes - 1))
    monkeypatch.setattr(np, "empty", lambda *a, **k: pytest.fail("Unadmitted tangent copy allocated"))
    with ResourceScope(ledger), pytest.raises(MemoryError):
        MPSTangent(source)
    assert ledger.receipt()["live_memory_bytes"] == 0


def test_owned_component_and_exported_view_keep_leases_until_their_owners_die():
    ledger = Ledger()
    with ResourceScope(ledger):
        source = MatrixProductState.zero(3)
        original = MPSTangent(source, 0.5j)
        total = MPSTangent.linear_combination([(1, original), (-0.2j, original)])
        changed = total.applied(gate_matrix("cx"), (2, 0))
        exported = changed.component_states
    assert ledger.receipt()["live_memory_bytes"] == native_storage_bytes((
        source._tensors, tuple(state._tensors for state, _ in original._components),
        tuple(state._tensors for state, _ in changed._components),
        tuple(state._tensors for state in exported)
    ))
    view = exported[0]._tensors[0][:, :, :]
    retained = native_storage_bytes(view)
    del source, original, total, changed, exported
    gc.collect()
    assert ledger.receipt()["live_memory_bytes"] == retained
    del view
    gc.collect()
    receipt = ledger.receipt()
    assert receipt["live_memory_bytes"] == 0
    assert receipt["total_reserved_memory_bytes"] == receipt["total_released_memory_bytes"]


def test_failed_nonlocal_svd_does_not_mutate_tangent_or_leak_released_arrays(monkeypatch):
    source = MatrixProductState.zero(5)
    original = MPSTangent(source, 0.5j)
    before = tuple(t.copy() for t in original._components[0][0]._tensors)
    ledger, errors = Ledger(), []
    def failed(*a, **k):
        raise np.linalg.LinAlgError("Injected tangent SVD failure")
    with monkeypatch.context() as patch:
        patch.setattr(np.linalg, "svd", failed)
        try:
            with ResourceScope(ledger):
                original.applied(gate_matrix("cx"), (0, 4))
        except np.linalg.LinAlgError as error:
            errors.append(error)
    # A live exception traceback is a real buffer owner, not a zero-memory case.
    assert ledger.receipt()["live_memory_bytes"] > 0
    errors.clear()
    gc.collect()
    assert ledger.receipt()["live_memory_bytes"] == 0
    for expected, actual in zip(before, original._components[0][0]._tensors):
        np.testing.assert_array_equal(actual, expected)
    assert original.inner(original) == pytest.approx(0.25)


def test_new_scale_buffer_is_admitted_before_abs_kernel(monkeypatch):
    source = np.ones((3, 4), complex)
    ledger = Ledger(Limits(max_total_memory_bytes=source.size * 8 - 1))
    monkeypatch.setattr(np, "absolute", lambda *a, **k: pytest.fail("Scale kernel preceded buffer admission"))
    with ResourceScope(ledger), pytest.raises(MemoryError):
        arrays.component_scale(source)
    assert ledger.receipt()["live_memory_bytes"] == 0
