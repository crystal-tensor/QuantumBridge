# Copyright 2026 QuantumBridge Contributors. Apache-2.0.
"""Independent packed-memory helper math and owned-copy/view lifetimes."""

import gc
import numpy as np
import pytest

from quantumbridge.execution.resource_context import ResourceScope
from quantumbridge.execution.resource_ledger import UnifiedResourceLedger
from quantumbridge.primitives.v2 import BitArray, DataBin, SamplerPubResult


def test_samples_counts_and_bool_orders_preserve_nonzero_cross_byte_bits():
    samples = ["111000000", "000000001", "100000010"]
    bits = BitArray.from_samples(samples)
    assert bits.num_bits == 9
    np.testing.assert_array_equal(bits.array, [[1, 192], [0, 1], [1, 2]])
    np.testing.assert_array_equal(
        bits.to_bool_array(), [[int(c) for c in row] for row in samples]
    )
    np.testing.assert_array_equal(
        bits.to_bool_array("little"), [[int(c) for c in row[::-1]] for row in samples]
    )
    np.testing.assert_array_equal(
        BitArray.from_bool_array(bits.to_bool_array()).array, bits.array
    )
    np.testing.assert_array_equal(
        BitArray.from_bool_array(bits.to_bool_array("little"), "little").array,
        bits.array,
    )
    assert bits.get_int_counts() == {448: 1, 1: 1, 258: 1}
    np.testing.assert_array_equal(bits.bitcount(), [3, 1, 2])


def test_bit_and_shot_selection_uses_public_little_endian_indices():
    bits = BitArray.from_samples(["111000000", "000000001", "100000010"])
    assert bits.slice_bits([8, 0]).get_bitstrings() == ["01", "10", "01"]
    assert bits.slice_shots([2, 0]).get_bitstrings() == ["100000010", "111000000"]
    assert bits.postselect([8, 0], [1, 0]).get_bitstrings() == [
        "111000000",
        "100000010",
    ]
    assert bits.postselect(0, 1).get_bitstrings() == ["000000001"]


def test_concatenation_bits_places_first_register_in_low_bits():
    a = BitArray.from_samples(["10", "01"])
    b = BitArray.from_samples(["111000000", "000000001"])
    joined = BitArray.concatenate_bits([a, b])
    assert joined.num_bits == 11
    assert joined.get_bitstrings() == ["11100000010", "00000000101"]
    pub = SamplerPubResult(DataBin(alpha=a, beta=b))
    np.testing.assert_array_equal(pub.join_data().array, joined.array)
    assert pub.join_data(["beta", "alpha"]).get_bitstrings() == [
        "10111000000",
        "01000000001",
    ]


def test_reshape_can_change_batch_or_total_shot_axes_but_never_bit_width():
    bits = BitArray(
        np.array(
            [[[[0], [1], [2]], [[3], [0], [1]]], [[[2], [3], [0]], [[1], [2], [3]]]],
            dtype=np.uint8,
        ),
        2,
    )
    assert bits.shape == (2, 2) and bits.num_shots == 3
    assert bits.reshape(4).shape == (4,)
    assert bits.reshape(12).shape == () and bits.reshape(12).num_shots == 12
    assert bits.reshape(3, 4).shape == (3,) and bits.reshape(3, 4).num_shots == 4
    np.testing.assert_array_equal(
        bits.transpose().array, bits.array.transpose(1, 0, 2, 3)
    )
    np.testing.assert_array_equal(
        BitArray.concatenate([bits, bits], axis=0).array,
        np.concatenate([bits.array, bits.array], axis=0),
    )
    assert BitArray.concatenate_shots([bits, bits]).num_shots == 6
    with pytest.raises(ValueError):
        bits.reshape(-1)


def test_count_batches_and_diagonal_expectation_are_actual_sample_statistics():
    bits = BitArray.from_counts([{"00": 3, "11": 1}, {"01": 2, "10": 2}], num_bits=2)
    assert bits.shape == (2,) and bits.num_shots == 4
    np.testing.assert_allclose(
        bits.expectation_values(["ZZ", "IZ"]), [1.0, 0.0], atol=0, rtol=0
    )
    np.testing.assert_allclose(
        bits.expectation_values([["ZZ"], [{"IZ": 0.5, "ZI": 0.5}]]),
        [[1.0, -1.0], [0.5, 0.0]],
        atol=0,
        rtol=0,
    )
    with pytest.raises(ValueError):
        bits.expectation_values("XI")


def test_helper_copy_and_view_keep_storage_leases_after_container_deletion():
    ledger = UnifiedResourceLedger()
    with ResourceScope(ledger):
        original = BitArray.from_samples(["111000000", "000000001"])
        copied = original.slice_bits([8, 0])
        view = memoryview(original.reshape(1).array)
        copied_view = copied.array[:]
    del original, copied
    gc.collect()
    assert ledger.receipt()["live_memory_bytes"] == 6
    assert view.tolist() == [[[1, 192], [0, 1]]]
    del view
    gc.collect()
    assert ledger.receipt()["live_memory_bytes"] == 2
    assert copied_view.tolist() == [[1], [2]]
    del copied_view
    gc.collect()
    assert ledger.receipt()["live_memory_bytes"] == 0


def test_helper_output_budget_denies_before_the_first_array_allocation(monkeypatch):
    from quantumbridge.execution.resource_limits import UnifiedExecutionLimits
    bits = BitArray(np.array([[1, 192], [0, 1]], dtype=np.uint8), 9)
    ledger = UnifiedResourceLedger(UnifiedExecutionLimits(max_total_memory_bytes=1))
    calls = []
    original = np.empty

    def observed(*args, **kwargs):
        calls.append(1)
        return original(*args, **kwargs)

    monkeypatch.setattr(np, "empty", observed)
    with ResourceScope(ledger), pytest.raises(MemoryError):
        bits.slice_bits([8, 0])
    assert calls == [] and ledger.receipt()["live_memory_bytes"] == 0
