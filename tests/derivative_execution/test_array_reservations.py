# Copyright 2026 QuantumBridge Contributors.
# Licensed under the Apache License, Version 2.0.
"""Typed output, conversion and lifetime contracts for numerical allocations."""

import numpy as np
import pytest

from quantumbridge import UnsupportedFeature
from quantumbridge.execution import ResourceLimitError, UnifiedExecutionLimits as Limits, UnifiedResourceLedger as Ledger
from quantumbridge.execution.array_reservations import ArrayReservation, array_layout, borrow_callback_array, mapped_matmul, matmul_into, scope_array
from quantumbridge.execution.resource_context import ResourceScope


@pytest.mark.parametrize("left_shape,right_shape", [((3,), (3,)), ((2, 3), (3,)),
    ((3,), (3, 4)), ((2, 1, 3, 4), (5, 4, 6)), ((2, 0), (0, 3)), ((0, 3), (3, 2))])
def test_matmul_shapes_values_and_broadcasts(left_shape, right_shape):
    rng = np.random.default_rng(5)
    left, right = rng.normal(size=left_shape), rng.normal(size=right_shape)
    expected = left @ right
    ledger = Ledger()
    with ResourceScope(ledger) as scope:
        actual = mapped_matmul(scope, "mapped", left, right)
        np.testing.assert_allclose(actual, expected, atol=1e-12)
        assert actual.shape == np.shape(expected)
        assert ledger.receipt()["live_memory_bytes"] == actual.nbytes
    assert ledger.receipt()["live_memory_bytes"] == 0


def test_output_limit_rejects_before_allocation_or_multiplication(monkeypatch):
    left, right = np.ones((4, 3)), np.ones((3, 2))
    ledger = Ledger(Limits(max_total_memory_bytes=63))
    def forbidden(*a, **k): pytest.fail("native allocation/matmul preceded the budget check")
    monkeypatch.setattr(np, "empty", forbidden)
    monkeypatch.setattr(np, "matmul", forbidden)
    with pytest.raises(ResourceLimitError), ResourceScope(ledger) as scope:
        mapped_matmul(scope, "mapped", left, right)
    assert ledger.receipt()["live_memory_bytes"] == 0


def test_complex_outputs_use_actual_sixteen_byte_itemsize():
    left, right = np.ones((2, 3), complex)*(1.+2j), np.ones((3, 4), complex)*(2.-.3j)
    ledger = Ledger(Limits(max_total_memory_bytes=128))
    with ResourceScope(ledger) as scope:
        result = mapped_matmul(scope, "complex_mapped", left, right)
        np.testing.assert_allclose(result, left @ right, atol=1e-12)
        assert result.dtype == np.complex128 and result.nbytes == 128
        assert ledger.receipt()["observed_array_bytes"]["complex_mapped"] == 128
    assert ledger.receipt()["peak_memory_bytes"] == 128


def test_mixed_dtype_cast_is_reserved_before_matmul(monkeypatch):
    left, right = np.ones((2, 3)), np.ones((3, 4), complex)
    # Output 128 plus the explicit complex conversion of left 96.
    ledger = Ledger(Limits(max_total_memory_bytes=223))
    def forbidden(*a, **k): pytest.fail("matmul ran before the required cast reservation")
    monkeypatch.setattr(np, "matmul", forbidden)
    with pytest.raises(ResourceLimitError), ResourceScope(ledger) as scope:
        mapped_matmul(scope, "mapped", left, right)
    assert ledger.receipt()["live_memory_bytes"] == 0


def test_strided_operand_copy_is_accounted_and_released():
    left = np.arange(24., dtype=float).reshape(4, 6)[:, ::2]
    right = np.ones((3, 2))
    ledger = Ledger(Limits(max_total_memory_bytes=160))
    with ResourceScope(ledger) as scope:
        result = mapped_matmul(scope, "mapped", left, right)
        np.testing.assert_allclose(result, left @ right)
        assert ledger.receipt()["live_memory_bytes"] == 64
        assert ledger.receipt()["peak_memory_bytes"] == 160
        assert ledger.receipt()["observed_array_bytes"]["matmul_operand_workspace"] == 96
    assert ledger.receipt()["live_memory_bytes"] == 0


