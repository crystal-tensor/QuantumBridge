# Copyright 2026 QuantumBridge Contributors.
# Licensed under the Apache License, Version 2.0.
"""Structured failure categories and real request recovery, without SDK oracles."""

from dataclasses import replace

import numpy as np
import pytest

from quantumbridge import Circuit, Parameter, PauliZ, StatevectorDevice, DensityMatrixDevice
from quantumbridge.execution import (DerivativeExecutionRequest as Request, UnifiedExecutionLimits as Limits,
    UnifiedResourceLedger as Ledger, DerivativeExecutionStatus as Status)
from quantumbridge.qml import QNode


def source():
    return QNode(lambda t, x: (t.ry(x, 0), t.expval(PauliZ(0)))[-1], 1, max_diff=2)


def query(**options):
    return Request(source(), (.3,), derivative_order=2, derivative_kind="hvp", tangent=.4, **options)


def test_invalid_numeric_input_classified_before_any_resource_work():
    ledger = Ledger()
    result = StatevectorDevice().execute_derivatives(replace(query(), parameters=(np.nan,)), ledger=ledger, return_status=True)
    assert result.status == Status.INVALID_INPUT
    assert result.receipt["consumed_derivative_work"] == result.receipt["consumed_tapes"] == 0


def test_unsupported_method_is_not_invalid_input_or_runtime():
    result = StatevectorDevice().execute_derivatives(query(method="unknown"), return_status=True)
    assert result.status == Status.UNSUPPORTED and result.derivative is None


def test_invalid_direction_is_not_resource_or_runtime_failure():
    result = StatevectorDevice().execute_derivatives(replace(query(), tangent=[.4]), return_status=True)
    assert result.status == Status.INVALID_INPUT


def test_order_two_method_on_first_order_request_rejects():
    result = StatevectorDevice().execute_derivatives(replace(query(method="second_adjoint"), derivative_kind="jacobian", derivative_order=1), return_status=True)
    assert result.status == Status.INVALID_INPUT


def test_memory_error_in_actual_device_remains_resource_failure(monkeypatch):
    def fail(*a, **k): raise MemoryError("test injected allocation failure")
    monkeypatch.setattr(StatevectorDevice, "statevector", fail)
    result = StatevectorDevice().execute_derivatives(query(), return_status=True)
    assert result.status == Status.RESOURCE_LIMIT and result.receipt["live_memory_bytes"] == 0


def test_runtime_value_error_from_simulator_is_not_bad_request(monkeypatch):
    def fail(*a, **k): raise ValueError("test injected malformed simulator output")
    monkeypatch.setattr(StatevectorDevice, "statevector", fail)
    result = StatevectorDevice().execute_derivatives(query(), return_status=True)
    assert result.status == Status.NATIVE_RUNTIME_FAILURE


def test_numerical_failure_is_distinct_and_does_not_leak(monkeypatch):
    from quantumbridge.diff.qnode_engine import ExecutionPlan
    def fail(*a, **k): raise FloatingPointError("test injected numerical failure")
    monkeypatch.setattr(ExecutionPlan, "second_derivatives", fail)
    result = StatevectorDevice().execute_derivatives(query(), return_status=True)
    assert result.status == Status.NUMERICAL_FAILURE and result.code == 5
    assert result.receipt["live_memory_bytes"] == 0


def test_safe_error_does_not_echo_arbitrary_device_message(monkeypatch):
    def fail(*a, **k): raise RuntimeError("private test marker should not escape")
    monkeypatch.setattr(StatevectorDevice, "statevector", fail)
    result = StatevectorDevice().execute_derivatives(query(), return_status=True)
    assert "private test marker" not in str(result.error.to_dict())


def test_request_limit_and_supplied_parent_limit_are_both_enforced():
    parent = Ledger(Limits(max_total_memory_bytes=1))
    result = StatevectorDevice().execute_derivatives(query(limits=Limits()), ledger=parent, return_status=True)
    assert result.code == 3 and parent.receipt()["live_memory_bytes"] == 0
    parent = Ledger()
    result = StatevectorDevice().execute_derivatives(query(limits=Limits(max_total_memory_bytes=1)), ledger=parent, return_status=True)
    assert result.code == 3 and parent.receipt()["live_memory_bytes"] == 0


