# Copyright 2026 QuantumBridge Contributors.
# Licensed under the Apache License, Version 2.0.
"""Persistent snapshots and runtime admission are different lifetimes."""

import gc
import weakref
from concurrent.futures import ThreadPoolExecutor
from threading import Barrier

import numpy as np
import pytest

from quantumbridge import PauliZ
from quantumbridge.execution import UnifiedExecutionLimits as Limits
from quantumbridge.execution.resource_context import current_resources
from quantumbridge.interfaces.framework_derivatives import execute_mapped_derivative
from quantumbridge.interfaces.native_host import NativeHostKernel
from quantumbridge.qml import QNode


def build_kernel(interface, payload):
    if interface == "jax":
        jnp = pytest.importorskip("jax.numpy")
        from quantumbridge.interfaces.jax_autodiff import JAXBridgeLimits
        point, limits = jnp.asarray([.3]), JAXBridgeLimits()
    else:
        tf = pytest.importorskip("tensorflow")
        from quantumbridge.interfaces.tensorflow_autodiff import TensorFlowBridgeLimits
        point, limits = tf.constant([.3], tf.float64), TensorFlowBridgeLimits()
    def fn(tape, point):
        tape.circuit.metadata["immutable_payload"] = payload
        tape.ry(point[0], 0)
        return tape.expval(PauliZ(0))
    node = QNode(fn, 1, interface=interface, max_diff=2, diff_method="adjoint",
        unified_limits=Limits(max_total_memory_bytes=1))
    source, recorder, program = node._construct((point,), {}, prepare_only=True)
    assert current_resources() is None
    kernel = NativeHostKernel(node, source, recorder, program, limits,
        interface="jax" if interface == "jax" else "tensorflow", validate_derivatives=False)
    kernel.angles = []
    assert current_resources() is None
    return kernel, point


def compiled_query(kernel, interface, limit):
    def host(raw):
        result = execute_mapped_derivative(kernel, raw, raw, np.ones((1, 1)),
            np.zeros((1, 1, 1)), np.ones(1), kind="hvp", input_shape=(1,),
            method="adjoint", limits=limit)
        value = np.full((1,), np.nan, dtype=raw.dtype) if result.code else np.asarray(result.derivative, dtype=raw.dtype)
        return value, np.int32(result.code)
    if interface == "jax":
        jax = pytest.importorskip("jax")
        return jax.jit(lambda value: jax.pure_callback(host,
            (jax.ShapeDtypeStruct((1,), value.dtype), jax.ShapeDtypeStruct((), np.int32)), value))
    tf = pytest.importorskip("tensorflow")
    from quantumbridge.interfaces.tensorflow_callbacks import TensorFlowCallback
    callback = TensorFlowCallback(host)
    @tf.function(autograph=False)
    def query(value):
        payload, status = callback.numpy_function((value,), (value.dtype, tf.int32))
        payload.set_shape((1,))
        status.set_shape(())
        return payload, status
    return query


