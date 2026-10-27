# Copyright 2026 QuantumBridge Contributors. Apache-2.0.
"""Binding storage admission and escaped-view leases, not process-RSS claims."""

import gc

import numpy as np
import pytest

from quantumbridge import Circuit
from quantumbridge.execution.derivative_status import ResourceLimitError
from quantumbridge.execution.resource_context import ResourceScope
from quantumbridge.execution.resource_ledger import UnifiedResourceLedger
from quantumbridge.execution.resource_limits import UnifiedExecutionLimits
from quantumbridge.primitives import BindingsArray


def ledger(memory, parent=None, **limits):
    return UnifiedResourceLedger(UnifiedExecutionLimits(max_total_memory_bytes=memory, **limits), parent)


def test_exact_binding_payload_and_escaped_views_keep_their_leases():
    resources = ledger(64)
    with ResourceScope(resources):
        array = BindingsArray({"a": [[.1], [.2], [.3], [.4]]})
        output = array.as_array()
        escaped_input = array.data[("a",)][1:]
        escaped_output = memoryview(output)
        assert resources.receipt()["live_memory_bytes"] == 64
    del array, output
    gc.collect()
    assert resources.receipt()["live_memory_bytes"] == 64
    assert escaped_input[0, 0] == .2 and escaped_output[2, 0] == .3
    del escaped_input
    gc.collect()
    assert resources.receipt()["live_memory_bytes"] == 32
    del escaped_output
    gc.collect()
    assert resources.receipt()["live_memory_bytes"] == 0


def test_as_array_one_below_denies_before_destination_allocation(monkeypatch):
    resources = ledger(63)
    with ResourceScope(resources):
        array = BindingsArray({"a": [[.1], [.2], [.3], [.4]]})
        calls = []
        original = np.empty

        def observed(*args, **kwargs):
            calls.append(args)
            return original(*args, **kwargs)

        monkeypatch.setattr(np, "empty", observed)
        with pytest.raises(ResourceLimitError):
            array.as_array()
        assert calls == []
        assert resources.receipt()["live_memory_bytes"] == 32
    del array
    gc.collect()
    assert resources.receipt()["live_memory_bytes"] == 0


def test_all_parameter_groups_are_reserved_before_the_first_conversion(monkeypatch):
    resources = ledger(31)
    calls = []
    original = np.empty

    def observed(*args, **kwargs):
        calls.append(args)
        return original(*args, **kwargs)

    monkeypatch.setattr(np, "empty", observed)
    with ResourceScope(resources), pytest.raises(ResourceLimitError):
        BindingsArray({"a": [.1, .2], "b": [.3, .4]})
    assert calls == []
    assert resources.receipt()["live_memory_bytes"] == 0


def test_child_binding_leases_obey_the_parent_budget():
    parent = ledger(32)
    child = ledger(64, parent=parent)
    with ResourceScope(child):
        array = BindingsArray({"a": [.1, .2, .3, .4]})
        with pytest.raises(ResourceLimitError):
            array.as_array()
        assert parent.receipt()["live_memory_bytes"] == child.receipt()["live_memory_bytes"] == 32
    del array
    gc.collect()
    assert parent.receipt()["live_memory_bytes"] == child.receipt()["live_memory_bytes"] == 0


def test_noncontiguous_reshape_owns_a_prior_copy_lease():
    resources = ledger(160)
    values = np.arange(12.).reshape(2, 3, 2)
    with ResourceScope(resources):
        array = BindingsArray({("a", "b"): values})
        selected = array[:, ::2]
        flattened = selected.reshape(4)
        assert resources.receipt()["live_memory_bytes"] == 64
        np.testing.assert_array_equal(flattened.as_array(), values[:, ::2].reshape(4, 2))
        view = flattened.data[("a", "b")][:1]
    del flattened, selected, array
    gc.collect()
    assert resources.receipt()["live_memory_bytes"] == 64
    assert view.tolist() == [[0., 1.]]
    del view
    gc.collect()
    assert resources.receipt()["live_memory_bytes"] == 0


def test_eager_circuit_binding_is_bounded_before_object_array_allocation(monkeypatch):
    resources = ledger(0, max_total_tapes=2)
    array = BindingsArray(shape=(3,))
    calls = []
    original = np.empty

    def observed(*args, **kwargs):
        calls.append(args)
        return original(*args, **kwargs)

    monkeypatch.setattr(np, "empty", observed)
    with ResourceScope(resources), pytest.raises(ResourceLimitError, match="binding_circuits"):
        array.bind_all(Circuit(1))
    assert calls == [] and resources.receipt()["live_memory_bytes"] == 0


def test_parameterless_bind_checks_coordinates_even_without_value_buffers():
    array = BindingsArray(shape=(2, 0))
    with pytest.raises(IndexError):
        array.bind(Circuit(1), (1, 0))


def test_huge_broadcast_input_is_denied_before_value_iteration_or_copy(monkeypatch):
    huge = np.broadcast_to(np.array(.1), (2**40, 1))
    calls = []
    original = np.empty

    def observed(*args, **kwargs):
        calls.append(args)
        return original(*args, **kwargs)

    monkeypatch.setattr(np, "empty", observed)
    with pytest.raises(ResourceLimitError):
        BindingsArray({"a": huge})
    assert calls == []


def test_noncontiguous_multiple_group_reshape_reserves_before_allocation(monkeypatch):
    values = np.arange(12.).reshape(2, 3, 2)
    resources = ledger(127)
    with ResourceScope(resources):
        array = BindingsArray({"a": values[..., :1], "b": values[..., 1:]})[:, ::2]
        calls = []
        original = np.empty

        def observed(*args, **kwargs):
            calls.append(args)
            return original(*args, **kwargs)

        monkeypatch.setattr(np, "empty", observed)
        # Two copies need 32 bytes each. An outstanding 64-byte allocation
        # leaves only 63 bytes: neither reshape destination may be allocated.
        with resources.reserve("other_live_output", memory_bytes=64):
            with pytest.raises(ResourceLimitError):
                array.reshape(4)
        assert calls == []
    assert resources.receipt()["live_memory_bytes"] == 0


def test_foreign_array_protocol_is_not_executed():
    class Foreign:
        def __array__(self, *args, **kwargs):
            raise AssertionError("A foreign conversion callback was invoked.")

    with pytest.raises((ValueError, TypeError, NotImplementedError)):
        BindingsArray({"a": Foreign()})
