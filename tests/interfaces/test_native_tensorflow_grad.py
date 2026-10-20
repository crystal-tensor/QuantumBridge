# Copyright 2026 QuantumBridge Contributors.
# Licensed under the Apache License, Version 2.0.
# Independently authored TensorFlow/native derivative contracts.

import numpy as np
import pytest

from quantumbridge import Hamiltonian, PauliX, PauliZ
from quantumbridge.diff.qnode_engine import ExecutionPlan
from quantumbridge.qml import QNode
from quantumbridge.transforms import split_non_commuting


def derivative_spy(monkeypatch):
    calls = []
    original = ExecutionPlan.jacobian
    def checked(plan, values, method=None, step=1e-6, **options):
        assert (method or plan.node.diff_method) != "finite-diff"
        calls.append(tuple(request.kind for request in plan.requests))
        return original(plan, values, method, step, **options)
    monkeypatch.setattr(ExecutionPlan, "jacobian", checked)
    return calls


def test_actual_gradient_tape_reaches_native_quantum_derivative(monkeypatch):
    tf = pytest.importorskip("tensorflow")
    calls = derivative_spy(monkeypatch)
    def circuit(tape, theta):
        tape.ry(theta, 0)
        return tape.expval(PauliZ(0))
    node = QNode(circuit, 1, interface="tf", diff_method="parameter-shift")
    theta = tf.Variable(.37, dtype=tf.float64)
    with tf.GradientTape() as recording:
        value = node(theta)
        loss = value ** 2
    gradient = recording.gradient(loss, theta)
    assert tf.is_tensor(value) and gradient is not None
    assert value.dtype == theta.dtype and gradient.dtype == theta.dtype
    np.testing.assert_allclose(value.numpy(), np.cos(.37), atol=1e-11, rtol=0)
    np.testing.assert_allclose(gradient.numpy(), -2 * np.cos(.37) * np.sin(.37), atol=1e-11, rtol=0)
    assert calls


def test_actual_gradient_tape_preserves_qwc_gate_coefficient_product_rule(monkeypatch):
    tf = pytest.importorskip("tensorflow")
    calls = derivative_spy(monkeypatch)
    def circuit(tape, theta):
        tape.ry(theta, 0)
        return tape.expval(Hamiltonian([
            (.7 + .1 * theta, PauliX(0)), (.2, PauliX(0).tensor(PauliZ(1))),
        ]))
    node = split_non_commuting(QNode(circuit, 2, interface="tensorflow", diff_method="parameter-shift"))
    theta = tf.Variable(.37, dtype=tf.float64)
    with tf.GradientTape() as recording:
        value = node(theta)
    gradient = recording.gradient(value, theta)
    assert gradient is not None
    np.testing.assert_allclose(value.numpy(), .937 * np.sin(.37), atol=1e-11, rtol=0)
    np.testing.assert_allclose(gradient.numpy(), .1 * np.sin(.37) + .937 * np.cos(.37), atol=1e-11, rtol=0)
    assert ("pauli_group",) in calls


def ry_node(**options):
    def circuit(tape, x):
        tape.ry(x, 0)
        return tape.expval(PauliZ(0))
    return QNode(circuit, 1, interface="tf", **options)


def tf_value_grad(node, value):
    tf = pytest.importorskip("tensorflow")
    with tf.GradientTape() as tape:
        tape.watch(value)
        result = node(value)
    return result, tape.gradient(result, value)


def test_float32_dtype_is_preserved():
    tf = pytest.importorskip("tensorflow")
    value, gradient = tf_value_grad(ry_node(), tf.constant(.23, tf.float32))
    assert value.dtype == gradient.dtype == tf.float32
    np.testing.assert_allclose([value, gradient], [np.cos(.23), -np.sin(.23)], atol=1e-6, rtol=0)


def test_auto_interface_uses_tensorflow_not_numpy():
    tf = pytest.importorskip("tensorflow")
    node = ry_node(); node.interface = "auto"
    value, derivative = tf_value_grad(node, tf.constant(.31, tf.float64))
    np.testing.assert_allclose([value, derivative], [np.cos(.31), -np.sin(.31)], atol=1e-11)
    assert node.last_metadata["native_tensorflow"]


def test_two_explicit_variables_get_distinct_gradients():
    tf = pytest.importorskip("tensorflow")
    def circuit(t, a, b):
        t.ry(a + 2*b, 0)
        return t.expval(PauliZ(0))
    a, b = tf.Variable(.17, dtype=tf.float64), tf.Variable(.21, dtype=tf.float64)
    with tf.GradientTape() as recording:
        result = QNode(circuit, 1, interface="tf")(a, b)
    np.testing.assert_allclose(recording.gradient(result, [a, b]), -np.sin(.59)*np.array([1, 2]), atol=1e-11)


