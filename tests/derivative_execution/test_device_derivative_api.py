# Copyright 2026 QuantumBridge Contributors.
# Licensed under the Apache License, Version 2.0.
"""Actual Device requests, independently checked against mathematical formulas."""

from dataclasses import replace

import numpy as np
import pytest

from quantumbridge import Circuit, Parameter, PauliX, PauliZ, StatevectorDevice, MatrixProductStateDevice, DensityMatrixDevice, StabilizerDevice
from quantumbridge.execution import DerivativeExecutionRequest as Request, DerivativeExecutionError, UnifiedExecutionLimits, UnifiedResourceLedger
from quantumbridge.qml import QNode, Tape


def circuit_request(**changes):
    theta = Parameter("theta")
    circuit = Circuit(1).ry(theta, 0)
    return Request(circuit, [.3], observable=PauliZ(0), **changes)


def test_native_circuit_device_jacobian_does_not_call_qnode_gradient(monkeypatch):
    monkeypatch.setattr(QNode, "compute_jacobian", lambda *a, **k: pytest.fail("Device must execute native plans directly"))
    request = circuit_request(method="parameter-shift")
    device = StatevectorDevice()
    assert device.supports_derivatives(request)
    result = device.execute_derivatives(request)
    assert result.code == 0 and result.metadata["device_derivative_protocol"]
    np.testing.assert_allclose(result.value, np.cos(.3), atol=1e-12)
    np.testing.assert_allclose(result.derivative, [-np.sin(.3)], atol=1e-12)
    assert result.receipt["live_memory_bytes"] == result.receipt["active_tapes"] == 0


def test_native_circuit_device_second_adjoint_hessian_forbids_shift(monkeypatch):
    from quantumbridge.diff.qnode_engine import ExecutionPlan
    monkeypatch.setattr(ExecutionPlan, "shift_recipe", lambda *a: pytest.fail("no shift fallback"))
    request = circuit_request(method="second_adjoint", derivative_order=2, derivative_kind="hessian")
    result = StatevectorDevice().execute_derivatives(request)
    np.testing.assert_allclose(result.derivative, [[-np.cos(.3)]], atol=1e-12)
    assert result.metadata["shifted_evaluation_count"] == 0


def test_native_circuit_device_second_adjoint_hvp_is_directional(monkeypatch):
    from quantumbridge.diff.qnode_engine import ExecutionPlan
    monkeypatch.setattr(ExecutionPlan, "shift_recipe", lambda *a: pytest.fail("no shift fallback"))
    request = circuit_request(method="second_adjoint", derivative_order=2, derivative_kind="hvp", tangent=[.4])
    result = StatevectorDevice().execute_derivatives(request)
    np.testing.assert_allclose(result.derivative, [-.4*np.cos(.3)], atol=1e-12)
    assert result.metadata["hvp_streamed"]


def test_native_tape_nested_probability_jacobian_and_input_mapping():
    tape = Tape(1)
    theta = Parameter("theta")
    tape.ry(theta, 0)
    tape.set_output({"z": tape.expval(PauliZ(0)), "p": tape.probs([0])})
    request = Request(tape, {"theta": .3}, method="parameter-shift")
    result = StatevectorDevice().execute_derivatives(request)
    np.testing.assert_allclose(result.derivative["p"]["0"], [-.5*np.sin(.3)], atol=1e-12)
    np.testing.assert_allclose(result.derivative["p"]["1"], [.5*np.sin(.3)], atol=1e-12)


def test_device_and_qnode_nonlinear_shared_parameter_hvp_agree():
    def fn(t, x):
        t.ry(x[0]*x[1], 0)
        return t.expval(PauliZ(0))
    node = QNode(fn, 1, max_diff=2)
    point, direction = np.array([.2, .3]), np.array([.4, -.1])
    result = node.device.execute_derivatives(Request(node, (point,), derivative_order=2,
        derivative_kind="hvp", tangent=direction))
    np.testing.assert_allclose(result.derivative, node.compute_hvp(direction, point), atol=1e-12)


def test_vjp_returns_input_shape_and_rejects_wrong_output_cotangent():
    device = StatevectorDevice()
    request = circuit_request(derivative_kind="vjp", cotangent=2.)
    np.testing.assert_allclose(device.compute_vjp(request), [-2*np.sin(.3)], atol=1e-12)
    with pytest.raises(DerivativeExecutionError) as caught:
        device.compute_vjp(replace(request, cotangent=[2.]))
    assert caught.value.code == 1


