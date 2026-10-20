# Copyright 2026 QuantumBridge Contributors.
# Licensed under the Apache License, Version 2.0.
# Independent public-API oracles; no upstream implementation/test source ports.

import numpy as np
import pytest

from quantumbridge import Hamiltonian, PauliX, PauliZ
from quantumbridge.qml import QNode
from quantumbridge.transforms import split_non_commuting


def frameworks():
    tf, pl = pytest.importorskip("tensorflow"), pytest.importorskip("pennylane")
    return tf, pl


def gradient(tf, function, value):
    x = tf.Variable(value, dtype=tf.float64)
    with tf.GradientTape() as tape:
        y = function(x)
    return y, tape.gradient(y, x)


def compare(native, public, *, wires=1, transformed=False, value=.37):
    tf, pl = frameworks()
    a = QNode(native, wires, interface="tf", diff_method="parameter-shift")
    b = pl.QNode(public(pl, tf), pl.device("default.qubit", wires=wires), interface="tf", diff_method="parameter-shift")
    if transformed: a, b = split_non_commuting(a), pl.transforms.split_non_commuting(b)
    left, right = gradient(tf, a, value), gradient(tf, b, value)
    np.testing.assert_allclose(left[0], right[0], atol=2e-10, rtol=0)
    np.testing.assert_allclose(left[1], right[1], atol=2e-10, rtol=0)


def test_public_legacy_tf_single_gate_actual_gradient():
    def native(t, x):
        t.ry(x, 0)
        return t.expval(PauliZ(0))
    def public(pl, tf):
        def circuit(x):
            pl.RY(x, wires=0)
            return pl.expval(pl.Z(0))
        return circuit
    compare(native, public)


def test_public_legacy_tf_nonlinear_shared_preprocessing():
    tf, _ = frameworks()
    def native(t, x):
        t.ry(tf.sin(x), 0); t.ry(2*x, 0)
        return t.expval(PauliZ(0))
    def public(pl, tf):
        def circuit(x):
            pl.RY(tf.sin(x), wires=0); pl.RY(2*x, wires=0)
            return pl.expval(pl.Z(0))
        return circuit
    compare(native, public)


def test_public_legacy_tf_qwc_two_groups():
    def native(t, x):
        t.ry(x, 0)
        return t.expval(Hamiltonian([(.7, PauliX(0)), (.2, PauliZ(0))]))
    def public(pl, tf):
        def circuit(x):
            pl.RY(x, wires=0)
            return pl.expval(.7*pl.X(0)+.2*pl.Z(0))
        return circuit
    compare(native, public, transformed=True)


def test_public_legacy_tf_gate_coefficient_product_rule():
    def native(t, x):
        t.ry(x, 0)
        return t.expval(Hamiltonian([(.7+.1*x, PauliX(0)), (.2, PauliX(0).tensor(PauliZ(1)))]))
    def public(pl, tf):
        def circuit(x):
            pl.RY(x, wires=0)
            return pl.expval(pl.Hamiltonian([tf.constant(.7, tf.float64)+tf.constant(.1, tf.float64)*x, tf.constant(.2, tf.float64)], [pl.X(0), pl.X(0)@pl.Z(1)]))
        return circuit
    compare(native, public, wires=2, transformed=True)


def test_public_legacy_tf_weight_vector():
    def native(t, x):
        t.ry(x[0], 0); t.rx(x[1], 0)
        return t.expval(PauliZ(0))
    def public(pl, tf):
        def circuit(x):
            pl.RY(x[0], wires=0); pl.RX(x[1], wires=0)
            return pl.expval(pl.Z(0))
        return circuit
    compare(native, public, value=[.2, .4])


def test_public_legacy_tf_probability_cotangent():
    tf, pl = frameworks()
    def native(t, x):
        t.ry(x, 0)
        return t.probs(wires=[0])
    def public(x):
        pl.RY(x, wires=0)
        return pl.probs(wires=[0])
    a = QNode(native, 1, interface="tf", diff_method="parameter-shift")
    b = pl.QNode(public, pl.device("default.qubit", wires=1), interface="tf", diff_method="parameter-shift")
    first = gradient(tf, lambda x: 2*a(x)["0"]-3*a(x)["1"], .37)
    second = gradient(tf, lambda x: tf.reduce_sum(b(x)*tf.constant([2., -3.], tf.float64)), .37)
    np.testing.assert_allclose(first, second, atol=2e-10, rtol=0)
