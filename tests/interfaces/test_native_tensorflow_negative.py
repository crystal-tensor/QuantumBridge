# Copyright 2026 QuantumBridge Contributors.
# Licensed under the Apache License, Version 2.0.
# Explicit unsupported boundaries; no detached or fabricated gradients.

import builtins
import numpy as np
import pytest

from quantumbridge import PauliZ, StatevectorDevice, UnsupportedFeature
from quantumbridge.interfaces import MissingOptionalDependency, TensorFlowBridgeLimits
from quantumbridge.qml import QNode


def node(**options):
    def circuit(t, x):
        t.ry(x, 0)
        return t.expval(PauliZ(0))
    return QNode(circuit, 1, interface="tf", **options)


def test_second_derivative_rejects_instead_of_silent_zero():
    tf = pytest.importorskip("tensorflow")
    x = tf.Variable(.3)
    with tf.GradientTape() as outer:
        with tf.GradientTape() as inner:
            result = node()(x)
        first = inner.gradient(result, x)
    with pytest.raises(UnsupportedFeature, match="second derivatives"): outer.gradient(first, x)


def test_user_float_and_numpy_casts_cannot_silently_detach():
    tf = pytest.importorskip("tensorflow")
    for cast in [float, lambda x: x.numpy(), np.asarray]:
        def circuit(t, x):
            t.ry(cast(x), 0)
            return t.expval(PauliZ(0))
        with pytest.raises((TypeError, AttributeError, NotImplementedError)):
            QNode(circuit, 1, interface="tf")(tf.Variable(.3))


def test_complex_half_and_broadcast_gate_parameters_reject():
    tf = pytest.importorskip("tensorflow")
    for value in [tf.constant(.3+0j, tf.complex128), tf.constant(.3, tf.float16)]:
        with pytest.raises(UnsupportedFeature): node()(value)
    with pytest.raises(UnsupportedFeature, match="scalar"): node()(tf.constant([.2, .3]))


def test_full_state_and_finite_difference_are_not_claimed_supported():
    tf = pytest.importorskip("tensorflow")
    with pytest.raises(UnsupportedFeature): QNode(lambda t, x: t.state(), 1, interface="tf")(tf.constant(.3))
    with pytest.raises(UnsupportedFeature): node(diff_method="finite-diff")(tf.constant(.3))
    with pytest.raises(UnsupportedFeature, match="diff_method"): node(gradient_kwargs={"method": "finite-diff"})(tf.constant(.3))
    with pytest.raises(UnsupportedFeature): node(max_diff=3)(tf.constant(.3))


def test_dynamic_shapes_require_explicit_unsupported_result():
    tf = pytest.importorskip("tensorflow")
    function = tf.function(node(), autograph=False)
    with pytest.raises(UnsupportedFeature, match="static shapes"):
        function.get_concrete_function(tf.TensorSpec([None], tf.float32))


def test_native_device_and_limit_types_validate():
    tf = pytest.importorskip("tensorflow")
    with pytest.raises(UnsupportedFeature, match="native vector/density/MPS"): node(device=object())(tf.constant(.3))
    with pytest.raises(TypeError, match="TensorFlowBridgeLimits"): node(tensorflow_limits={})(tf.constant(.3))
    for value in [0, False, 1.5]:
        with pytest.raises(ValueError): TensorFlowBridgeLimits(max_input_elements=value)
    for step in [0, False, float("nan")]:
        with pytest.raises(ValueError): node(gradient_kwargs={"step": step})(tf.constant(.3))


def test_mutable_rng_and_sampled_variance_gradient_reject():
    tf = pytest.importorskip("tensorflow")
    with pytest.raises(UnsupportedFeature, match="immutable"):
        node(shots=100, seed=np.random.default_rng(3))(tf.constant(.3))
    def circuit(t, x):
        t.ry(x, 0)
        return t.var(PauliZ(0))
    with pytest.raises(UnsupportedFeature): QNode(circuit, 1, interface="tf", shots=100, seed=3)(tf.constant(.3))


