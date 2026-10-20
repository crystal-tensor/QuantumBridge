# Copyright 2026 QuantumBridge Contributors.
# Licensed under the Apache License, Version 2.0.
"""Independent mathematical Device contracts, not SDK implementation fixtures."""

import numpy as np

from quantumbridge import Hamiltonian, PauliX, PauliZ, StatevectorDevice
from quantumbridge.utils.math import PauliString
from quantumbridge.execution import DerivativeExecutionRequest as Request
from quantumbridge.qml import QNode
from quantumbridge.transforms import split_non_commuting


def second(fn, point, width=1, *, method="second_adjoint", kind="hessian", tangent=None, shots=None):
    node = QNode(fn, width, max_diff=2, shots=shots, seed=17 if shots else None)
    return node.device.execute_derivatives(Request(node, (point,), derivative_order=2,
        derivative_kind=kind, method=method, tangent=tangent))


def test_nonlinear_two_input_full_hessian_and_directional_product():
    def fn(t, x):
        t.ry(x[0]*x[1], 0)
        return t.expval(PauliZ(0))
    point = np.array([.2, .3])
    first = np.array([.3, .2])
    expected = -np.cos(.06)*np.outer(first, first)-np.sin(.06)*np.array([[0., 1.], [1., 0.]])
    full = second(fn, point)
    product = second(fn, point, kind="hvp", tangent=np.array([.4, -.1]))
    np.testing.assert_allclose(full.derivative, expected, atol=1e-12)
    np.testing.assert_allclose(product.derivative, expected @ [.4, -.1], atol=1e-12)


def test_live_coefficient_curvature_and_gate_cross_partial():
    def fn(t, x):
        t.ry(x[0], 0)
        return t.expval(Hamiltonian([(.7+x[1]**2, PauliX(0))]))
    x, y = .2, .3
    expected = np.array([[-(.7+y*y)*np.sin(x), 2*y*np.cos(x)],
                         [2*y*np.cos(x), 2*np.sin(x)]])
    np.testing.assert_allclose(second(fn, np.array([x, y])).derivative, expected, atol=1e-12)


def test_complex_observable_fixed_phase_is_not_discarded_or_misconjugated():
    matrix = np.array([[.4, .2-.3j], [.2+.3j, -.4]])
    def fn(t, x):
        t.circuit.global_phase = .43
        t.ry(x, 0)
        return t.expval(matrix)
    np.testing.assert_allclose(second(fn, .3).derivative, -.2*np.sin(.3)-.4*np.cos(.3), atol=1e-12)


def test_analytic_variance_second_derivative_retains_mean_terms():
    def fn(t, x):
        t.ry(x, 0)
        return t.var(PauliZ(0))
    for method in ("second_adjoint", "parameter-shift"):
        np.testing.assert_allclose(second(fn, .3, method=method).derivative, 2*np.cos(.6), atol=1e-12)


def test_ordered_probability_hessian_matches_measurement_wire_order():
    def fn(t, x):
        t.ry(x, 0)
        t.x(1)
        return t.probs([1, 0])
    result = second(fn, .3, width=2)
    assert tuple(result.derivative) == ("00", "01", "10", "11")
    np.testing.assert_allclose(list(result.derivative.values()), [0., 0., -.5*np.cos(.3), .5*np.cos(.3)], atol=1e-12)


def test_controlled_rotation_keeps_half_and_full_frequencies():
    def fn(t, x):
        t.h(0)
        t.cry(x, 0, 1)
        return t.expval(Hamiltonian([(1., PauliX(0)), (.3, PauliZ(1))]))
    expected = -.25*np.cos(.15)-.15*np.cos(.3)
    np.testing.assert_allclose(second(fn, .3, width=2).derivative, expected, atol=1e-12)


def test_identity_coefficient_mixed_curvature_has_no_quantum_work():
    def fn(t, x):
        return t.expval(Hamiltonian([(x[0]*x[1], PauliString(()))]))
    node = split_non_commuting(QNode(fn, 1, max_diff=2))
    result = node.device.execute_derivatives(Request(node, (np.array([.2, .3]),),
        derivative_order=2, derivative_kind="hvp", method="second_adjoint", tangent=np.array([.4, -.1])))
    np.testing.assert_allclose(result.derivative, [-.1, .4], atol=1e-12)
    assert result.receipt["consumed_tapes"] == result.receipt["consumed_shots"] == 0


def test_seeded_finite_shift_hvp_is_an_estimate_with_actual_shots():
    def fn(t, x):
        t.ry(x, 0)
        return t.expval(PauliZ(0))
    result = second(fn, .3, kind="hvp", tangent=.4, shots=4096, method="parameter-shift")
    np.testing.assert_allclose(result.derivative, -.4*np.cos(.3), atol=.04, rtol=0)
    assert result.metadata["gradient_semantics"] == "finite-shot estimate"
    assert result.metadata["total_physical_shots"] == result.receipt["consumed_shots"] == 8*4096
    seeds = [entry["root_seed"] for entry in result.metadata["second_order_evaluations"]]
    assert len(set(seeds)) == len(seeds) == 8
    assert result.receipt["live_memory_bytes"] == 0
