# Copyright 2026 QuantumBridge Contributors.
# Licensed under the Apache License, Version 2.0.
"""Reject opaque copy protocols before their allocators or access hooks run."""

import gc
from dataclasses import dataclass

import numpy as np
import pytest

from quantumbridge.core.classical import UnsupportedFeature
from quantumbridge.execution import UnifiedExecutionLimits as Limits
from quantumbridge.execution.persistent_storage import PersistentStoragePool


@pytest.mark.parametrize("protocol", ["slots", "reduce", "dict", "list", "getattribute"])
def test_opaque_protocol_rejects_before_dispatch(protocol):
    calls = []
    class Slotted:
        __slots__ = ("array",)
        def __init__(self): self.array = np.ones(8)
    class Reduced:
        __slots__ = ()
        def __reduce_ex__(self, version):
            calls.append("reduce")
            return np.ones, (8,)
    class Dictionary(dict):
        def __deepcopy__(self, memo):
            calls.append("dict deepcopy")
            return {"hidden": np.ones(8)}
    class Sequence(list):
        def __deepcopy__(self, memo):
            calls.append("list deepcopy")
            return [np.ones(8)]
    class AccessHook:
        def __getattribute__(self, name):
            calls.append("getattribute")
            return object.__getattribute__(self, name)
    item = {"slots": Slotted, "reduce": Reduced, "dict": Dictionary,
            "list": Sequence, "getattribute": AccessHook}[protocol]()
    pool = PersistentStoragePool(Limits(max_total_memory_bytes=1))
    with pytest.raises(UnsupportedFeature): pool.freeze(item)
    assert calls == [], "an opaque object hook ran before rejection"
    assert pool.receipt()["persistent_owned_bytes"] == 0


@pytest.mark.parametrize("capture", ["closure", "default", "bound_method"])
def test_callable_native_storage_cannot_hide_in_unexamined_capture(capture):
    array = np.ones(8)
    if capture == "closure":
        def callback(): return array
    elif capture == "default":
        def callback(value=array): return value
    else:
        class Owner:
            def __init__(self): self.array = array
            def callback(self): return self.array
        callback = Owner().callback
    pool = PersistentStoragePool(Limits(max_total_memory_bytes=1))
    with pytest.raises(UnsupportedFeature): pool.freeze(callback)
    assert pool.receipt()["persistent_owned_bytes"] == 0


def test_foreign_dataclass_is_not_assumed_safe_from_its_field_names():
    @dataclass
    class Configuration:
        array: np.ndarray
    pool = PersistentStoragePool()
    with pytest.raises(UnsupportedFeature): pool.freeze(Configuration(np.ones(8)))
    assert pool.receipt()["persistent_owned_bytes"] == 0


def test_exact_recursive_containers_preserve_cycles_and_shared_array_identity():
    array = np.arange(8, dtype=float)
    root = {"array": array, "again": array}
    root["cycle"] = root
    pool = PersistentStoragePool(Limits(max_total_memory_bytes=64))
    owner = pool.freeze(root)
    assert owner.payload["cycle"] is owner.payload
    assert owner.payload["array"] is owner.payload["again"]
    assert not np.shares_memory(owner.payload["array"], array)
    assert pool.receipt()["persistent_owned_bytes"] == 64
    del owner
    gc.collect()
    assert pool.receipt()["persistent_owned_bytes"] == 0


def test_strict_native_copy_does_not_reenter_operator_constructor(monkeypatch):
    from quantumbridge.information import Operator
    source = Operator(np.eye(2, dtype=complex))
    def constructor(*args, **kwargs):
        pytest.fail("snapshot copy reentered a constructor instead of copying fields")
    monkeypatch.setattr(Operator, "__init__", constructor)
    pool = PersistentStoragePool(Limits(max_total_memory_bytes=64))
    owner = pool.freeze(source)
    np.testing.assert_array_equal(owner.payload.data, source.data)
    assert not np.shares_memory(owner.payload.data, source.data)
    assert pool.receipt()["persistent_owned_bytes"] == 64


def test_foreign_metaclass_access_and_equality_hooks_are_not_dispatched():
    calls = []
    class Meta(type):
        def __eq__(self, other):
            calls.append("equality")
            return type.__eq__(self, other)
        def __getattribute__(self, name):
            calls.append("class lookup")
            return type.__getattribute__(self, name)
        __hash__ = type.__hash__
    class Foreign(metaclass=Meta): pass
    value = Foreign()
    calls.clear()
    with pytest.raises(UnsupportedFeature): PersistentStoragePool().freeze(value)
    assert calls == []


def test_foreign_class_cannot_enter_native_copy_by_module_label_alone():
    class Foreign:
        __module__ = "quantumbridge.information.operator"
        def __init__(self): self.array = np.ones(8)
    with pytest.raises(UnsupportedFeature): PersistentStoragePool().freeze(Foreign())


def test_slice_fields_are_walked_before_deepcopy_of_the_builtin_container():
    array = np.ones(8)
    pool = PersistentStoragePool(Limits(max_total_memory_bytes=63))
    with pytest.raises(MemoryError): pool.freeze(slice(array, None, None))
    assert pool.receipt()["persistent_owned_bytes"] == 0
    pool = PersistentStoragePool(Limits(max_total_memory_bytes=64))
    owner = pool.freeze(slice(array, None, None))
    assert not np.shares_memory(owner.payload.start, array)
    assert not owner.payload.start.flags.writeable
    assert pool.receipt()["persistent_owned_bytes"] == 64


@pytest.mark.parametrize("kind", ["tensor", "variable"])
def test_tensorflow_capture_is_rejected_before_framework_copy(kind):
    tf = pytest.importorskip("tensorflow")
    value = tf.constant([.2], tf.float64) if kind == "tensor" else tf.Variable([.2], dtype=tf.float64)
    pool = PersistentStoragePool()
    with pytest.raises(UnsupportedFeature): pool.freeze(value)
    assert pool.receipt()["persistent_owned_bytes"] == 0


def test_native_fields_preserve_cycles_without_constructor_or_reduce_dispatch():
    from quantumbridge.core import Circuit
    circuit = Circuit(1)
    circuit.metadata["self"] = circuit
    circuit.metadata["array"] = np.ones(8)
    pool = PersistentStoragePool(Limits(max_total_memory_bytes=64))
    owner = pool.freeze(circuit)
    assert owner.payload.metadata["self"] is owner.payload
    assert owner.payload is not circuit
    assert pool.receipt()["persistent_owned_bytes"] == 64
    del owner
    gc.collect()
    assert pool.receipt()["persistent_owned_bytes"] == 0


def test_immutable_function_capture_is_borrowed_not_executed_or_duplicated():
    coefficient = np.float64(.7)
    def callback(value): return coefficient*value
    pool = PersistentStoragePool()
    owner = pool.freeze(callback)
    assert owner.payload is callback
    assert owner.payload(2) == 1.4
    assert pool.receipt()["persistent_owned_bytes"] == 0
    assert "callable_module_state" in pool.receipt()["ledger"]["unavailable"]