def test_shared_parameter_occurrences_accumulate():
    tf = pytest.importorskip("tensorflow")
    def circuit(t, x):
        t.ry(x, 0); t.ry(2*x, 0)
        return t.expval(PauliZ(0))
    _, derivative = tf_value_grad(QNode(circuit, 1, interface="tf"), tf.constant(.19, tf.float64))
    np.testing.assert_allclose(derivative, -3*np.sin(.57), atol=1e-11)


def test_tensorflow_sine_preprocessing_chain_is_not_detached():
    tf = pytest.importorskip("tensorflow")
    def circuit(t, x):
        t.ry(tf.sin(x) + 2*x, 0)
        return t.expval(PauliZ(0))
    _, derivative = tf_value_grad(QNode(circuit, 1, interface="tf"), tf.constant(.29, tf.float64))
    np.testing.assert_allclose(derivative, -np.sin(np.sin(.29)+.58)*(np.cos(.29)+2), atol=1e-11)


def test_kwargs_variable_derivative():
    tf = pytest.importorskip("tensorflow")
    x = tf.Variable(.27, dtype=tf.float64)
    with tf.GradientTape() as tape:
        result = ry_node()(x=x)
    np.testing.assert_allclose(tape.gradient(result, x), -np.sin(.27), atol=1e-11)


def test_vector_input_component_chain():
    tf = pytest.importorskip("tensorflow")
    def circuit(t, x):
        t.ry(x[0]*x[1], 0)
        return t.expval(PauliZ(0))
    _, derivative = tf_value_grad(QNode(circuit, 1, interface="tf"), tf.constant([.3, .7], tf.float64))
    np.testing.assert_allclose(derivative, -np.sin(.21)*np.array([.7, .3]), atol=1e-11)


def test_nontrainable_variable_remains_unwatched():
    tf = pytest.importorskip("tensorflow")
    x = tf.Variable(.2, trainable=False, dtype=tf.float64)
    with tf.GradientTape() as tape:
        result = ry_node()(x)
    assert tape.gradient(result, x) is None


def test_unused_explicit_variable_has_verified_zero_gradient():
    tf = pytest.importorskip("tensorflow")
    def circuit(t, x):
        t.ry(.4, 0)
        return t.expval(PauliZ(0))
    _, derivative = tf_value_grad(QNode(circuit, 1, interface="tf"), tf.constant(.2, tf.float64))
    assert derivative is not None and derivative == 0


def test_closure_variable_reads_are_differentiable_packed_inputs():
    tf = pytest.importorskip("tensorflow")
    x = tf.Variable(.41, dtype=tf.float64)
    def circuit(t):
        t.ry(tf.sin(x), 0)
        return t.expval(PauliZ(0))
    node = QNode(circuit, 1, interface="tf")
    with tf.GradientTape() as tape:
        value = node()
    np.testing.assert_allclose(tape.gradient(value, x), -np.sin(np.sin(.41))*np.cos(.41), atol=1e-11)


def test_coefficient_only_derivative_has_no_fake_gate_shifts():
    tf = pytest.importorskip("tensorflow")
    def circuit(t, x):
        t.ry(.4, 0)
        return t.expval(Hamiltonian([(x*x, PauliZ(0))]))
    node = QNode(circuit, 1, interface="tf")
    _, derivative = tf_value_grad(node, tf.constant(.3, tf.float64))
    np.testing.assert_allclose(derivative, .6*np.cos(.4), atol=1e-11)
    assert node.last_metadata["native_postprocessing_derivative"]


def test_nested_result_loss_cotangents_reach_each_leaf():
    tf = pytest.importorskip("tensorflow")
    def circuit(t, x):
        t.ry(x, 0)
        return {"z": t.expval(PauliZ(0)), "extra": [t.expval(PauliX(0)), (t.probs(wires=[0]),)]}
    x = tf.Variable(.33, dtype=tf.float64)
    with tf.GradientTape() as tape:
        value = QNode(circuit, 1, interface="tf")(x)
        loss = 2*value["z"] + 3*value["extra"][0] + 4*value["extra"][1][0]["1"]
    np.testing.assert_allclose(tape.gradient(loss, x), 3*np.cos(.33), atol=1e-11)


def test_output_gradient_vector_is_not_implicitly_all_ones():
    tf = pytest.importorskip("tensorflow")
    def circuit(t, x):
        t.ry(x, 0)
        return t.expval(PauliZ(0)), t.expval(PauliX(0))
    x = tf.Variable(.24, dtype=tf.float64)
    with tf.GradientTape() as tape:
        result = QNode(circuit, 1, interface="tf")(x)
    derivative = tape.gradient(result, x, output_gradients=(tf.constant(2., tf.float64), tf.constant(-3., tf.float64)))
    np.testing.assert_allclose(derivative, -2*np.sin(.24)-3*np.cos(.24), atol=1e-11)


