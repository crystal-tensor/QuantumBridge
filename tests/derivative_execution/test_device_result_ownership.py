# Copyright 2026 QuantumBridge Contributors.
# Licensed under the Apache License, Version 2.0.
"""Returned native arrays, not just callbacks, retain their resource leases."""

import gc
import weakref

import numpy as np
import pytest

from quantumbridge import PauliZ, StatevectorDevice
from quantumbridge.execution import DerivativeExecutionRequest as Request, UnifiedExecutionLimits as Limits, UnifiedResourceLedger as Ledger
from quantumbridge.qml import QNode, Tape


def request(kind="jacobian"):
    def fn(tape, point):
        tape.ry(point[0], 0)
        tape.rz(point[1], 0)
        return {"z": tape.expval(PauliZ(0)), "p": tape.probs([0])}
    node = QNode(fn, 1, max_diff=2, diff_method="adjoint")
    order = 2 if kind in {"hvp", "hessian"} else 1
    return Request(node, (np.array([.3, .2]),), derivative_kind=kind, derivative_order=order,
        method="adjoint", tangent=np.array([.4, -.1]) if kind in {"hvp", "jvp"} else None,
        cotangent={"z": .3, "p": {"0": .2, "1": -.1}} if kind == "vjp" else None)


@pytest.mark.parametrize("kind", ["jacobian", "jvp", "vjp", "hessian", "hvp"])
def test_public_result_keeps_storage_after_device_and_source_are_deleted(kind):
    device, config, ledger = StatevectorDevice(), request(kind), Ledger()
    device_reference, node_reference = weakref.ref(device), weakref.ref(config.circuit_or_tape)
    result = device.execute_derivatives(config, ledger=ledger)
    assert result.code == 0
    assert ledger.receipt()["live_memory_bytes"] > 0, "public Result storage was released at callback return"
    raw_bytes = result.jacobian.nbytes+(0 if result.second is None else result.second.nbytes)
    assert result.receipt["observed_array_bytes"]["retained_derivative_buffers"] >= raw_bytes
    derivative = result.jacobian.copy()
    work = ledger.receipt()["consumed_derivative_work"]
    del config, device
    gc.collect()
    assert device_reference() is None and node_reference() is None
    np.testing.assert_array_equal(result.jacobian, derivative)
    assert ledger.receipt()["live_memory_bytes"] > 0
    del result
    gc.collect()
    receipt = ledger.receipt()
    assert receipt["live_memory_bytes"] == 0
    assert receipt["total_reserved_memory_bytes"] == receipt["total_released_memory_bytes"]
    assert receipt["consumed_derivative_work"] == work


def test_user_held_nested_result_view_keeps_storage_after_result_is_deleted():
    ledger = Ledger()
    result = StatevectorDevice().execute_derivatives(request(), ledger=ledger)
    view = result.derivative["p"]["0"][1:]
    matrix_reference = weakref.ref(result.jacobian)
    before = ledger.receipt()["live_memory_bytes"]
    assert before > 0
    del result
    gc.collect()
    assert matrix_reference() is not None
    assert ledger.receipt()["live_memory_bytes"] == before
    np.testing.assert_allclose(view, [0.], atol=1e-12)
    del view
    gc.collect()
    assert matrix_reference() is None and ledger.receipt()["live_memory_bytes"] == 0


def test_retained_result_competes_with_the_next_request_and_release_recovers():
    config, device, probe = request(), StatevectorDevice(), Ledger()
    first = device.execute_derivatives(config, ledger=probe)
    cap = probe.receipt()["peak_memory_bytes"]
    del first
    gc.collect()
    ledger = Ledger(Limits(max_total_memory_bytes=cap))
    original = device.execute_derivatives(config, ledger=ledger)
    live = ledger.receipt()["live_memory_bytes"]
    assert live > 0
    failed = device.execute_derivatives(config, ledger=ledger, return_status=True)
    assert failed.code == 3 and failed.value is None and failed.derivative is None
    assert failed.jacobian is failed.second is None
    np.testing.assert_allclose(original.derivative["z"], [-np.sin(.3), 0.], atol=1e-12)
    consumed = ledger.receipt()["consumed_derivative_work"]
    del failed, original
    gc.collect()
    assert ledger.receipt()["live_memory_bytes"] == 0
    recovered = device.execute_derivatives(config, ledger=ledger)
    assert recovered.code == 0 and ledger.receipt()["consumed_derivative_work"] > consumed
    del recovered
    gc.collect()
    assert ledger.receipt()["live_memory_bytes"] == 0


def test_failed_status_result_does_not_retain_partial_configuration_copies():
    source = Tape(1)
    source.set_output(source.expval(PauliZ(0)))
    source.circuit.metadata = {"first": np.ones(8), "second": np.zeros(8)}
    ledger = Ledger(Limits(max_total_memory_bytes=64))
    failed = StatevectorDevice().execute_derivatives(Request(source, []), ledger=ledger, return_status=True)
    assert failed.code == 3 and failed.jacobian is failed.second is failed.value is None
    gc.collect()
    assert ledger.receipt()["live_memory_bytes"] == 0, "a returned status error retained the partial deepcopy frame"
    assert failed.error.__traceback__ is None
    assert failed.receipt["live_memory_bytes"] == failed.receipt["total_reserved_memory_bytes"]-failed.receipt["total_released_memory_bytes"]
