# Copyright 2026 QuantumBridge Contributors.
# Licensed under the Apache License, Version 2.0.
"""Strided tree copies reserve before allocation and retain their real roots."""

import gc
import weakref

import numpy as np
import pytest

from quantumbridge.diff.trace import flatten_tree, unflatten_tree
from quantumbridge.execution import UnifiedExecutionLimits as Limits, UnifiedResourceLedger as Ledger
from quantumbridge.execution.resource_context import ResourceScope


def strided_source():
    return np.arange(60., dtype=float).reshape(5, 3, 4)[:, ::2, :]


def test_flatten_rejects_before_copying_noncontiguous_leaves(monkeypatch):
    source = strided_source()
    ledger = Ledger(Limits(max_total_memory_bytes=source.size*8-1))
    monkeypatch.setattr(np, "concatenate", lambda *a, **k: pytest.fail("unreserved tree concatenation"))
    with ResourceScope(ledger), pytest.raises(MemoryError):
        flatten_tree(source)
    assert ledger.receipt()["live_memory_bytes"] == 0


def test_unflatten_rejects_before_a_noncontiguous_reshape_copy():
    source = strided_source()
    spec = ("leaf", (5,), 0, 5)
    assert not np.shares_memory(source, source.reshape(5, 8))
    ledger = Ledger(Limits(max_total_memory_bytes=source.nbytes-1))
    with ResourceScope(ledger), pytest.raises(MemoryError):
        unflatten_tree(source, spec, (8,))
    assert ledger.receipt()["live_memory_bytes"] == 0


@pytest.mark.parametrize("source", [strided_source(), strided_source()[::-1],
    np.asfortranarray(np.arange(12.).reshape(3, 4)), np.arange(5, dtype=np.int32)])
def test_flatten_has_one_owned_destination_no_leaf_copy_or_concatenation(source, monkeypatch):
    expected = source.astype(float).reshape(-1).copy()
    ledger = Ledger(Limits(max_total_memory_bytes=expected.nbytes))
    monkeypatch.setattr(np, "concatenate", lambda *a, **k: pytest.fail("extra concatenate allocation"))
    with ResourceScope(ledger):
        flat, spec = flatten_tree(source)
    np.testing.assert_array_equal(flat, expected)
    assert spec == ("leaf", source.shape, 0, source.size)
    assert flat.flags.owndata and not np.shares_memory(source, flat)
    assert ledger.receipt()["live_memory_bytes"] == flat.nbytes
    view = flat[::2]
    reference = weakref.ref(flat)
    del flat
    gc.collect()
    assert reference() is not None and ledger.receipt()["live_memory_bytes"] == expected.nbytes
    del view
    gc.collect()
    assert reference() is None and ledger.receipt()["live_memory_bytes"] == 0


def test_nested_flatten_empty_and_reconstruction_preserve_layout():
    source = {"vector": np.arange(6.).reshape(2, 3).T, "other": [2., (), np.empty((0, 2))]}
    ledger = Ledger()
    with ResourceScope(ledger):
        flat, spec = flatten_tree(source)
        restored = unflatten_tree(flat, spec)
    np.testing.assert_array_equal(restored["vector"], source["vector"])
    assert restored["other"][0] == 2. and restored["other"][1] == ()
    assert restored["other"][2].shape == (0, 2)
    assert np.shares_memory(flat, restored["vector"])
    assert ledger.receipt()["live_memory_bytes"] == 56
    del restored, flat
    gc.collect()
    assert ledger.receipt()["live_memory_bytes"] == 0


def test_unflatten_real_copy_retains_one_lease_but_view_only_reshape_is_free():
    source, ledger = strided_source(), Ledger()
    with ResourceScope(ledger):
        copied = unflatten_tree(source, ("leaf", (5,), 0, 5), (8,))
        view = unflatten_tree(source, ("leaf", (5,), 0, 5), (2, 4))
    np.testing.assert_array_equal(copied, source.reshape(5, 8))
    assert not np.shares_memory(copied, source) and np.shares_memory(view, source)
    assert ledger.receipt()["live_memory_bytes"] == source.nbytes
    nested = copied[:, ::2]
    del copied
    gc.collect()
    assert ledger.receipt()["live_memory_bytes"] == source.nbytes
    del nested
    gc.collect()
    assert ledger.receipt()["live_memory_bytes"] == 0


