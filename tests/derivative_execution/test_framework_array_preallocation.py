# Copyright 2026 QuantumBridge Contributors.
# Licensed under the Apache License, Version 2.0.
"""Native framework snapshots, copies and selection reserve before allocation."""

import gc
from types import SimpleNamespace

import numpy as np
import pytest

from quantumbridge.execution import UnifiedExecutionLimits as Limits, UnifiedResourceLedger
from quantumbridge.execution.resource_context import ResourceScope
from quantumbridge.interfaces.native_host import NativeHostKernel
from quantumbridge.interfaces.qnode_autodiff import _FrameworkCallbacks


def callbacks(cap, count=4, indices=(0, 2)):
    ledger = UnifiedResourceLedger(Limits(max_total_memory_bytes=cap))
    plan = SimpleNamespace(ledger=ledger, recorder=SimpleNamespace(angles=[.2]*count))
    return _FrameworkCallbacks(plan, indices, "torch"), ledger


def test_fixed_snapshot_rejects_before_numpy_fromiter(monkeypatch):
    monkeypatch.setattr(np, "fromiter", lambda *a, **k: pytest.fail("unreserved fixed snapshot"))
    with pytest.raises(MemoryError): callbacks(31)


def test_unpack_copy_reserves_before_copying_fixed_storage():
    owner, ledger = callbacks(63)
    class CopyProbe(np.ndarray):
        def copy(self, *args, **kwargs): pytest.fail("unreserved fixed copy")
    owner.fixed = owner.fixed.view(CopyProbe)
    with pytest.raises(MemoryError): owner.unpack(np.array([.3, .4]))
    assert ledger.receipt()["live_memory_bytes"] == 32
    del owner
    gc.collect()
    assert ledger.receipt()["live_memory_bytes"] == 0


def test_fixed_and_noncontiguous_selected_slots_are_correct_and_independent():
    owner, ledger = callbacks(128)
    first = owner.unpack(np.array([.3, .4]))
    second = owner.unpack(np.array([.8, .9]))
    np.testing.assert_array_equal(first, [.3, .2, .4, .2])
    np.testing.assert_array_equal(second, [.8, .2, .9, .2])
    assert not np.shares_memory(first, second)
    assert not np.shares_memory(first, owner.fixed)
    assert ledger.receipt()["live_memory_bytes"] == 96
    del first, second, owner
    gc.collect()
    assert ledger.receipt()["live_memory_bytes"] == 0


def test_selected_jacobian_denies_before_column_copy(monkeypatch):
    owner, ledger = callbacks(63)
    external = np.ones((2, 4))
    owner.plan.jacobian = lambda *a, **k: (0., external, None)
    owner.plan.node = SimpleNamespace(gradient_kwargs={})
    monkeypatch.setattr(owner, "unpack", lambda value: value)
    monkeypatch.setattr(np, "empty", lambda *a, **k: pytest.fail("unreserved selected columns"))
    with pytest.raises(MemoryError): owner.selected_jacobian(np.ones(2))
    assert ledger.receipt()["live_memory_bytes"] == 32


def test_dtype_conversion_reserves_before_copy(monkeypatch):
    owner, ledger = callbacks(47)
    source = np.ones(2, dtype=np.float32)
    monkeypatch.setattr(np, "array", lambda *a, **k: pytest.fail("unreserved dtype conversion"))
    with pytest.raises(MemoryError): owner.real(source)
    assert ledger.receipt()["live_memory_bytes"] == 32


def test_native_seed_identity_reserves_before_eye(monkeypatch):
    kernel = object.__new__(NativeHostKernel)
    kernel.size = 16
    values = np.ones(16)
    ledger = UnifiedResourceLedger(Limits(max_total_memory_bytes=2047))
    monkeypatch.setattr(np, "eye", lambda *a, **k: pytest.fail("unreserved native seed identity"))
    with ResourceScope(ledger), pytest.raises(MemoryError): kernel.plan(values, derivative=True)
    assert ledger.receipt()["live_memory_bytes"] == 0


def test_mps_preflight_reads_bonds_without_materializing_tensor_copies(monkeypatch):
    from quantumbridge import Circuit, MatrixProductStateDevice
    from quantumbridge.information.matrix_product_state import MatrixProductState
    from quantumbridge.execution.derivative_planning import device_working_bytes
    initial = MatrixProductState.zero(100)
    device = MatrixProductStateDevice(initial_state=initial, max_bond_dim=2)
    def forbidden(self): pytest.fail("resource estimator copied MPS tensors before reservation")
    monkeypatch.setattr(MatrixProductState, "tensors", property(forbidden))
    estimate = device_working_bytes(device, Circuit(100))
    assert estimate == 12*100*2*16+128*4
