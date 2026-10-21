# Copyright 2026 QuantumBridge Contributors.
# Licensed under the Apache License, Version 2.0.
"""Ordinary TensorFlow tapes own native kernels separately from status queries."""

import gc
import weakref
from concurrent.futures import ThreadPoolExecutor

import numpy as np
import pytest

from quantumbridge import PauliZ
from quantumbridge.interfaces.native_host import NativeHostKernel
from quantumbridge.qml import QNode


def observe_kernels(monkeypatch):
    records, original = [], NativeHostKernel.__init__
    def initialize(self, *args, **kwargs):
        original(self, *args, **kwargs)
        records.append((weakref.ref(self), self.storage_owner.pool))
    monkeypatch.setattr(NativeHostKernel, "__init__", initialize)
    return records


@pytest.mark.parametrize("mode", ["eager", "persistent", "nested_eager", "graph", "nested_graph"])
def test_ordinary_tape_and_concrete_function_have_real_final_owner(mode, monkeypatch):
    tf = pytest.importorskip("tensorflow")
    records = observe_kernels(monkeypatch)
    from quantumbridge.diff.qnode_engine import ExecutionPlan
    executed = []
    for name in ("evaluate", "jacobian", "second_derivatives"):
        original = getattr(ExecutionPlan, name)
        def run(self, *args, _original=original, _name=name, **kwargs):
            executed.append(_name)
            return _original(self, *args, **kwargs)
        monkeypatch.setattr(ExecutionPlan, name, run)
    payload = np.arange(8, dtype=float)
    def fn(tape, theta):
        tape.circuit.metadata["persistent_payload"] = payload
        tape.ry(theta, 0)
        return tape.expval(PauliZ(0))
    node = QNode(fn, 1, interface="tf", max_diff=2, diff_method="adjoint")
    point = tf.constant(.37, tf.float64)
    concrete = None
    if mode in {"graph", "nested_graph"}:
        @tf.function(autograph=False)
        def compiled(theta):
            with tf.GradientTape() as outer:
                outer.watch(theta)
                with tf.GradientTape() as inner:
                    inner.watch(theta)
                    value = node(theta)
                first = inner.gradient(value, theta)
            second = outer.gradient(first, theta) if mode == "nested_graph" else tf.zeros_like(theta)
            return value, first, second
        concrete = compiled.get_concrete_function(tf.TensorSpec((), tf.float64))
        assert executed == [], "ordinary TF tracing executed quantum work"
        value, first, second = concrete(point)
        reference, pool = records[0]
        del compiled
        gc.collect()
        assert reference() is not None
        value, first, second = concrete(point*2)
        view = reference().source.circuit.metadata["persistent_payload"][::2]
        angle = .74
    elif mode == "nested_eager":
        with tf.GradientTape() as outer:
            outer.watch(point)
            with tf.GradientTape() as inner:
                inner.watch(point)
                value = node(point)
            reference, pool = records[0]
            view = reference().source.circuit.metadata["persistent_payload"][::2]
            first = inner.gradient(value, point)
        second = outer.gradient(first, point)
        del inner, outer
        angle = .37
    else:
        with tf.GradientTape(persistent=mode == "persistent") as tape:
            tape.watch(point)
            value = node(point)
        reference, pool = records[0]
        assert reference() is not None
        view = reference().source.circuit.metadata["persistent_payload"][::2]
        first = tape.gradient(value, point)
        if mode == "persistent":
            np.testing.assert_allclose(tape.gradient(value, point), first, atol=1e-11)
        second = tf.zeros_like(point)
        del tape
        angle = .37
    np.testing.assert_allclose((value, first), (np.cos(angle), -np.sin(angle)), atol=1e-11)
    if mode in {"nested_eager", "nested_graph"}:
        np.testing.assert_allclose(second, -np.cos(angle), atol=1e-11)
        assert "second_derivatives" in executed
    assert "evaluate" in executed and "jacobian" in executed
    assert len(records) == 1
    assert pool.receipt()["persistent_owned_bytes"] == 64
    assert pool.receipt()["new_physical_allocation_count"] == 1
    del concrete, value, first, second
    gc.collect()
    assert reference() is None, "ordinary TF registration still pins the native kernel"
    assert pool.receipt()["persistent_owned_bytes"] == 64
    np.testing.assert_array_equal(view, payload[::2])
    del view
    gc.collect()
    assert pool.receipt()["persistent_owned_bytes"] == 0


