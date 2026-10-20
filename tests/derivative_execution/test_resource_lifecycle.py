# Copyright 2026 QuantumBridge Contributors.
# Licensed under the Apache License, Version 2.0.
"""Independent ownership/lifetime scenarios, no quantum SDK dependencies."""

import pytest

from quantumbridge.execution import UnifiedExecutionLimits as Limits, UnifiedResourceLedger as Ledger, ResourceLimitError


def test_release_on_success_and_observation_is_not_reservation():
    ledger = Ledger()
    with ledger.reserve("state", memory_bytes=128) as allocation:
        allocation.observe(96)
        assert ledger.receipt()["live_memory_bytes"] == 128
    r = ledger.receipt()
    assert r["live_memory_bytes"] == 0 and r["peak_memory_bytes"] == 128
    assert r["observed_array_bytes"] == {"state": 96}
    assert r["total_reserved_memory_bytes"] == r["total_released_memory_bytes"] == 128


def test_release_on_exception_keeps_consumed_shots():
    ledger = Ledger()
    with pytest.raises(RuntimeError):
        with ledger.reserve("sample", memory_bytes=64, shots=10) as allocation:
            allocation.consume(shots=3)
            raise RuntimeError("test failure")
    assert ledger.receipt()["live_memory_bytes"] == ledger.receipt()["reserved_shots"] == 0
    assert ledger.receipt()["consumed_shots"] == 3


def test_sequential_children_do_not_sum_as_simultaneous_peak():
    ledger = Ledger(Limits(max_total_memory_bytes=100))
    for _ in range(10):
        with ledger.reserve("child", memory_bytes=80):
            pass
    assert ledger.receipt()["peak_memory_bytes"] == 80
    assert ledger.receipt()["total_reserved_memory_bytes"] == 800


def test_retained_parent_and_child_memory_add():
    ledger = Ledger(Limits(max_total_memory_bytes=100))
    with ledger.reserve("retained", memory_bytes=60):
        with pytest.raises(ResourceLimitError) as failure:
            ledger.reserve("child", memory_bytes=50)
        assert failure.value.category == "memory" and failure.value.estimated == 110
        assert ledger.receipt()["live_memory_bytes"] == 60


def test_siblings_share_parent_but_keep_subtree_receipts():
    parent = Ledger(Limits(max_total_memory_bytes=100))
    left, right = Ledger(parent=parent), Ledger(parent=parent)
    with left.reserve("left", memory_bytes=70):
        with pytest.raises(ResourceLimitError):
            right.reserve("right", memory_bytes=40)
    assert parent.receipt()["live_memory_bytes"] == 0
    assert right.receipt()["peak_memory_bytes"] == 0
    assert left.receipt()["peak_memory_bytes"] == 70


def test_child_stricter_cap_is_not_overridden_by_parent():
    root = Ledger()
    child = Ledger(Limits(max_total_memory_bytes=10), parent=root)
    with pytest.raises(ResourceLimitError):
        child.reserve("state", memory_bytes=11)
    assert root.receipt()["live_memory_bytes"] == 0


def test_three_level_work_accumulates_in_every_ancestor():
    root = Ledger(Limits(max_derivative_work=10))
    middle = Ledger(parent=root)
    leaf = Ledger(parent=middle)
    leaf.consume(derivative_work=7)
    with pytest.raises(ResourceLimitError):
        middle.consume(derivative_work=4)
    assert [x.receipt()["consumed_derivative_work"] for x in (root, middle, leaf)] == [7, 7, 7]


def test_preflight_does_not_consume_or_reserve():
    ledger = Ledger()
    ledger.preflight(memory_bytes=100, shots=20, tapes=3, derivative_work=50)
    r = ledger.receipt()
    assert r["estimated"]["memory_bytes"] == 100
    assert r["live_memory_bytes"] == r["consumed_shots"] == r["consumed_tapes"] == 0
    assert r["peak_memory_bytes"] == 0


def test_failed_preflight_has_structured_details_and_no_allocations():
    ledger = Ledger(Limits(max_total_shots=5))
    with pytest.raises(ResourceLimitError) as failure:
        ledger.preflight(shots=6)
    details = failure.value.to_dict()
    assert details["code"] == 3 and details["category"] == "shots"
    assert details["estimated"] == 6 and details["limit"] == 5 and details["stage"] == "preflight"
    assert ledger.receipt()["reserved_shots"] == 0


def test_partial_consumption_releases_unused_shots_without_refund():
    ledger = Ledger(Limits(max_total_shots=10))
    with ledger.reserve("sample", shots=10) as sample:
        sample.consume(shots=4)
        assert ledger.receipt()["reserved_shots"] == 6
    ledger.consume(shots=6)
    assert ledger.receipt()["consumed_shots"] == 10
    with pytest.raises(ResourceLimitError):
        ledger.consume(shots=1)


def test_remaining_reservations_block_unrelated_shot_consumption():
    ledger = Ledger(Limits(max_total_shots=10))
    with ledger.reserve("left", shots=8):
        with pytest.raises(ResourceLimitError):
            ledger.consume(shots=3)
        ledger.consume(shots=2)
    assert ledger.receipt()["consumed_shots"] == 2