def test_foreign_array_conversion_is_not_executed_under_a_native_budget():
    calls = []
    class Foreign:
        def __array__(self, *a, **k):
            calls.append("array")
            return np.ones(16)
    from quantumbridge.core.classical import UnsupportedFeature
    ledger = Ledger()
    with ResourceScope(ledger), pytest.raises(UnsupportedFeature):
        flatten_tree(Foreign())
    assert calls == [] and ledger.receipt()["live_memory_bytes"] == 0


def test_direction_tree_denies_before_cast_or_concatenate(monkeypatch):
    from types import SimpleNamespace
    from quantumbridge.execution.derivative_planning import _direction
    source = np.arange(8., dtype=np.float32)[::-1]
    ledger = Ledger(Limits(max_total_memory_bytes=63))
    request = SimpleNamespace(derivative_kind="jvp", tangent=source)
    monkeypatch.setattr(np, "concatenate", lambda *a, **k: pytest.fail("unreserved direction concatenation"))
    with ResourceScope(ledger), pytest.raises(MemoryError):
        _direction(request, (source,), source.size)


def test_ordinary_host_mapping_denies_before_matmul():
    from types import SimpleNamespace
    from quantumbridge.interfaces.jax_autodiff import JAXBridgeLimits
    from quantumbridge.interfaces.native_host import NativeHostKernel
    calls = []
    class Matrix(np.ndarray):
        def __matmul__(self, other):
            calls.append("mapped")
            return np.asarray(self) @ other
    matrix = np.eye(2).view(Matrix)
    recorder = SimpleNamespace(parameters=(0, 1), native_values=lambda: np.zeros(2),
        classical_jacobian=lambda size: np.eye(2))
    plan = SimpleNamespace(recorder=recorder, metadata={},
        jacobian=lambda *a, **k: (np.ones(2), matrix, ("leaf", (2,), 0, 2)))
    kernel = object.__new__(NativeHostKernel)
    kernel.size, kernel.output_size, kernel.spec = 2, 2, ("leaf", (2,), 0, 2)
    kernel.limits = JAXBridgeLimits()
    kernel.interface = "jax"
    kernel.node = SimpleNamespace(gradient_kwargs={})
    kernel.plan = lambda *a, **k: plan
    kernel._shot_work = lambda plan: (0, 0)
    ledger = Ledger(Limits(max_total_memory_bytes=31))
    with ResourceScope(ledger), pytest.raises(MemoryError):
        kernel.run(np.ones(2), True)
    assert calls == []


def test_foreign_tree_reflection_and_container_hooks_are_rejected_before_dispatch():
    from quantumbridge.core.classical import UnsupportedFeature
    calls = []
    class Foreign:
        def __getattribute__(self, key):
            calls.append(key)
            return object.__getattribute__(self, key)
    class Container(list):
        def __iter__(self):
            calls.append("iter")
            return super().__iter__()
    ledger = Ledger()
    for source in (Foreign(), Container([1.])):
        with ResourceScope(ledger), pytest.raises(UnsupportedFeature):
            flatten_tree(source)
    assert calls == [] and ledger.receipt()["live_memory_bytes"] == 0


def test_empty_tree_and_zero_dimensional_numeric_leaf_have_exact_storage():
    ledger = Ledger()
    with ResourceScope(ledger):
        empty, empty_spec = flatten_tree(())
        scalar, scalar_spec = flatten_tree(np.float32(.25))
    assert empty.shape == (0,) and empty_spec == ("tuple", ())
    assert scalar_spec == ("leaf", (), 0, 1)
    assert unflatten_tree(scalar, scalar_spec) == .25
    assert ledger.receipt()["live_memory_bytes"] == 8
    del scalar
    assert ledger.receipt()["live_memory_bytes"] == 0