def test_consecutive_success_failure_success_uses_fresh_math_and_releases():
    device, request = StatevectorDevice(), query()
    first = device.execute_derivatives(request)
    failed = device.execute_derivatives(replace(request, limits=Limits(max_derivative_work=1)), return_status=True)
    last = device.execute_derivatives(request)
    assert first.code == last.code == 0 and failed.code == 3
    np.testing.assert_allclose(last.derivative, first.derivative, atol=1e-12)


def test_second_adjoint_mixed_and_finite_requests_never_substitute_shift():
    request = query(method="second_adjoint")
    assert DensityMatrixDevice().execute_derivatives(request, return_status=True).code == 2
    assert StatevectorDevice().execute_derivatives(replace(request, shots=10, seed=3), return_status=True).code == 2


def test_complex_circuit_bindings_are_not_silently_cast_real():
    p = Parameter("p")
    request = Request(Circuit(1).ry(p, 0), [1.+.5j], observable=PauliZ(0))
    result = StatevectorDevice().execute_derivatives(request, return_status=True)
    assert result.code == 1


def test_second_adjoint_shared_work_and_separate_state_reservations(monkeypatch):
    from quantumbridge.diff.qnode_engine import ExecutionPlan
    from quantumbridge.execution import UnifiedResourceLedger
    categories = set()
    event = UnifiedResourceLedger._event
    def observe(ledger, action, category, amounts):
        if action == "reserve":categories.add(category)
        return event(ledger, action, category, amounts)
    monkeypatch.setattr(UnifiedResourceLedger, "_event", observe)
    monkeypatch.setattr(ExecutionPlan, "shift_recipe", lambda *a: pytest.fail("second adjoint cannot shift"))
    def repeated(count):
        def fn(t, x):
            for _ in range(count): t.ry(x, 0)
            return t.expval(PauliZ(0))
        return Request(QNode(fn, 1, max_diff=2), (.003,), method="second_adjoint",
            derivative_order=2, derivative_kind="hvp", tangent=.4)
    one = StatevectorDevice().execute_derivatives(repeated(1))
    categories.clear()
    many = StatevectorDevice().execute_derivatives(repeated(64))
    np.testing.assert_allclose(many.derivative, -.4*64**2*np.cos(64*.003), atol=1e-9)
    assert many.receipt["consumed_derivative_work"]-one.receipt["consumed_derivative_work"] == 2*63*2*19
    # The bounded receipt can omit old events; observe real reservations instead.
    assert {"adjoint_forward_states", "adjoint_tangent_states", "adjoint_reverse_states",
            "adjoint_temporary_states", "adjoint_local_matrices", "retained_derivative_buffers"} <= categories
    assert many.receipt["consumed_tapes"] == many.metadata["second_order_work"]["tape_count"] == 2


def test_shape_changing_custom_transform_does_not_return_a_truncated_derivative():
    qnode = source().with_transform(lambda tape: ((tape.copy(),),
        lambda results: (results[0], results[0])))
    result = qnode.device.execute_derivatives(Request(qnode, (.3,), derivative_order=2,
        derivative_kind="hvp", tangent=.4), return_status=True)
    assert result.code == 2 and result.value is None and result.derivative is None
    assert result.error.failed_operation == "derivative_output_structure"
    assert result.receipt["live_memory_bytes"] == 0


def test_keyboard_interrupt_releases_request_resources_without_refunding_work(monkeypatch):
    ledger = Ledger()
    def interrupted(*a, **k): raise KeyboardInterrupt()
    with monkeypatch.context() as context:
        context.setattr(StatevectorDevice, "statevector", interrupted)
        with pytest.raises(KeyboardInterrupt): StatevectorDevice().execute_derivatives(query(), ledger=ledger)
    receipt = ledger.receipt()
    assert receipt["live_memory_bytes"] == receipt["active_tapes"] == receipt["reserved_shots"] == 0
    assert receipt["consumed_derivative_work"] > 0
    assert StatevectorDevice().execute_derivatives(query()).code == 0


def test_snapshot_derivative_explicitly_rejects_without_dense_or_untracked_result(monkeypatch):
    circuit = Circuit(1).ry(Parameter("theta"), 0).save_statevector()
    request = Request(circuit, [.3], observable=PauliZ(0), method="parameter-shift",
        derivative_order=2, derivative_kind="hvp", tangent=[.4])
    result = StatevectorDevice().execute_derivatives(request, return_status=True)
    assert result.code == 2 and result.value is None and result.derivative is None
    assert result.receipt["live_memory_bytes"] == 0
