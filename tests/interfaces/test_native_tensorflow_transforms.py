# Copyright 2026 QuantumBridge Contributors.
# Licensed under the Apache License, Version 2.0.
# Independent native transformation and TensorFlow graph composition tests.

import numpy as np
import pytest

from quantumbridge import Hamiltonian, PauliX, PauliZ, templates
from quantumbridge.qml import QNode
from quantumbridge.transforms import (TransformProgram, cancel_inverses, compile, defer_measurements,
                                     merge_rotations, split_non_commuting, transform)


def evaluate(circuit, x=.3, *, stages=(), width=1, method="parameter-shift"):
    tf = pytest.importorskip("tensorflow")
    node = TransformProgram(stages)(QNode(circuit, width, interface="tf", diff_method=method))
    x = tf.constant(x, tf.float64)
    with tf.GradientTape() as tape:
        tape.watch(x)
        value = node(x)
    return value, tape.gradient(value, x), node


def test_real_children_and_reverse_processing_jacobians():
    @transform
    def fork(t):
        a, b = t.copy(), t.copy(); b.circuit.ry(.2, 0)
        return (a, b), lambda y: y[0]+2*y[1]
    def circuit(t, x):
        t.ry(x, 0)
        return t.expval(PauliZ(0))
    value, grad, node = evaluate(circuit, stages=[fork])
    np.testing.assert_allclose([value, grad], [np.cos(.3)+2*np.cos(.5), -np.sin(.3)-2*np.sin(.5)], atol=1e-11)
    assert node.last_metadata["executed_tape_count"] == 2


def test_nonlinear_postprocessing_chain_is_native():
    @transform
    def square(t):
        return (t,), lambda y: y[0]**2
    def circuit(t, x):
        t.ry(x, 0)
        return t.expval(PauliZ(0))
    value, grad, node = evaluate(circuit, stages=[square])
    np.testing.assert_allclose([value, grad], [np.cos(.3)**2, -np.sin(.6)], atol=1e-11)
    assert node.last_metadata["native_postprocessing_derivative"]


def test_postprocessing_order_is_reverse_of_transform_stages():
    @transform
    def twice(t): return (t,), lambda y: 2*y[0]
    @transform
    def offset(t): return (t,), lambda y: y[0]+3
    def circuit(t, x):
        t.ry(x, 0)
        return t.expval(PauliZ(0))
    value, grad, node = evaluate(circuit, stages=[twice, offset])
    np.testing.assert_allclose([value, grad], [2*(np.cos(.3)+3), -2*np.sin(.3)], atol=1e-11)
    assert node.last_metadata["postprocessing_order"] == [1, 0]


def test_cancel_merge_compile_qwc_preserves_tensorflow_source_derivative():
    tf = pytest.importorskip("tensorflow")
    def circuit(t, x):
        t.x(0); t.x(0); t.ry(tf.sin(x), 0); t.ry(2*x, 0)
        return t.expval(Hamiltonian([(.7, PauliZ(0)), (.2, PauliX(0))]))
    value, grad, node = evaluate(circuit, stages=[cancel_inverses, merge_rotations, compile(basis_set={"RY", "RZ", "CX"}), split_non_commuting])
    a = np.sin(.3)+.6
    np.testing.assert_allclose([value, grad], [.7*np.cos(a)+.2*np.sin(a), (-.7*np.sin(a)+.2*np.cos(a))*(2+np.cos(.3))], atol=1e-11)
    assert node.last_metadata["transform_count"] == 4


def test_fresh_coefficient_primals_are_not_stale_group_weights():
    def circuit(t, x):
        t.ry(.4, 0)
        return t.expval(Hamiltonian([(x, PauliX(0)), (x*x, PauliZ(0))]))
    for x in [0., .3, -.7]:
        value, grad, _ = evaluate(circuit, x, stages=[split_non_commuting])
        np.testing.assert_allclose([value, grad], [x*np.sin(.4)+x*x*np.cos(.4), np.sin(.4)+2*x*np.cos(.4)], atol=1e-11)


def test_same_variable_in_gate_and_multiple_coefficients():
    def circuit(t, x):
        t.ry(x, 0)
        return t.expval(Hamiltonian([(x, PauliX(0)), (x*x, PauliZ(0))]))
    value, grad, _ = evaluate(circuit, stages=[split_non_commuting])
    np.testing.assert_allclose([value, grad], [.3*np.sin(.3)+.09*np.cos(.3), np.sin(.3)+.9*np.cos(.3)-.09*np.sin(.3)], atol=1e-11)


def test_template_tensor_array_uses_native_recording():
    def circuit(t, x):
        templates.AngleEmbedding(x, [0, 1], rotation="Y").apply(t)
        return t.expval(PauliZ(0).tensor(PauliZ(1)))
    _, grad, _ = evaluate(circuit, [.2, .4], width=2, stages=[split_non_commuting])
    np.testing.assert_allclose(grad, [-np.sin(.2)*np.cos(.4), -np.cos(.2)*np.sin(.4)], atol=1e-11)


def test_deferred_measurement_reused_wire_derivative():
    def circuit(t, x):
        t.ry(x, 0); record = t.measure(0); t.h(0)
        t.cond(record, lambda branch: branch.x(1))
        return t.expval(PauliZ(1))
    value, grad, node = evaluate(circuit, width=2, stages=[defer_measurements, split_non_commuting])
    np.testing.assert_allclose([value, grad], [np.cos(.3), -np.sin(.3)], atol=1e-11)
    assert node.last_metadata["deferred_measurements"][0]["ancilla_count"] == 1


def test_record_only_probability_derivative():
    tf = pytest.importorskip("tensorflow")
    def circuit(t, x):
        t.ry(x, 0); record = t.measure(0); t.h(0)
        return t.probs(records=[record])
    node = defer_measurements(QNode(circuit, 1, interface="tf", diff_method="parameter-shift"))
    x = tf.Variable(.3, dtype=tf.float64)
    with tf.GradientTape() as tape:
        p = node(x)["1"]
    np.testing.assert_allclose(tape.gradient(p, x), .5*np.sin(.3), atol=1e-11)


def test_transformed_adjoint_and_native_reference_agree():
    def circuit(t, x):
        t.ry(x, 0)
        return t.expval(Hamiltonian([(.7, PauliZ(0)), (.2, PauliX(0))]))
    value, grad, node = evaluate(circuit, method="adjoint", stages=[split_non_commuting])
    ref = QNode(circuit, 1)
    np.testing.assert_allclose([value, grad], [ref(.3), ref.gradient(.3)], atol=1e-11)
    assert node.last_metadata["gradient_method"] == "adjoint"