@pytest.mark.parametrize("interface", ["jax", "tf"])
def test_construct_outside_request_then_runtime_reject_and_reuse(interface, monkeypatch):
    payload = np.ones(8)
    kernel, point = build_kernel(interface, payload)
    snapshot = kernel.source.circuit.metadata["immutable_payload"]
    assert not np.shares_memory(snapshot, payload), "persistent kernel still borrows mutable caller storage"
    assert not snapshot.flags.writeable
    payload[:] = 9.
    np.testing.assert_array_equal(snapshot, np.ones(8))
    pool = kernel.storage_owner.pool
    assert pool.receipt()["persistent_owned_bytes"] == 64
    from quantumbridge.diff.qnode_engine import ExecutionPlan
    calls, original = [], ExecutionPlan.second_derivatives
    def second(self, *args, **kwargs):
        calls.append(1)
        return original(self, *args, **kwargs)
    monkeypatch.setattr(ExecutionPlan, "second_derivatives", second)
    low, valid = compiled_query(kernel, interface, Limits(max_total_memory_bytes=1)), compiled_query(kernel, interface, Limits())
    rejected, status = low(point)
    assert int(status) == 3 and np.all(np.isnan(rejected)) and calls == []
    first, status = valid(point)
    assert int(status) == 0
    np.testing.assert_allclose(first, [-np.cos(.3)], atol=2e-6)
    changed, status = valid(point*2)
    assert int(status) == 0
    np.testing.assert_allclose(changed, [-np.cos(.6)], atol=2e-6)
    rejected, status = low(point)
    assert int(status) == 3 and np.all(np.isnan(rejected)) and len(calls) == 2
    assert pool.receipt()["persistent_owned_bytes"] == 64
    assert pool.receipt()["new_physical_allocation_count"] == 1
    reference = weakref.ref(kernel)
    del kernel, low
    gc.collect()
    assert reference() is not None
    again, status = valid(point)
    assert int(status) == 0
    np.testing.assert_allclose(again, first, atol=2e-6)
    del valid, snapshot
    gc.collect()
    assert reference() is None
    assert pool.receipt()["persistent_owned_bytes"] == 0


@pytest.mark.parametrize("interface", ["jax", "tf"])
def test_public_status_query_traces_one_snapshot_then_reuses_and_releases(interface, monkeypatch):
    from quantumbridge.execution.persistent_storage import PersistentStoragePool
    snapshots, original = [], PersistentStoragePool.freeze
    def freeze(self, *args, **kwargs):
        owner = original(self, *args, **kwargs)
        snapshots.append((weakref.ref(owner), self))
        return owner
    monkeypatch.setattr(PersistentStoragePool, "freeze", freeze)
    payload = np.ones(8)
    def fn(tape, point):
        tape.circuit.metadata["immutable_payload"] = payload
        tape.ry(point[0]**2, 0)
        return tape.expval(PauliZ(0))
    node = QNode(fn, 1, interface=interface, max_diff=2, diff_method="adjoint")
    if interface == "jax":
        jax, jnp = pytest.importorskip("jax"), pytest.importorskip("jax.numpy")
        point = jnp.array([.3])
        compiled = jax.jit(lambda x: node.jax_hvp_with_status(jnp.ones_like(x), x))
    else:
        tf = pytest.importorskip("tensorflow")
        point = tf.constant([.3], tf.float64)
        compiled = tf.function(lambda x: node.tensorflow_hvp_with_status(tf.ones_like(x), x), autograph=False)
    value, status = compiled(point)
    assert int(status) == 0
    np.testing.assert_allclose(value, [-2*np.sin(.09)-.36*np.cos(.09)], atol=2e-6)
    assert len(snapshots) == 1, "classical source-map tracing recopied the persistent kernel"
    reference, pool = snapshots[0]
    assert pool.receipt()["persistent_owned_bytes"] == 64
    value, status = compiled(point*2)
    assert int(status) == 0
    np.testing.assert_allclose(value, [-2*np.sin(.36)-1.44*np.cos(.36)], atol=2e-6)
    assert len(snapshots) == 1 and reference() is not None
    concrete = compiled.get_concrete_function(point) if interface == "tf" else None
    del compiled
    gc.collect()
    if concrete is not None:
        assert reference() is not None
        value, status = concrete(point)
        assert int(status) == 0
        np.testing.assert_allclose(value, [-2*np.sin(.09)-.36*np.cos(.09)], atol=2e-6)
        del concrete
        gc.collect()
    assert reference() is None
    assert pool.receipt()["persistent_owned_bytes"] == 0