def test_shared_graph_kernel_runtime_admission_failure_and_concrete_owner(monkeypatch):
    tf = pytest.importorskip("tensorflow")
    from quantumbridge.execution import UnifiedExecutionLimits as Limits, UnifiedResourceLedger
    from quantumbridge.interfaces.tensorflow_autodiff import TensorFlowBridgeLimits
    from quantumbridge.interfaces.tensorflow_graph import TensorFlowGraphKernel
    from quantumbridge.interfaces import tensorflow_graph
    from quantumbridge.diff.qnode_engine import ExecutionPlan
    payload = np.ones(8)
    def fn(tape, point):
        tape.circuit.metadata["shared"] = payload
        tape.ry(point[0], 0)
        return tape.expval(PauliZ(0))
    node = QNode(fn, 1, interface="tf", max_diff=2, diff_method="adjoint")
    point = tf.constant([.37], tf.float64)
    source, recorder, program = node._construct((point,), {}, prepare_only=True)
    kernel = NativeHostKernel(node, source, recorder, program, TensorFlowBridgeLimits(), interface="tensorflow")
    kernel.angles = []
    pool, reference = kernel.storage_owner.pool, weakref.ref(kernel)
    accounts, work = [], []
    def ledger(*args, **kwargs):
        account = UnifiedResourceLedger(*args, **kwargs)
        accounts.append(account)
        return account
    monkeypatch.setattr(tensorflow_graph, "UnifiedResourceLedger", ledger)
    original = ExecutionPlan.jacobian
    def jacobian(self, *args, **kwargs):
        work.append(1)
        return original(self, *args, **kwargs)
    monkeypatch.setattr(ExecutionPlan, "jacobian", jacobian)
    def compile_query(limit):
        owner = TensorFlowGraphKernel(kernel, tf.float64, return_status=True, request_limits=limit)
        @tf.function(autograph=False)
        def query(value):
            with tf.GradientTape() as tape:
                tape.watch(value)
                result, status = owner.evaluate(0, (value,))
            return result, tape.gradient(result, value), status
        return query
    valid, low = compile_query(Limits()), compile_query(Limits(max_total_memory_bytes=1))
    value, gradient, status = valid(point)
    assert int(status) == 0
    np.testing.assert_allclose((value[0], gradient[0]), (np.cos(.37), -np.sin(.37)), atol=1e-11)
    before = len(work)
    rejected, derivative, status = low(point)
    assert int(status) == 3 and np.all(np.isnan(rejected)) and np.all(np.isnan(derivative))
    assert len(work) == before
    value, gradient, status = valid(point*2)
    assert int(status) == 0
    np.testing.assert_allclose((value[0], gradient[0]), (np.cos(.74), -np.sin(.74)), atol=1e-11)
    assert len(work) == before + 1
    assert all(account.receipt()["request_resident_charge_bytes"] == 0 for account in accounts)
    assert any(account.receipt()["total_resident_charge_bytes"] == 64 for account in accounts)
    assert pool.receipt()["new_physical_allocation_count"] == 1
    with ThreadPoolExecutor(max_workers=2) as executor:
        outputs = list(executor.map(valid, (point, point*2)))
    for result, angle in zip(outputs, (.37, .74)):
        assert int(result[2]) == 0
        np.testing.assert_allclose((result[0][0], result[1][0]), (np.cos(angle), -np.sin(angle)), atol=1e-11)
    assert all(account.receipt()["request_resident_charge_bytes"] == 0 for account in accounts)
    assert pool.receipt()["new_physical_allocation_count"] == 1
    concrete = valid.get_concrete_function(point)
    del kernel, low
    gc.collect()
    assert reference() is not None
    value, gradient, status = valid(point)
    assert int(status) == 0
    np.testing.assert_allclose((value[0], gradient[0]), (np.cos(.37), -np.sin(.37)), atol=1e-11)
    del valid
    gc.collect()
    assert reference() is not None
    value, gradient, status = concrete(point)
    assert int(status) == 0
    np.testing.assert_allclose((value[0], gradient[0]), (np.cos(.37), -np.sin(.37)), atol=1e-11)
    del concrete
    gc.collect()
    assert reference() is None
    assert pool.receipt()["persistent_owned_bytes"] == 0


@pytest.mark.parametrize("failure, expected", [(FloatingPointError("injected"), 1), (TypeError("injected"), 4)])
def test_graph_error_protocol_does_not_change_with_owner_fix(monkeypatch, failure, expected):
    tf = pytest.importorskip("tensorflow")
    def fn(tape, point):
        tape.ry(point, 0)
        return tape.expval(PauliZ(0))
    node = QNode(fn, 1, interface="tf")
    def run(*args, **kwargs): raise failure
    monkeypatch.setattr(NativeHostKernel, "run", run)
    compiled = tf.function(node.tensorflow_with_status, autograph=False)
    value, status = compiled(tf.constant(.37, tf.float64))
    assert int(status) == expected
    assert np.isnan(value)