def test_advanced_column_selection_is_an_independently_owned_root():
    from types import SimpleNamespace
    from quantumbridge.execution.device_derivatives import _input_tree
    source, ledger = np.arange(8.).reshape(2, 4), Ledger()
    prepared = SimpleNamespace(output_spec=("leaf", (2,), 0, 2), layout=[((2,), [3, 1])], single=True)
    with ResourceScope(ledger):
        selected = _input_tree(source, prepared)
    np.testing.assert_array_equal(selected, source[:, [3, 1]])
    assert not np.shares_memory(source, selected)
    assert ledger.receipt()["live_memory_bytes"] == 32
    view = selected[:, 1:]
    del selected
    gc.collect()
    assert ledger.receipt()["live_memory_bytes"] == 32
    del view
    gc.collect()
    assert ledger.receipt()["live_memory_bytes"] == 0


def test_advanced_column_selection_denies_before_index_copy():
    from types import SimpleNamespace
    from quantumbridge.execution.device_derivatives import _input_tree
    calls = []
    class Matrix(np.ndarray):
        def __getitem__(self, key):
            if isinstance(key, tuple) and isinstance(key[1], list): calls.append("advanced")
            return super().__getitem__(key)
    source = np.arange(8.).reshape(2, 4).view(Matrix)
    prepared = SimpleNamespace(output_spec=("leaf", (2,), 0, 2), layout=[((2,), [3, 1])], single=True)
    ledger = Ledger(Limits(max_total_memory_bytes=31))
    with ResourceScope(ledger), pytest.raises(MemoryError):
        _input_tree(source, prepared)
    assert calls == []


def test_column_selection_preserves_repeated_negative_and_empty_columns():
    from quantumbridge.execution.array_ownership import select_columns
    source, ledger = np.arange(8.).reshape(2, 4), Ledger()
    with ResourceScope(ledger):
        selected = select_columns(source, [-1, 1, 1])
        empty = select_columns(source, [])
        view = select_columns(source, slice(None, None, -1))
    np.testing.assert_array_equal(selected, source[:, [-1, 1, 1]])
    assert selected.flags.owndata and not np.shares_memory(selected, source)
    assert empty.shape == (2, 0) and np.shares_memory(view, source)
    assert ledger.receipt()["live_memory_bytes"] == 48
    del selected
    assert ledger.receipt()["live_memory_bytes"] == 0


@pytest.mark.parametrize("indices, error", [(True, "unsupported"), ([True], "invalid"),
    ([1.2], "invalid"), ([4], "bounds"), ([-5], "bounds")])
def test_invalid_selected_columns_do_not_allocate(indices, error, monkeypatch):
    from quantumbridge.core.classical import UnsupportedFeature
    from quantumbridge.execution.array_ownership import select_columns
    source, ledger = np.ones((2, 4)), Ledger()
    monkeypatch.setattr(np, "empty", lambda *a, **k: pytest.fail("invalid selection allocated"))
    expected = {"unsupported": UnsupportedFeature, "invalid": ValueError, "bounds": IndexError}[error]
    with ResourceScope(ledger), pytest.raises(expected):
        select_columns(source, indices)
    with ResourceScope(ledger), pytest.raises(ValueError):
        select_columns(source[0], [])
    assert ledger.receipt()["live_memory_bytes"] == 0


def test_legacy_view_only_shape_check_and_invalid_target(monkeypatch):
    import warnings
    from quantumbridge.diff import trace
    monkeypatch.setattr(trace, "_NO_COPY_RESHAPE", False)
    source, ledger = strided_source(), Ledger()
    with warnings.catch_warnings(), ResourceScope(ledger):
        warnings.filterwarnings("ignore", message="Setting the shape on a NumPy array", category=DeprecationWarning)
        copied = unflatten_tree(source, ("leaf", (5,), 0, 5), (8,))
        view = unflatten_tree(source, ("leaf", (5,), 0, 5), (2, 4))
        with pytest.raises(ValueError):
            unflatten_tree(source, ("leaf", (5,), 0, 5), (9,))
    assert not np.shares_memory(copied, source) and np.shares_memory(view, source)
    assert ledger.receipt()["live_memory_bytes"] == source.nbytes
    del copied
    gc.collect()
    assert ledger.receipt()["live_memory_bytes"] == 0