@pytest.mark.parametrize("interface", ["jax", "tf"])
def test_public_status_low_resident_cap_fails_at_runtime_without_quantum_work(interface, monkeypatch):
    from quantumbridge.diff.qnode_engine import ExecutionPlan
    from quantumbridge.execution.persistent_storage import PersistentStoragePool
    pools, original = [], PersistentStoragePool.freeze
    def freeze(self, *args, **kwargs):
        owner = original(self, *args, **kwargs)
        pools.append(self)
        return owner
    monkeypatch.setattr(PersistentStoragePool, "freeze", freeze)
    def unexpected(*args, **kwargs):
        pytest.fail("resident cap failure reached quantum second derivatives")
    monkeypatch.setattr(ExecutionPlan, "second_derivatives", unexpected)
    payload = np.ones(8)
    def fn(tape, point):
        tape.circuit.metadata["immutable_payload"] = payload
        tape.ry(point[0], 0)
        return tape.expval(PauliZ(0))
    node = QNode(fn, 1, interface=interface, max_diff=2,
        unified_limits=Limits(max_total_memory_bytes=1))
    if interface == "jax":
        jax, jnp = pytest.importorskip("jax"), pytest.importorskip("jax.numpy")
        compiled = jax.jit(lambda x: node.jax_hvp_with_status(jnp.ones_like(x), x))
        value, status = compiled(jnp.array([.3]))
    else:
        tf = pytest.importorskip("tensorflow")
        compiled = tf.function(lambda x: node.tensorflow_hvp_with_status(tf.ones_like(x), x), autograph=False)
        value, status = compiled(tf.constant([.3], tf.float64))
    assert int(status) == 3 and np.all(np.isnan(value))
    assert len(pools) == 1
    assert pools[0].receipt()["persistent_owned_bytes"] == 64


def test_tf_compiled_status_payload_rejects_additional_gradient():
    tf = pytest.importorskip("tensorflow")
    def fn(tape, point):
        tape.ry(point[0], 0)
        return tape.expval(PauliZ(0))
    node = QNode(fn, 1, interface="tf", max_diff=2)
    compiled = tf.function(lambda x: node.tensorflow_hvp_with_status(tf.ones_like(x), x), autograph=False)
    point = tf.Variable([.3], dtype=tf.float64)
    _, status = compiled(point)
    assert int(status) == 0
    from quantumbridge.core.classical import UnsupportedFeature
    with pytest.raises(UnsupportedFeature, match="Differentiate the QNode"):
        with tf.GradientTape() as tape:
            value, _ = compiled(point)
        tape.gradient(value, point)


def test_shared_kernel_concurrent_native_requests_keep_separate_admission(monkeypatch):
    from quantumbridge.diff.qnode_engine import ExecutionPlan
    from quantumbridge.execution import UnifiedResourceLedger
    from quantumbridge.execution.resource_context import ResourceScope
    kernel, _ = build_kernel("jax", np.ones(8))
    pool, parent = kernel.storage_owner.pool, UnifiedResourceLedger()
    both, observations = Barrier(2), []
    original = ExecutionPlan.second_derivatives
    def second(self, *args, **kwargs):
        both.wait(timeout=10)
        observations.append(parent.receipt()["request_resident_charge_bytes"])
        both.wait(timeout=10)
        return original(self, *args, **kwargs)
    monkeypatch.setattr(ExecutionPlan, "second_derivatives", second)
    def request(angle):
        point = np.array([angle])
        with ResourceScope(parent):
            return execute_mapped_derivative(kernel, point, point, np.ones((1, 1)),
                np.zeros((1, 1, 1)), np.ones(1), kind="hvp", input_shape=(1,),
                method="adjoint", limits=Limits())
    with ThreadPoolExecutor(max_workers=2) as executor:
        results = list(executor.map(request, (.3, .6)))
    assert [result.code for result in results] == [0, 0]
    np.testing.assert_allclose([result.derivative[0] for result in results], -np.cos([.3, .6]), atol=1e-9)
    assert observations == [128, 128]
    receipt = parent.receipt()
    assert receipt["request_resident_charge_bytes"] == 0
    assert receipt["consumed_derivative_work"] > 0
    assert pool.receipt()["persistent_owned_bytes"] == 64
    assert pool.receipt()["new_physical_allocation_count"] == 1
    del results
    gc.collect()
    assert parent.receipt()["live_memory_bytes"] == 0
