# Copyright 2026 QuantumBridge Contributors.
# Licensed under the Apache License, Version 2.0.
# Independent second-order contracts, persisted before runtime implementation.

import numpy as np
import pytest

from quantumbridge import Hamiltonian, PauliX, PauliZ
from quantumbridge.qml import QNode
from quantumbridge.transforms import split_non_commuting


def test_native_ry_hessian_matches_independent_second_derivative():
    def circuit(t, theta):
        t.ry(theta, 0)
        return t.expval(PauliZ(0))
    node = QNode(circuit, 1, max_diff=2, diff_method="parameter-shift")
    actual = node.compute_hessian(.37)
    np.testing.assert_allclose(actual, -np.cos(.37), atol=1e-11, rtol=0)


def test_actual_tensorflow_nested_tapes_reach_native_second_derivative():
    tf = pytest.importorskip("tensorflow")
    def circuit(t, theta):
        t.ry(theta, 0)
        return t.expval(PauliZ(0))
    node = QNode(circuit, 1, interface="tf", max_diff=2, diff_method="parameter-shift")
    theta = tf.Variable(.37, dtype=tf.float64)
    with tf.GradientTape() as outer:
        with tf.GradientTape() as inner:
            value = node(theta)
        first = inner.gradient(value, theta)
    second = outer.gradient(first, theta)
    assert first is not None and second is not None
    np.testing.assert_allclose([value, first, second], [np.cos(.37), -np.sin(.37), -np.cos(.37)], atol=1e-11, rtol=0)


def test_actual_torch_double_backward_reaches_native_second_derivative():
    torch = pytest.importorskip("torch")
    def circuit(t, theta):
        t.ry(theta, 0)
        return t.expval(PauliZ(0))
    node = QNode(circuit, 1, interface="torch", max_diff=2, diff_method="parameter-shift")
    theta = torch.tensor(.37, dtype=torch.float64, requires_grad=True)
    value = node(theta)
    first = torch.autograd.grad(value, theta, create_graph=True)[0]
    second = torch.autograd.grad(first, theta)[0]
    np.testing.assert_allclose([value.detach(), first.detach(), second.detach()],
                               [np.cos(.37), -np.sin(.37), -np.cos(.37)], atol=1e-11, rtol=0)


def test_actual_transformed_qwc_tensorflow_second_order_full_product_rule():
    tf = pytest.importorskip("tensorflow")
    def circuit(t, theta):
        t.ry(tf.sin(theta) + 2*theta, 0)
        return t.expval(Hamiltonian([(.7+.1*theta, PauliX(0)), (.2, PauliX(0).tensor(PauliZ(1)))]))
    node = split_non_commuting(QNode(circuit, 2, interface="tf", max_diff=2, diff_method="parameter-shift"))
    theta = tf.Variable(.37, dtype=tf.float64)
    with tf.GradientTape() as outer:
        with tf.GradientTape() as inner:
            value = node(theta)
        first = inner.gradient(value, theta)
    second = outer.gradient(first, theta)
    a, g, gp = .937, np.sin(.37)+.74, np.cos(.37)+2
    expected = [a*np.sin(g), .1*np.sin(g)+a*np.cos(g)*gp,
                .2*np.cos(g)*gp-a*np.sin(g)*gp**2-a*np.cos(g)*np.sin(.37)]
    assert first is not None and second is not None
    np.testing.assert_allclose([value, first, second], expected, atol=1e-10, rtol=0)