def test_overconsuming_a_ticket_does_not_corrupt_accounts():
    ledger = Ledger()
    with ledger.reserve("sample", shots=3) as sample:
        with pytest.raises(ValueError):
            sample.consume(shots=4)
        assert ledger.receipt()["reserved_shots"] == 3


def test_active_tape_is_not_counted_twice_as_completed_execution():
    ledger = Ledger(Limits(max_total_tapes=1))
    with ledger.reserve("tape", tapes=1) as active:
        active.consume(tapes=1)
        assert ledger.receipt()["active_tapes"] == 1
    assert ledger.receipt()["consumed_tapes"] == 1
    assert ledger.receipt()["active_tapes"] == 0


def test_nested_active_tapes_are_limited_before_expansion():
    ledger = Ledger(Limits(max_total_tapes=1))
    with ledger.reserve("parent", tapes=1):
        with pytest.raises(ResourceLimitError):
            ledger.reserve("child", tapes=1)


def test_cumulative_tapes_remain_after_sequential_releases():
    ledger = Ledger(Limits(max_total_tapes=2))
    for _ in range(2):
        with ledger.reserve("tape", tapes=1):
            ledger.consume(tapes=1)
    with pytest.raises(ResourceLimitError):
        ledger.consume(tapes=1)
    assert ledger.receipt()["consumed_tapes"] == 2


def test_release_is_idempotent_and_cannot_reenter_or_observe():
    ledger = Ledger()
    reservation = ledger.reserve("state", memory_bytes=10)
    reservation.release()
    reservation.release()
    with pytest.raises(ValueError): reservation.__enter__()
    with pytest.raises(ValueError): reservation.observe(1)
    with pytest.raises(ValueError): reservation.consume(shots=0)
    assert ledger.receipt()["total_released_memory_bytes"] == 10


def test_observed_workspace_cannot_be_larger_than_prior_reservation():
    ledger = Ledger()
    with ledger.reserve("workspace", memory_bytes=100) as allocation:
        with pytest.raises(RuntimeError): allocation.observe(101)
    assert ledger.receipt()["observed_array_bytes"] == {}


def test_unavailable_workspace_is_not_reported_as_observed_peak():
    root, child = Ledger(), Ledger()
    child = Ledger(parent=root)
    child.unavailable("lapack_internal_peak", "allocator not observable")
    assert root.receipt()["observed_array_bytes"] == {}
    assert root.receipt()["unavailable"]["lapack_internal_peak"] == "allocator not observable"


def test_receipts_do_not_expose_mutable_ledger_state():
    ledger = Ledger()
    ledger.consume(shots=1)
    receipt = ledger.receipt()
    receipt["events"].clear()
    receipt["estimated"]["shots"] = -1
    assert ledger.receipt()["events"] and ledger.receipt()["estimated"]["shots"] == 0


def test_failure_then_valid_reservation_recovers_exactly():
    ledger = Ledger(Limits(max_total_memory_bytes=10))
    with ledger.reserve("state", memory_bytes=10): pass
    with pytest.raises(ResourceLimitError): ledger.reserve("state", memory_bytes=11)
    with ledger.reserve("state", memory_bytes=10): pass
    assert ledger.receipt()["live_memory_bytes"] == 0
    assert ledger.receipt()["peak_memory_bytes"] == 10


def test_work_reservation_converts_to_consumed_not_double_counted():
    ledger = Ledger(Limits(max_derivative_work=5))
    with ledger.reserve("adjoint", derivative_work=5) as work:
        work.consume(derivative_work=3)
        assert ledger.receipt()["reserved_derivative_work"] == 2
    ledger.consume(derivative_work=2)
    assert ledger.receipt()["consumed_derivative_work"] == 5


def test_invalid_amounts_limits_categories_and_parents_reject():
    for value in (-1, True, .5):
        with pytest.raises(ValueError): Ledger().reserve("bad", memory_bytes=value)
        with pytest.raises(ValueError): Limits(max_total_shots=value)
    with pytest.raises(TypeError): Ledger(parent=object())
    with pytest.raises(TypeError): Ledger(limits=object())
    with pytest.raises(ValueError): Ledger().reserve("")


def test_zero_budget_allows_zero_resource_classical_work_only():
    ledger = Ledger(Limits(0, 0, 0, 0))
    with ledger.reserve("identity"): pass
    with pytest.raises(ResourceLimitError): ledger.reserve("one-byte", memory_bytes=1)


def test_nested_reservation_atomic_when_parent_rejects_last_category():
    root = Ledger(Limits(max_derivative_work=1))
    child = Ledger(parent=root)
    with pytest.raises(ResourceLimitError):
        child.reserve("all", memory_bytes=100, shots=10, tapes=1, derivative_work=2)
    assert root.receipt()["total_reserved_memory_bytes"] == 0
    assert child.receipt()["reserved_shots"] == 0


def test_event_history_is_bounded_and_omissions_are_explicit():
    ledger = Ledger()
    for _ in range(4100): ledger.consume()
    r = ledger.receipt()
    assert len(r["events"]) == 4096 and r["omitted_events"] == 4
    assert r["event_count"] == 4100
