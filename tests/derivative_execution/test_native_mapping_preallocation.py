# Copyright 2026 QuantumBridge Contributors.
# Licensed under the Apache License, Version 2.0.
"""Source-map allocation timing, independent of the quantum numerical engine."""

from types import SimpleNamespace

import numpy as np
import pytest

from quantumbridge import StatevectorDevice
from quantumbridge.diff.trace import flatten_tree
from quantumbridge.execution import UnifiedExecutionLimits as Limits, UnifiedResourceLedger as Ledger
from quantumbridge.execution.resource_context import ResourceScope
from quantumbridge.interfaces.framework_derivatives import execute_mapped_derivative


def kernel_with_existing_maps(own, internal=None):
    recorder = SimpleNamespace(parameters=tuple(range(len(own))),
        classical_jacobian=lambda size: own,
        classical_second=lambda size, columns: internal,
        native_values=lambda: np.zeros(len(own)))
    node = SimpleNamespace(device=StatevectorDevice())
    plan = SimpleNamespace(recorder=recorder, node=node)
    kernel = SimpleNamespace(source=object(), size=own.shape[1], spec=flatten_tree(0.)[1],
        output_size=1, node=node,
        plan=lambda *args, **kwargs: plan)
    return kernel


def test_mapped_output_budget_rejects_before_matmul_even_when_inputs_exist(monkeypatch):
    calls = []
    class NativeJacobian(np.ndarray):
        def __matmul__(self, other):
            calls.append("operator_matmul")
            return np.asarray(self) @ np.asarray(other)
    own = np.ones((32, 16)).view(NativeJacobian)
    classical = np.ones((16, 32))
    parent = Ledger(Limits(max_total_memory_bytes=own.nbytes+classical.nbytes+4096))
    with parent.reserve("existing_own", memory_bytes=own.nbytes), parent.reserve("existing_classical", memory_bytes=classical.nbytes), ResourceScope(parent):
        result = execute_mapped_derivative(kernel_with_existing_maps(own), np.zeros(32),
            np.zeros(16), classical, np.empty((16, 32, 0)), np.zeros(32),
            kind="jacobian", input_shape=(32,), method="parameter-shift", limits=None)
        assert result.code == 3
        assert calls == [], "mapped output was allocated before its resource rejection"
        assert parent.receipt()["live_memory_bytes"] == own.nbytes+classical.nbytes
    assert parent.receipt()["live_memory_bytes"] == 0


def test_second_mapping_budget_rejects_before_unreserved_einsum(monkeypatch):
    from quantumbridge.interfaces import framework_derivatives as module
    own, classical = np.ones((2, 64)), np.ones((64, 1))
    internal = np.ones((2, 64, 64))
    kernel = kernel_with_existing_maps(own, internal)
    calls, original = [], np.einsum
    def einsum(*args, **kwargs):
        calls.append(args[0])
        return original(*args, **kwargs)
    monkeypatch.setattr(np, "einsum", einsum)
    # Isolate source-map preparation: real executor preflight must still reject
    # the prepared derivative/storage requirement after the mapper returns.
    monkeypatch.setattr(module, "finish_derivative", lambda *a, **k:
        SimpleNamespace(plan=None, work={"tape_count": 0, "physical_shots": 0,
            "derivative_work": 0}, buffer_bytes=1024, device_bytes=0))
    parent = Ledger(Limits(max_total_memory_bytes=1024))
    with ResourceScope(parent):
        result = execute_mapped_derivative(kernel, np.zeros(1), np.zeros(64), classical,
            np.zeros((64, 1, 1)), np.zeros(1), kind="hessian", input_shape=(1,),
            method="parameter-shift", limits=None)
    assert result.code == 3
    assert calls == [], "second contractions ran before their storage budget was checked"
    assert parent.receipt()["live_memory_bytes"] == 0


def test_packed_direction_denies_before_matmul_and_plan_construction(monkeypatch):
    kernel = kernel_with_existing_maps(np.ones((4, 4)))
    kernel.plan = lambda *a, **k: pytest.fail("plan built before packed direction allocation check")
    raw, packed = np.zeros(2), np.zeros(4)
    classical, second, direction = np.ones((4, 2)), np.zeros((4, 2, 1)), np.ones(2)
    monkeypatch.setattr(np, "matmul", lambda *a, **k: pytest.fail("unreserved packed direction"))
    result = execute_mapped_derivative(kernel, raw, packed, classical, second, direction,
        kind="hvp", input_shape=(2,), method="parameter-shift", limits=Limits(max_total_memory_bytes=31))
    assert result.code == 3 and result.receipt["live_memory_bytes"] == 0


def test_native_jacobian_denies_before_materializing_recorder_map(monkeypatch):
    kernel = kernel_with_existing_maps(np.ones((8, 4)))
    plan = kernel.plan()
    calls = []
    def getter(size):
        calls.append(size)
        raise AssertionError("native recorder Jacobian materialized before checking its 256 bytes")
    plan.recorder.classical_jacobian = getter
    result = execute_mapped_derivative(kernel, np.zeros(2), np.zeros(4), np.ones((4, 2)),
        np.empty((4, 2, 0)), np.zeros(2), kind="jacobian", input_shape=(2,),
        method="parameter-shift", limits=Limits(max_total_memory_bytes=255))
    assert result.code == 3 and calls == [] and result.receipt["live_memory_bytes"] == 0