def test_gradient_tape_jacobian_has_input_output_axes():
    tf = pytest.importorskip("tensorflow")
    def circuit(t, x):
        t.ry(x[0], 0); t.ry(x[1], 1)
        return t.expval(PauliZ(0)), t.expval(PauliZ(1))
    x = tf.Variable([.2, .4], dtype=tf.float64)
    with tf.GradientTape(persistent=True) as tape:
        result = tf.stack(QNode(circuit, 2, interface="tf")(x))
    actual = tape.jacobian(result, x, experimental_use_pfor=False)
    np.testing.assert_allclose(actual, np.diag(-np.sin([.2, .4])), atol=1e-11)


def test_variance_derivative_matches_independent_formula():
    tf = pytest.importorskip("tensorflow")
    def circuit(t, x):
        t.ry(x, 0)
        return t.var(PauliZ(0))
    _, derivative = tf_value_grad(QNode(circuit, 1, interface="tf"), tf.constant(.4, tf.float64))
    np.testing.assert_allclose(derivative, np.sin(.8), atol=1e-11)


def test_density_device_uses_actual_native_shift():
    tf = pytest.importorskip("tensorflow")
    from quantumbridge import DensityMatrixDevice
    node = ry_node(device=DensityMatrixDevice())
    _, derivative = tf_value_grad(node, tf.constant(.4, tf.float64))
    np.testing.assert_allclose(derivative, -np.sin(.4), atol=1e-11)
    assert node.last_metadata["gradient_method"] == "parameter-shift"


def test_adjoint_and_shift_both_match_independent_math():
    tf = pytest.importorskip("tensorflow")
    for method in ("adjoint", "parameter-shift"):
        node = ry_node(diff_method=method)
        _, derivative = tf_value_grad(node, tf.constant(.4, tf.float64))
        np.testing.assert_allclose(derivative, -np.sin(.4), atol=1e-11)
        assert node.last_metadata["gradient_method"] == method


def test_tensorflow_classical_loss_reference_matches_native():
    tf = pytest.importorskip("tensorflow")
    x = tf.Variable(.22, dtype=tf.float64)
    with tf.GradientTape() as reference:
        expected_loss = tf.exp(tf.cos(x))
    with tf.GradientTape() as recording:
        actual_loss = tf.exp(ry_node()(x))
    np.testing.assert_allclose(recording.gradient(actual_loss, x), reference.gradient(expected_loss, x), atol=1e-11)


def test_real_keras_sgd_twenty_updates_change_variable_and_lower_loss():
    tf = pytest.importorskip("tensorflow")
    node, theta = ry_node(diff_method="parameter-shift"), tf.Variable(.7, dtype=tf.float64)
    optimizer = tf.keras.optimizers.SGD(learning_rate=.2)
    trace = []
    for _ in range(20):
        with tf.GradientTape() as recording:
            value = node(theta)
            loss = (value + .5)**2
        gradient = recording.gradient(loss, theta)
        trace.append((float(theta), float(loss), float(gradient)))
        optimizer.apply_gradients([(gradient, theta)])
    assert len(trace) == 20 and optimizer.iterations == 20
    assert trace[-1][1] < trace[0][1]/100 and abs(float(theta)-.7) > .1
    assert node.last_metadata["native_quantum_derivative"]


def test_tensorflow_bridge_does_not_require_upstream_quantum_sdks():
    import importlib.util
    tf = pytest.importorskip("tensorflow")
    value, derivative = tf_value_grad(ry_node(), tf.constant(.23, tf.float64))
    assert value is not None and derivative is not None
    if importlib.util.find_spec("pennylane") is None:
        assert "pennylane" not in __import__("sys").modules


def test_native_circuit_free_parameter_reconstruction():
    tf = pytest.importorskip("tensorflow")
    from quantumbridge import Circuit, Parameter
    p = Parameter("theta")
    node = QNode.from_circuit(Circuit(1).ry(2*p, 0), PauliZ(0), interface="tf")
    _, derivative = tf_value_grad(node, tf.constant(.23, tf.float64))
    np.testing.assert_allclose(derivative, -2*np.sin(.46), atol=1e-11)


def test_nested_variable_input_preserves_structure_and_unused_zero():
    tf = pytest.importorskip("tensorflow")
    x, y = tf.Variable(.2, dtype=tf.float64), tf.Variable(.4, dtype=tf.float64)
    def circuit(t, inputs):
        t.ry(inputs["x"][0], 0)
        return t.expval(PauliZ(0))
    with tf.GradientTape() as recording:
        value = QNode(circuit, 1, interface="tf")({"x": [x], "unused": y})
    gradients = recording.gradient(value, [x, y])
    np.testing.assert_allclose(gradients, [-np.sin(.2), 0], atol=1e-11)


def test_constant_no_gate_node_has_scalar_output_and_zero_derivative():
    tf = pytest.importorskip("tensorflow")
    _, derivative = tf_value_grad(QNode(lambda t, x: t.expval(PauliZ(0)), 1, interface="tf"), tf.constant(.2, tf.float64))
    assert derivative is not None and derivative == 0
