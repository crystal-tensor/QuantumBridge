# Copyright 2026 QuantumBridge Contributors.
# Licensed under the Apache License, Version 2.0.
"""Independently authored public-API deferred-measurement oracles."""

import numpy as np
import pytest

qml = pytest.importorskip("pennylane")

from quantumbridge.qml import QNode
from quantumbridge.transforms import defer_measurements, split_non_commuting
from quantumbridge.utils.math import PauliZ, Hamiltonian, PauliString


def oracle(function, width=4, shots=None):
    node = qml.QNode(function, qml.device("default.qubit", wires=width, seed=29, shots=shots),
                     interface="autograd", diff_method="parameter-shift")
    return qml.defer_measurements(node)


def probabilities(mapping):
    return np.asarray([mapping[label] for label in sorted(mapping)])


def test_public_reused_measurement_wire_matches_native_logical_probabilities():
    def public():
        qml.Hadamard(0)
        m = qml.measure(0)
        qml.Hadamard(0)
        qml.cond(m, qml.PauliX)(1)
        return qml.probs(wires=[0, 1])
    def native(t):
        t.h(0)
        m = t.measure(0)
        t.h(0)
        t.cond(m, lambda b: b.x(1))
        return t.probs([0, 1])
    np.testing.assert_allclose(probabilities(defer_measurements(QNode(native, 2))()), oracle(public)(), atol=1e-12)


def test_public_conditional_else_and_zero_controls_match_native_reduced_density():
    def public():
        qml.RY(.4, 0)
        m = qml.measure(0)
        qml.cond(m == 0, qml.PauliY, qml.Hadamard)(1)
        return qml.density_matrix(wires=[1])
    def native(t):
        t.ry(.4, 0)
        m = t.measure(0)
        t.cond(m == 0, lambda b: b.y(1), lambda b: b.h(1))
        return t.density_matrix([1])
    np.testing.assert_allclose(defer_measurements(QNode(native, 2))(), oracle(public)(), atol=1e-12)


def test_public_boolean_two_measurement_records_have_matching_quantum_output():
    def public():
        qml.Hadamard(0)
        qml.RY(.7, 1)
        a, b = qml.measure(0), qml.measure(1)
        qml.cond(a ^ b, qml.RY)(.8, 2)
        return qml.density_matrix(wires=[2])
    def native(t):
        t.h(0)
        t.ry(.7, 1)
        a, b = t.measure(0), t.measure(1)
        t.cond(a ^ b, lambda branch: branch.ry(.8, 2))
        return t.density_matrix([2])
    np.testing.assert_allclose(defer_measurements(QNode(native, 3))(), oracle(public, width=5)(), atol=1e-12)


def test_public_native_deferred_gradient_matches_actual_public_parameter_shift():
    def public(x):
        qml.RY(x, 0)
        m = qml.measure(0)
        qml.cond(m, qml.PauliX)(1)
        return qml.expval(qml.PauliZ(1))
    def native(t, x):
        t.ry(x, 0)
        m = t.measure(0)
        t.cond(m, lambda b: b.x(1))
        return t.expval(PauliZ(1))
    expected = qml.grad(oracle(public))(qml.numpy.array(.37, requires_grad=True))
    assert defer_measurements(QNode(native, 2)).gradient(.37) == pytest.approx(float(expected), abs=1e-12)


def test_public_conditional_rotation_shared_nonlinear_gradient_preserves_the_graph():
    def public(x):
        qml.RY(x, 0)
        m = qml.measure(0)
        qml.cond(m, qml.RY)(qml.numpy.sin(x)+.2, 1)
        return qml.expval(qml.PauliZ(1))
    def native(t, x):
        t.ry(x, 0)
        m = t.measure(0)
        t.cond(m, lambda b: b.ry(np.sin(x)+.2, 1))
        return t.expval(PauliZ(1))
    expected = qml.grad(oracle(public))(qml.numpy.array(.37, requires_grad=True))
    assert defer_measurements(QNode(native, 2)).gradient(.37) == pytest.approx(float(expected), abs=1e-12)


def test_public_measurement_record_distribution_is_not_the_reused_quantum_wire():
    def public():
        qml.RY(.37, 0)
        m = qml.measure(0)
        qml.Hadamard(0)
        return qml.probs(op=m)
    def native(t):
        t.ry(.37, 0)
        m = t.measure(0)
        t.h(0)
        return t.probs(records=m)
    np.testing.assert_allclose(probabilities(defer_measurements(QNode(native, 1))()), oracle(public)(), atol=1e-12)


def test_public_finite_shot_joint_records_agree_statistically_not_sample_by_sample():
    def public():
        qml.Hadamard(0)
        m = qml.measure(0)
        qml.Hadamard(0)
        qml.cond(m, qml.PauliX)(1)
        last = qml.measure(1)
        return qml.probs(op=[m, last])
    def native(t):
        t.h(0)
        m = t.measure(0)
        t.h(0)
        t.cond(m, lambda b: b.x(1))
        return t.probs([1], records=m)
    expected = oracle(public, shots=3001)()
    actual = probabilities(defer_measurements(QNode(native, 2, shots=3001, seed=29))())
    np.testing.assert_allclose(actual, expected, atol=.06, rtol=0)
    assert actual[1] == actual[2] == 0.


def test_public_defer_qwc_trainable_coefficient_and_gate_product_rule_match():
    def public(x):
        qml.RY(x, 0)
        m = qml.measure(0)
        qml.cond(m, qml.PauliX)(1)
        return qml.expval(qml.Hamiltonian([x, x*x], [qml.PauliZ(1), qml.Identity(0)]))
    def native(t, x):
        t.ry(x, 0)
        m = t.measure(0)
        t.cond(m, lambda b: b.x(1))
        return t.expval(Hamiltonian([(x, PauliZ(1)), (x*x, PauliString([]))]))
    expected = qml.grad(oracle(public))(qml.numpy.array(.37, requires_grad=True))
    node = split_non_commuting(defer_measurements(QNode(native, 2)))
    assert node.gradient(.37) == pytest.approx(float(expected), abs=1e-12)
