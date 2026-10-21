# Copyright 2026 QuantumBridge Contributors.
# Licensed under the Apache License, Version 2.0.
"""Completed MPS trajectories are work even when a later trajectory fails."""

import gc

import numpy as np
import pytest

from quantumbridge import Circuit, MatrixProductStateDevice, PauliZ
from quantumbridge.execution import DerivativeExecutionRequest as Request, UnifiedExecutionLimits as Limits, UnifiedResourceLedger as Ledger
from quantumbridge.execution.control_flow_engine import DynamicExecutionEngine
from quantumbridge.execution.resource_context import ResourceScope
from quantumbridge.information import MatrixProductState
from quantumbridge.qml import QNode
from quantumbridge.noise import AmplitudeDampingChannel, NoiseModel
from quantumbridge.simulator.snapshots import SnapshotContext


def test_mps_status_preserves_two_completed_shots_after_third_measurement_failure(monkeypatch):
    def source(tape, x):
        tape.ry(x, 0)
        return tape.expval(PauliZ(0))
    device = MatrixProductStateDevice()
    node = QNode(source, 1, device=device, shots=5, seed=7)
    request = Request(node, (.3,), derivative_order=0, derivative_kind="value")
    original, completed = MatrixProductState.measure, []
    def failed(self, *args, **kwargs):
        if len(completed) == 2:raise RuntimeError("injected third trajectory measurement failure")
        result = original(self, *args, **kwargs)
        completed.append(result)
        return result
    with monkeypatch.context() as patch:
        patch.setattr(MatrixProductState, "measure", failed)
        result = device.execute_derivatives(request, return_status=True)
    assert result.code == 4 and result.value is None
    assert len(completed) == result.receipt["consumed_shots"] == 2
    assert result.receipt["live_memory_bytes"] == result.receipt["reserved_shots"] == 0
    assert "failed_native_sample_completion" in result.receipt["unavailable"]
    recovered = device.execute_derivatives(request)
    repeated = device.execute_derivatives(request)
    assert recovered.receipt["consumed_shots"] == 5
    np.testing.assert_array_equal(recovered.value, repeated.value)


def test_dynamic_snapshot_failure_preserves_only_completed_shots(monkeypatch):
    circuit = Circuit(1).h(0).save_matrix_product_state(pershot=True)
    snapshots = SnapshotContext(circuit, "matrix_product_state", finite_shots=True)
    engine = DynamicExecutionEngine(MatrixProductStateDevice(), circuit, snapshot_context=snapshots)
    original, saves, ledger = SnapshotContext.observe, [], Ledger()
    def failed(self, *args, **kwargs):
        if len(saves) == 2:raise MemoryError("injected third snapshot failure")
        result = original(self, *args, **kwargs)
        saves.append(1)
        return result
    with monkeypatch.context() as patch:
        patch.setattr(SnapshotContext, "observe", failed)
        with ResourceScope(ledger), pytest.raises(MemoryError):
            engine.shots(5, seed=7)
    assert ledger.receipt()["consumed_shots"] == len(saves) == 2
    assert ledger.receipt()["reserved_shots"] == 0
    assert "failed_native_sample_completion" in ledger.receipt()["unavailable"]
    assert ledger.receipt()["live_memory_bytes"] == 2*32
    del snapshots, engine
    gc.collect()
    assert ledger.receipt()["live_memory_bytes"] == 0


@pytest.mark.parametrize("error,code", [(RuntimeError, 4), (MemoryError, 3), (FloatingPointError, 5)])
def test_third_kraus_failure_preserves_completed_noisy_shots_and_recovers(error, code, monkeypatch):
    def source(tape, x):
        tape.ry(x, 0)
        return tape.expval(PauliZ(0))
    device = MatrixProductStateDevice(noise_model=NoiseModel().add_channel(AmplitudeDampingChannel(.3)))
    node = QNode(source, 1, device=device, shots=7, seed=11)
    request = Request(node, (1.3,), derivative_order=0, derivative_kind="value")
    original, calls = MatrixProductStateDevice._kraus_choices, []
    def failed(*args):
        calls.append(1)
        if len(calls) == 3:raise error("injected third Kraus failure")
        return original(*args)
    with monkeypatch.context() as patch:
        patch.setattr(MatrixProductStateDevice, "_kraus_choices", staticmethod(failed))
        result = device.execute_derivatives(request, return_status=True)
    assert result.code == code and result.value is None
    assert result.receipt["consumed_shots"] == 2
    assert result.receipt["live_memory_bytes"] == result.receipt["reserved_shots"] == 0
    assert "failed_native_sample_completion" in result.receipt["unavailable"]
    recovered = device.execute_derivatives(request)
    repeated = device.execute_derivatives(request)
    assert recovered.receipt["consumed_shots"] == 7
    np.testing.assert_array_equal(recovered.value, repeated.value)


def test_direct_mps_postprocessing_failure_keeps_all_completed_shots(monkeypatch):
    device, ledger = MatrixProductStateDevice(), Ledger()
    def failed(*args):raise MemoryError("injected counts postprocessing failure")
    with monkeypatch.context() as patch:
        patch.setattr(MatrixProductStateDevice, "_counts", staticmethod(failed))
        with ResourceScope(ledger), pytest.raises(MemoryError):
            device.run_shots(Circuit(1).h(0), shots=5, seed=7)
    gc.collect()
    assert ledger.receipt()["consumed_shots"] == 5
    assert ledger.receipt()["live_memory_bytes"] == ledger.receipt()["reserved_shots"] == 0
    recovered = device.run_shots(Circuit(1).h(0), shots=5, seed=7)
    repeated = device.run_shots(Circuit(1).h(0), shots=5, seed=7)
    assert recovered.counts() == repeated.counts()


@pytest.mark.parametrize("dynamic", [False, True])
def test_mps_direct_shot_cap_denies_before_state_allocation(dynamic, monkeypatch):
    device, ledger = MatrixProductStateDevice(), Ledger(Limits(max_total_shots=3))
    circuit = Circuit(1)
    if dynamic:circuit.save_matrix_product_state(pershot=True)
    monkeypatch.setattr(MatrixProductStateDevice, "_initial", lambda *a, **k: pytest.fail("Shot cap ignored"))
    with ResourceScope(ledger), pytest.raises(MemoryError):
        device.run_shots(circuit, shots=4)
    assert ledger.receipt()["consumed_shots"] == ledger.receipt()["reserved_shots"] == 0


def test_nested_dynamic_shot_meter_does_not_double_charge():
    ledger, device = Ledger(), MatrixProductStateDevice()
    with ResourceScope(ledger):
        result = device.run_shots(Circuit(1).h(0).save_matrix_product_state(pershot=True), shots=5, seed=7)
    assert sum(result.counts().values()) == ledger.receipt()["consumed_shots"] == 5
    assert len(result.matrix_product_state("matrix_product_state")) == 5
    del result
    gc.collect()
    assert ledger.receipt()["live_memory_bytes"] == ledger.receipt()["reserved_shots"] == 0
