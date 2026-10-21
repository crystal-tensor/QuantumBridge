# Copyright 2026 QuantumBridge Contributors.
# Licensed under the Apache License, Version 2.0.
"""Known native configuration arrays cannot copy outside the active account."""

import gc
from types import SimpleNamespace

import numpy as np
import pytest

from quantumbridge import DensityMatrixDevice, PauliZ
from quantumbridge.execution import UnifiedExecutionLimits as Limits, UnifiedResourceLedger as Ledger
from quantumbridge.execution.resource_context import ResourceScope
from quantumbridge.interfaces.native_host import NativeHostKernel
from quantumbridge.qml import QNode, Tape


def test_tape_metadata_real_copy_rejects_before_ndarray_deepcopy():
    calls = []
    class CopyProbe(np.ndarray):
        def __deepcopy__(self, memo):
            calls.append("deepcopy")
            return np.asarray(self).copy()
    source = Tape(1)
    source.circuit.metadata["native_numeric_payload"] = np.ones(8).view(CopyProbe)
    ledger = Ledger(Limits(max_total_memory_bytes=63))
    with ResourceScope(ledger), pytest.raises(MemoryError): source.copy()
    assert calls == [], "source array copied before its 64-byte budget was checked"
    assert ledger.receipt()["live_memory_bytes"] == 0


def test_host_device_copy_rejects_before_initial_state_ndarray_deepcopy():
    calls = []
    class CopyProbe(np.ndarray):
        def __deepcopy__(self, memo):
            calls.append("deepcopy")
            return np.asarray(self).copy()
    initial = (np.eye(2, dtype=complex)/2).view(CopyProbe)
    source = Tape(1)
    source.set_output(source.expval(PauliZ(0)))
    kernel = object.__new__(NativeHostKernel)
    kernel.size, kernel.parameters, kernel.coefficients = 0, (), [()]
    kernel.source, kernel.program = source, None
    kernel.node = QNode(lambda t: t.expval(PauliZ(0)), 1,
        device=DensityMatrixDevice(initial_state=initial))
    ledger = Ledger(Limits(max_total_memory_bytes=63))
    with ResourceScope(ledger), pytest.raises(MemoryError): kernel.plan(np.empty(0))
    assert calls == [], "initial-state configuration copied before checking its 64 bytes"
    assert ledger.receipt()["live_memory_bytes"] == 0


def test_tape_copy_reuses_one_destination_for_repeated_source_references():
    source = Tape(1)
    array = np.arange(8, dtype=float)
    source.circuit.metadata = {"first": array, "again": array}
    ledger = Ledger(Limits(max_total_memory_bytes=64))
    with ResourceScope(ledger):
        copied = source.copy()
        first = copied.circuit.metadata["first"]
        assert first is copied.circuit.metadata["again"]
        assert not np.shares_memory(first, array)
        assert ledger.receipt()["live_memory_bytes"] == 64
    peer = SimpleNamespace(storage=first)
    del first, copied
    gc.collect()
    assert ledger.receipt()["live_memory_bytes"] == 64
    np.testing.assert_array_equal(peer.storage, array)
    del peer
    gc.collect()
    assert ledger.receipt()["live_memory_bytes"] == 0


def test_distinct_input_views_become_real_independent_copies_not_false_aliases():
    source = Tape(1)
    array = np.arange(12, dtype=float).reshape(3, 4)
    source.circuit.metadata = {"first": array, "again": array, "transpose": array.T}
    ledger = Ledger(Limits(max_total_memory_bytes=192))
    with ResourceScope(ledger):
        copied = source.copy()
        metadata = copied.circuit.metadata
        assert metadata["first"] is metadata["again"]
        assert not np.shares_memory(metadata["first"], metadata["transpose"])
        np.testing.assert_array_equal(metadata["transpose"], array.T)
        assert ledger.receipt()["live_memory_bytes"] == 192
    del copied, metadata
    gc.collect()
    assert ledger.receipt()["live_memory_bytes"] == 0


def test_subclass_copy_behavior_is_preserved_and_workspace_not_claimed_known():
    calls = []
    class CopyProbe(np.ndarray):
        def __deepcopy__(self, memo):
            calls.append("custom")
            return np.asarray(self).copy()
    source = Tape(1)
    source.circuit.metadata["data"] = np.ones(4).view(CopyProbe)
    ledger = Ledger(Limits(max_total_memory_bytes=32))
    with ResourceScope(ledger):
        copied = source.copy()
        assert calls == ["custom"]
        assert ledger.receipt()["live_memory_bytes"] == 32
        assert "ndarray_subclass_copy_workspace" in ledger.receipt()["unavailable"]
    del copied
    gc.collect()
    assert ledger.receipt()["live_memory_bytes"] == 0


def test_partial_copy_failure_releases_after_error_collection_and_recovers():
    source = Tape(1)
    source.circuit.metadata = {"first": np.ones(8), "second": np.zeros(8)}
    ledger = Ledger(Limits(max_total_memory_bytes=64))
    with ResourceScope(ledger):
        with pytest.raises(MemoryError) as failure: source.copy()
        assert ledger.receipt()["live_memory_bytes"] == 64
        del failure
        gc.collect()
        assert ledger.receipt()["live_memory_bytes"] == 0
        source.circuit.metadata.pop("second")
        copied = source.copy()
        assert ledger.receipt()["live_memory_bytes"] == 64
    del copied
    gc.collect()
    assert ledger.receipt()["live_memory_bytes"] == 0
