# Copyright 2026 QuantumBridge Contributors.
# Licensed under the Apache License, Version 2.0.
# Independently authored graph, Variable and static shape contracts.

import numpy as np
import pytest

from quantumbridge import Hamiltonian, PauliX, PauliZ
from quantumbridge.qml import QNode
from quantumbridge.transforms import split_non_commuting


def framework():
    return pytest.importorskip("tensorflow")


def make_node(**options):
    def circuit(t, x):
        t.ry(x, 0)
        return t.expval(PauliZ(0))
    return QNode(circuit, 1, interface="tf", **options)


def test_concrete_function_traces_without_simulation(monkeypatch):
    tf = framework()
    from quantumbridge.diff.qnode_engine import ExecutionPlan
    with monkeypatch.context() as patch:
        patch.setattr(ExecutionPlan, "evaluate", lambda *a, **k: pytest.fail("quantum work during tracing"))
        function = tf.function(make_node(), autograph=False).get_concrete_function(tf.TensorSpec((), tf.float64))
    np.testing.assert_allclose(function(tf.constant(.3, tf.float64)), np.cos(.3), atol=1e-11)


def test_same_static_graph_reads_fresh_runtime_values_and_gradients():
    tf = framework()
    node = make_node()
    @tf.function(input_signature=[tf.TensorSpec((), tf.float64)], autograph=False)
    def execute(x):
        with tf.GradientTape() as tape:
            tape.watch(x)
            value = node(x)
        return value, tape.gradient(value, x)
    for x in [.2, .7]:
        np.testing.assert_allclose(execute(tf.constant(x, tf.float64)), [np.cos(x), -np.sin(x)], atol=1e-11)
    assert execute.experimental_get_tracing_count() == 1
    assert node.last_metadata["trace_configuration_only"]
    assert node.last_metadata["observed_callback_count"] == "not reported from tracing"


def test_graph_variable_assignment_is_not_frozen():
    tf = framework()
    x = tf.Variable(.2, dtype=tf.float64)
    node = make_node()
    @tf.function(autograph=False)
    def execute():
        with tf.GradientTape() as tape:
            value = node(x)
        return value, tape.gradient(value, x)
    np.testing.assert_allclose(execute(), [np.cos(.2), -np.sin(.2)], atol=1e-11)
    x.assign(.7)
    np.testing.assert_allclose(execute(), [np.cos(.7), -np.sin(.7)], atol=1e-11)


def test_graph_tensorflow_preprocessing_and_coefficient_product_rule():
    tf = framework()
    def circuit(t, x):
        t.ry(tf.sin(x), 0)
        return t.expval(Hamiltonian([(x*x, PauliX(0)), (.2, PauliZ(0))]))
    node = split_non_commuting(QNode(circuit, 1, interface="tf"))
    @tf.function(input_signature=[tf.TensorSpec((), tf.float64)], autograph=False)
    def execute(x):
        with tf.GradientTape() as tape:
            tape.watch(x)
            value = node(x)
        return value, tape.gradient(value, x)
    for x in [.2, .7]:
        a = np.sin(x)
        expected = [x*x*np.sin(a)+.2*np.cos(a), 2*x*np.sin(a)+(x*x*np.cos(a)-.2*np.sin(a))*np.cos(x)]
        np.testing.assert_allclose(execute(tf.constant(x, tf.float64)), expected, atol=1e-11)


def test_graph_nested_output_and_vector_cotangents():
    tf = framework()
    def circuit(t, x):
        t.ry(x, 0)
        return {"values": (t.expval(PauliZ(0)), t.expval(PauliX(0)))}
    node = QNode(circuit, 1, interface="tf")
    @tf.function(input_signature=[tf.TensorSpec((), tf.float32)], autograph=False)
    def execute(x):
        with tf.GradientTape() as tape:
            tape.watch(x)
            y = tf.stack(node(x)["values"])
        return y, tape.gradient(y, x, output_gradients=tf.constant([2., -3.]))
    result, gradient = execute(tf.constant(.3))
    np.testing.assert_allclose(result, [np.cos(.3), np.sin(.3)], atol=1e-6)
    np.testing.assert_allclose(gradient, -2*np.sin(.3)-3*np.cos(.3), atol=1e-6)


def test_bounded_batch_maps_and_differentiates_each_item():
    tf = framework()
    node, x = make_node(), tf.Variable([.2, .7], dtype=tf.float64)
    with tf.GradientTape() as tape:
        value = node.tensorflow_batch(x)
        loss = tf.reduce_sum(value)
    np.testing.assert_allclose(value, np.cos([.2, .7]), atol=1e-11)
    np.testing.assert_allclose(tape.gradient(loss, x), -np.sin([.2, .7]), atol=1e-11)
    assert node.last_metadata["batch_size"] == 2


def test_graph_snapshot_does_not_read_mutated_diff_options():
    tf = framework()
    node = make_node(diff_method="parameter-shift")
    @tf.function(input_signature=[tf.TensorSpec((), tf.float64)], autograph=False)
    def execute(x):
        with tf.GradientTape() as tape:
            tape.watch(x)
            value = node(x)
        return value, tape.gradient(value, x)
    first = execute(tf.constant(.3, tf.float64))
    node.gradient_kwargs["method"] = "finite-diff"
    node.diff_method = "finite-diff"
    np.testing.assert_allclose(execute(tf.constant(.3, tf.float64)), first, atol=0, rtol=0)


def test_graph_checked_nonfinite_status_recovers_on_valid_input():
    tf = framework()
    node = make_node()
    function = tf.function(node.tensorflow_with_status, input_signature=[tf.TensorSpec((), tf.float64)], autograph=False)
    for x in [float("nan"), float("inf")]:
        value, status = function(tf.constant(x, tf.float64))
        assert np.isnan(value) and status == 1
    value, status = function(tf.constant(.2, tf.float64))
    assert status == 0
    np.testing.assert_allclose(value, np.cos(.2), atol=1e-11)


def test_graph_optimizer_updates_read_native_gradients():
    tf = framework()
    node, x = make_node(), tf.Variable(.8, dtype=tf.float64)
    optimizer = tf.keras.optimizers.Adam(learning_rate=.1)
    @tf.function(autograph=False)
    def step():
        with tf.GradientTape() as tape:
            loss = (node(x)+.5)**2
        gradient = tape.gradient(loss, x)
        optimizer.apply_gradients([(gradient, x)])
        return loss, gradient
    trace = [step() for _ in range(20)]
    assert trace[-1][0] < trace[0][0]/5 and abs(float(x)-.8) > .1
    assert optimizer.iterations == 20