def test_factory_failure_releases_before_request_scope_ends():
    ledger = Ledger()
    def fail(): raise MemoryError("injected allocation failure")
    with ResourceScope(ledger) as scope:
        with pytest.raises(MemoryError): scope_array(scope, "failed", (32,), float, fail)
        assert ledger.receipt()["live_memory_bytes"] == 0
    assert ledger.receipt()["total_reserved_memory_bytes"] == ledger.receipt()["total_released_memory_bytes"]


def test_wrong_factory_buffer_and_double_release_do_not_leak():
    ledger = Ledger()
    with ArrayReservation(ledger, "wrong", (2,), float) as reservation:
        with pytest.raises(RuntimeError): reservation.create(lambda: np.zeros(3))
        reservation.release()
        with pytest.raises(ValueError): reservation.attach(np.zeros(2))
        with pytest.raises(ValueError): reservation.__enter__()
    assert ledger.receipt()["live_memory_bytes"] == 0


@pytest.mark.parametrize("shape,dtype,error", [((-1,), float, ValueError), ((True,), float, ValueError),
    ((1.5,), float, ValueError), ((2,), object, TypeError), ((2,), "U2", TypeError),
    ((2**62, 4), float, ResourceLimitError), ((0, 2**64), float, ResourceLimitError),
    ((2**60,), complex, ResourceLimitError)])
def test_shape_and_dtype_reject_before_numpy_allocation(shape, dtype, error, monkeypatch):
    def forbidden(*a, **k): pytest.fail("invalid layout attempted an allocation")
    monkeypatch.setattr(np, "empty", forbidden)
    with pytest.raises(error): ArrayReservation(Ledger(), "shape", shape, dtype)


def test_matmul_dimension_batch_and_output_alias_contracts():
    with pytest.raises(ValueError): mapped_matmul(None, "bad", np.ones((2, 3)), np.ones((4, 2)))
    with pytest.raises(ValueError): mapped_matmul(None, "bad", np.ones((2, 3, 4)), np.ones((5, 4, 6)))
    with pytest.raises(ValueError): mapped_matmul(None, "bad", np.array(1.), np.ones(1))
    with pytest.raises(TypeError): mapped_matmul(None, "bad", [1.], np.ones(1))
    left, right = np.eye(2), np.eye(2)
    with pytest.raises(ValueError, match="non-overlapping"): matmul_into(left, right, left)
    readonly = np.zeros((2, 2)); readonly.flags.writeable = False
    with pytest.raises(ValueError, match="writable"): matmul_into(left, right, readonly)
    with pytest.raises(ValueError): matmul_into(left, right, np.zeros(1))


def test_cpu_dlpack_borrow_shares_storage_and_forbids_device_copy():
    source = np.arange(6.)
    class Borrowed:
        def __dlpack_device__(self): return (1, 0)
        def __dlpack__(self, **kwargs): return source.__dlpack__(**kwargs)
    result = borrow_callback_array(Borrowed())
    assert np.shares_memory(result, source) and not result.flags.owndata
    assert borrow_callback_array(source) is source
    class NeedsCopy:
        def __dlpack_device__(self): return (1, 0)
        def __dlpack__(self, **kwargs): raise BufferError("cannot share this buffer")
    with pytest.raises(UnsupportedFeature): borrow_callback_array(NeedsCopy())
    class Device:
        def __dlpack_device__(self): return (2, 0)
        def __dlpack__(self, **kwargs): pytest.fail("a non-CPU exporter must not be invoked")
    with pytest.raises(UnsupportedFeature): borrow_callback_array(Device())
    with pytest.raises(UnsupportedFeature): borrow_callback_array([.3])


def test_empty_scalar_layout_and_unmanaged_factory_contract():
    assert array_layout((), np.float32)[2] == 4
    result = scope_array(None, "plain", (2,), float, lambda: np.ones(2))
    np.testing.assert_array_equal(result, [1., 1.])