def test_jvp_executes_native_jacobian_contraction():
    request = circuit_request(derivative_kind="jvp", tangent=[.4])
    base, derivative = StatevectorDevice().execute_and_compute_jvp(request)
    np.testing.assert_allclose([base, derivative], [np.cos(.3), -.4*np.sin(.3)], atol=1e-12)


def test_mps_device_hvp_never_expands_full_state(monkeypatch):
    from quantumbridge.information.matrix_product_state import MatrixProductState
    monkeypatch.setattr(StatevectorDevice, "statevector", lambda *a: pytest.fail("no dense fallback"))
    monkeypatch.setattr(MatrixProductState, "statevector", lambda *a: pytest.fail("no full MPS expansion"))
    request = circuit_request(derivative_order=2, derivative_kind="hvp", tangent=[.4])
    result = MatrixProductStateDevice().execute_derivatives(request)
    np.testing.assert_allclose(result.derivative, [-.4*np.cos(.3)], atol=1e-12)
    assert result.receipt["peak_memory_bytes"] > 0


def test_density_device_uses_native_density_shift_not_statevector(monkeypatch):
    monkeypatch.setattr(StatevectorDevice, "statevector", lambda *a: pytest.fail("no pure-state fallback"))
    request = circuit_request(method="parameter-shift", derivative_order=2, derivative_kind="hessian")
    result = DensityMatrixDevice().execute_derivatives(request)
    np.testing.assert_allclose(result.derivative, [[-np.cos(.3)]], atol=1e-12)


def test_tableau_capability_rejects_continuous_derivatives_without_fallback(monkeypatch):
    monkeypatch.setattr(StatevectorDevice, "statevector", lambda *a: pytest.fail("no fallback"))
    device, request = StabilizerDevice(), circuit_request()
    assert not device.supports_derivatives(request)
    result = device.execute_derivatives(request, return_status=True)
    assert result.code == 2 and result.derivative is None


def test_invalid_request_order_is_not_runtime_failure():
    request = circuit_request(derivative_order=2)
    result = StatevectorDevice().execute_derivatives(request, return_status=True)
    assert result.code == 1 and result.error.stage == "validation"


def test_budget_failure_then_valid_request_recovers_without_memory_leak():
    device = StatevectorDevice()
    request = circuit_request(method="parameter-shift")
    first = device.execute_derivatives(request)
    ledger = UnifiedResourceLedger(UnifiedExecutionLimits(max_total_memory_bytes=1))
    failed = device.execute_derivatives(request, ledger=ledger, return_status=True)
    assert failed.code == 3 and ledger.receipt()["live_memory_bytes"] == 0
    np.testing.assert_allclose(device.execute_derivatives(request).derivative, first.derivative, atol=1e-12)


def test_execute_and_compute_helpers_actually_return_native_results():
    device, request = StatevectorDevice(), circuit_request(method="parameter-shift")
    base, jac = device.execute_and_compute_derivatives(request)
    np.testing.assert_allclose([base, jac[0]], [np.cos(.3), -np.sin(.3)], atol=1e-12)
    np.testing.assert_allclose(device.compute_hessian(request), [[-np.cos(.3)]], atol=1e-12)
    np.testing.assert_allclose(device.compute_hvp(replace(request, tangent=[.4])), [-.4*np.cos(.3)], atol=1e-12)


def test_source_maps_and_derivative_arrays_are_reserved_before_plan_allocation(monkeypatch):
    from quantumbridge.diff.qnode_engine import AngleRecorder, ExecutionPlan
    from quantumbridge.execution.resource_context import current_resources
    original_map, original_jacobian = AngleRecorder.classical_jacobian, ExecutionPlan.jacobian
    calls = []
    def reserved(category):
        receipt = current_resources().ledger.receipt()
        assert any(event["action"] == "reserve" and event["category"] == category
            for event in receipt["events"])
        assert receipt["live_memory_bytes"] > 0
    def source(self, size):
        reserved("classical_source_maps")
        calls.append("map")
        return original_map(self, size)
    def jacobian(self, *args, **kwargs):
        reserved("retained_derivative_buffers")
        calls.append("jacobian")
        return original_jacobian(self, *args, **kwargs)
    monkeypatch.setattr(AngleRecorder, "classical_jacobian", source)
    monkeypatch.setattr(ExecutionPlan, "jacobian", jacobian)
    result = StatevectorDevice().execute_derivatives(circuit_request())
    assert result.code == 0 and calls == ["map", "jacobian"]