def test_runtime_failure_codes_are_real_host_results(monkeypatch):
    tf = pytest.importorskip("tensorflow")
    for failure, code in [(UnsupportedFeature("injected_runtime"), 2), (MemoryError("injected_budget"), 3), (RuntimeError("injected_other"), 4)]:
        def fail(*a, **k): raise failure
        with monkeypatch.context() as patch:
            patch.setattr(StatevectorDevice, "expectation", fail)
            function = tf.function(node().tensorflow_with_status, autograph=False)
            value, status = function(tf.constant(.3))
            assert np.isnan(value) and status == code


def test_unchecked_graph_runtime_failure_raises_assertion():
    tf = pytest.importorskip("tensorflow")
    with pytest.raises(tf.errors.InvalidArgumentError, match="host execution failed"):
        tf.function(node(), autograph=False)(tf.constant(float("nan")))


def test_missing_tensorflow_does_not_become_numpy_execution(monkeypatch):
    original = builtins.__import__
    def missing(name, *args, **kwargs):
        if name == "tensorflow": raise ImportError("deliberately absent")
        return original(name, *args, **kwargs)
    monkeypatch.setattr(builtins, "__import__", missing)
    with pytest.raises(MissingOptionalDependency): node()(.3)


def test_distributed_scope_is_explicitly_unsupported():
    tf = pytest.importorskip("tensorflow")
    with tf.distribute.OneDeviceStrategy("/CPU:0").scope():
        with pytest.raises(UnsupportedFeature, match="Distributed"): node()(tf.constant(.3))


def test_raw_unrecorded_framework_parameter_cannot_enter_host():
    tf = pytest.importorskip("tensorflow")
    def circuit(t, x):
        t.circuit.metadata["global_phase"] = x
        return t.expval(PauliZ(0))
    with pytest.raises(UnsupportedFeature, match="parameter recording"):
        QNode(circuit, 1, interface="tf")(tf.constant(.3))


def test_empty_or_unknown_batch_shape_rejects():
    tf = pytest.importorskip("tensorflow")
    for values in [tf.constant(.3), tf.constant([], tf.float64)]:
        with pytest.raises(UnsupportedFeature, match="leading axis"): node().tensorflow_batch(values)


def test_eager_checked_failures_and_gradient_status_are_not_fabricated(monkeypatch):
    tf = pytest.importorskip("tensorflow")
    for failure, code in [(UnsupportedFeature("injected"), 2), (MemoryError("injected"), 3), (RuntimeError("injected"), 4)]:
        def fail(*a, **k): raise failure
        with monkeypatch.context() as patch:
            patch.setattr(StatevectorDevice, "expectation", fail)
            value, status = node().tensorflow_with_status(tf.constant(.3))
            assert np.isnan(value) and status == code
    x = tf.Variable(.3, dtype=tf.float64)
    with tf.GradientTape() as tape:
        value, status = node().tensorflow_with_status(x)
    assert status == 0
    np.testing.assert_allclose(tape.gradient(value, x), -np.sin(.3), atol=1e-11)
    x.assign(float("nan"))
    with tf.GradientTape() as tape:
        value, status = node().tensorflow_with_status(x)
    assert np.isnan(value) and status == 1 and np.isnan(tape.gradient(value, x))


def test_invalid_nonnumeric_and_captured_dtypes_reject():
    tf = pytest.importorskip("tensorflow")
    with pytest.raises(TypeError, match="numeric tensors"): node()(tf.constant("invalid"))
    with pytest.raises(UnsupportedFeature): node()(np.array(.3+0j))
    for x in [tf.constant(.3, tf.float16), tf.constant(1)]:
        def circuit(t):
            t.ry(x, 0)
            return t.expval(PauliZ(0))
        with pytest.raises(TypeError, match="float32/float64"): QNode(circuit, 1, interface="tf")()
    with pytest.raises(TypeError, match="TensorFlowBridgeLimits"):
        node(tensorflow_limits={}).tensorflow_batch(tf.ones(2))


def test_missing_tensorflow_batch_dependency_is_explicit(monkeypatch):
    original = builtins.__import__
    def missing(name, *args, **kwargs):
        if name == "tensorflow": raise ImportError("deliberately absent")
        return original(name, *args, **kwargs)
    monkeypatch.setattr(builtins, "__import__", missing)
    with pytest.raises(MissingOptionalDependency): node().tensorflow_batch([.3])
