# Copyright 2026 QuantumBridge Contributors.
# Licensed under the Apache License, Version 2.0.
# Independent analytic and execution-accounting contracts for native Hessians.

import numpy as np
import pytest

from quantumbridge import Hamiltonian, PauliX, PauliZ
from quantumbridge.core.classical import UnsupportedFeature
from quantumbridge.diff import HigherOrderLimits
from quantumbridge.qml import QNode
from quantumbridge.transforms import split_non_commuting


def _ry_z(t, x):
    t.ry(x, 0)
    return t.expval(PauliZ(0))


@pytest.mark.parametrize("gate", ["rx", "ry", "rz", "phase", "cp", "crx", "cry", "crz", "rxx", "ryy", "rzz"])
def test_gate_second_recipes_match_independent_trigonometric_formulas(gate):
    theta = .37
    def program(t, angle):
        if gate in {"rz", "phase", "rzz"}: t.h(0)
        if gate in {"crx", "cry", "crz", "cp"}: t.h(0)
        if gate in {"crz", "cp"}: t.h(1)
        if gate in {"cp", "crx", "cry", "crz"}: getattr(t, gate)(angle, 0, 1)
        elif gate in {"rxx", "ryy", "rzz"}: getattr(t, gate)(angle, 0, 1)
        else: getattr(t, gate)(angle, 0)
        if gate in {"crx", "cry", "crz"}:
            target = PauliX(1) if gate == "crz" else PauliZ(1)
            return t.expval(Hamiltonian([(1., PauliX(0)), (.3, target)]))
        return t.expval(PauliX(0) if gate in {"rz", "phase", "rzz", "cp"} else PauliZ(0))
    node = QNode(program, 2, max_diff=2)
    expected = -.25*np.cos(theta/2)-.15*np.cos(theta) if gate in {"crx", "cry", "crz"} else -.5*np.cos(theta) if gate == "cp" else -np.cos(theta)
    np.testing.assert_allclose(node.compute_hessian(theta), expected, atol=1e-11, rtol=0)
    assert node.last_metadata["second_order_method"] == "convolved exact parameter-shift"
    assert node.last_metadata["second_shifted_evaluation_count"] == (16 if gate in {"crx", "cry", "crz"} else 4)


def test_mixed_partials_nested_outputs_shared_inputs_and_keyword_blocks():
    def program(t, x, *, scale):
        t.ry(x[0]*x[1], 0)
        t.ry(scale, 0)
        return {"z": t.expval(PauliZ(0)), "probabilities": t.probs(wires=[0])}
    node = QNode(program, 1, max_diff=2)
    x, scale = np.array([.7, .2]), .3
    angle = x.prod()+scale
    gradient = np.array([x[1], x[0], 1.])
    map_hessian = np.array([[0., 1., 0.], [1., 0., 0.], [0., 0., 0.]])
    expected = -np.cos(angle)*np.outer(gradient, gradient)-np.sin(angle)*map_hessian
    value, blocks = node.execute_and_compute_hessian(x, scale=scale, argnums=(0,), argnames=("scale",))
    np.testing.assert_allclose(value["z"], np.cos(angle), atol=1e-12)
    for left, right, reference in [(0, 0, expected[:2, :2]), (0, 1, expected[:2, 2]), (1, 0, expected[2, :2]), (1, 1, expected[2, 2])]:
        np.testing.assert_allclose(blocks[left][right]["z"], reference, atol=1e-11)
        np.testing.assert_allclose(blocks[left][right]["probabilities"]["0"], reference/2, atol=1e-11)
        np.testing.assert_allclose(blocks[left][right]["probabilities"]["1"], -reference/2, atol=1e-11)


def test_streamed_hvp_does_not_require_identity_or_full_hessian_budget(monkeypatch):
    def program(t, x):
        t.ry(x[0]*x[1], 0)
        return t.expval(PauliZ(0))
    x, tangent = np.array([.7, .2]), np.array([.4, -.3])
    gradient = np.array([.2, .7])
    hessian = -np.cos(.14)*np.outer(gradient, gradient)-np.sin(.14)*np.array([[0., 1.], [1., 0.]])
    node = QNode(program, 1, max_diff=2, higher_order_limits=HigherOrderLimits(max_hessian_elements=1))
    with pytest.raises(MemoryError): node.compute_hessian(x)
    monkeypatch.setattr(np, "eye", lambda *a, **k: pytest.fail("HVP must not allocate an identity or full Hessian"))
    value, product = node.execute_and_compute_hvp(tangent, x)
    np.testing.assert_allclose([value], [np.cos(.14)], atol=1e-12)
    np.testing.assert_allclose(product, hessian @ tangent, atol=1e-11)
    assert node.last_metadata["hvp_streamed"]


def test_analytic_variance_second_moment_and_outer_product_corrections():
    def program(t, x):
        t.ry(x*x, 0)
        return t.var(PauliZ(0))
    node = QNode(program, 1, max_diff=2)
    x = .7
    expected = 8*x*x*np.cos(2*x*x)+2*np.sin(2*x*x)
    np.testing.assert_allclose(node.compute_hessian(x), expected, atol=1e-11)
    np.testing.assert_allclose(node.compute_hvp(.3, x), .3*expected, atol=1e-11)


def test_qwc_real_child_second_derivatives_and_nonlinear_coefficient_cross_terms():
    def program(t, x):
        t.ry(np.sin(x)+2*x, 0)
        return t.expval(Hamiltonian([(.7+.1*x, PauliX(0)), (.2, PauliX(0).tensor(PauliZ(1)))]))
    node = split_non_commuting(QNode(program, 2, max_diff=2))
    x, a = .37, .937
    angle, first = np.sin(x)+2*x, np.cos(x)+2
    expected = .2*np.cos(angle)*first-a*np.sin(angle)*first**2-a*np.cos(angle)*np.sin(x)
    np.testing.assert_allclose(node.compute_hessian(x), expected, atol=1e-11)
    np.testing.assert_allclose(node.compute_hvp(.4, x), .4*expected, atol=1e-11)
    assert node.last_metadata["postprocessing_second_chain_rule"]
    assert node.last_metadata["second_shifted_evaluation_count"] > 0


def test_finite_shot_linear_expectation_independent_streams_and_actual_work():
    def program(t, x):
        t.ry(x, 0)
        return t.expval(PauliZ(0))
    node = QNode(program, 1, max_diff=2, shots=[4000, 5000], seed=41)
    first = node.compute_hessian(.37)
    metadata = node.last_metadata
    np.testing.assert_allclose(first, [-np.cos(.37)]*2, atol=.07, rtol=0)
    assert first == node.compute_hessian(.37)
    receipts = metadata["second_order_evaluations"]
    assert len(receipts) == 8
    assert len({receipt["root_seed"] for receipt in receipts}) == 8
    assert len({receipt["evaluation_id"] for receipt in receipts}) == 8
    assert metadata["total_physical_shots"] == 8*9000
    assert metadata["second_order_work"]["tape_count"] == 16


@pytest.mark.parametrize("options,method,error", [
    ({"higher_order_limits": HigherOrderLimits(max_shifted_circuits=5)}, None, MemoryError),
    ({"higher_order_limits": HigherOrderLimits(max_total_tapes=7)}, None, MemoryError),
    ({"higher_order_limits": HigherOrderLimits(max_derivative_order=1)}, None, MemoryError),
    ({"shots": 100, "seed": 7, "higher_order_limits": HigherOrderLimits(max_total_physical_shots=700)}, None, MemoryError),
    ({"shots": 100}, None, UnsupportedFeature),
    ({"shots": 100, "seed": 7}, "adjoint", UnsupportedFeature), ({}, "finite-diff", UnsupportedFeature),
])
def test_preflight_limits_and_unsupported_methods_execute_no_quantum_work(options, method, error, monkeypatch):
    node = QNode(_ry_z, 1, max_diff=2, **options)
    monkeypatch.setattr(node.device, "expectation", lambda *a, **k: pytest.fail("rejection must precede quantum execution"))
    with pytest.raises(error): node.compute_hessian(.37, method=method)


def test_invalid_order_tangents_and_sampled_variance_reject():
    node = QNode(_ry_z, 1)
    with pytest.raises(UnsupportedFeature): node.compute_hessian(.3)
    node.max_diff = 3
    with pytest.raises(UnsupportedFeature): node.compute_hessian(.3)
    node.max_diff = 2
    for tangent in ([1., 2.], float("nan"), 1j, None):
        with pytest.raises(ValueError): node.compute_hvp(tangent, .3)
    def variance(t, x):
        t.ry(x, 0)
        return t.var(PauliZ(0))
    node = QNode(variance, 1, max_diff=2, shots=100, seed=7)
    with pytest.raises(UnsupportedFeature, match="variance"): node.compute_hessian(.3)


@pytest.mark.parametrize("policy", [None, "uniform", "weighted"])
def test_qwc_finite_linear_second_estimates_have_actual_integer_group_work(policy, monkeypatch):
    def circuit(t, angle):
        t.ry(angle, 0)
        return t.expval(Hamiltonian([(.7, PauliX(0)), (.2, PauliZ(0))]))
    node = split_non_commuting(QNode(circuit, 1, max_diff=2, shots=[4000, 6000], seed=91), shot_dist=policy)
    original, calls = node.device.sample, []
    def sample(*args, **kwargs):
        calls.append((kwargs["shots"], kwargs["seed"]))
        return original(*args, **kwargs)
    monkeypatch.setattr(node.device, "sample", sample)
    expected = -.7*np.sin(.37)-.2*np.cos(.37)
    np.testing.assert_allclose(node.compute_hessian(.37), [expected, expected], atol=.07, rtol=0)
    assert len(calls) == 32
    assert len({seed for _, seed in calls}) == 32
    assert all(isinstance(shots, (int, np.integer)) and shots > 0 for shots, _ in calls)
    assert sum(shots for shots, _ in calls) == node.last_metadata["total_physical_shots"] == 80000*(2 if policy is None else 1)


def test_nonlinear_multichild_processing_second_cross_terms_are_not_dropped():
    def circuit(t, values):
        t.ry(values[0], 0); t.rx(values[1], 0)
        return t.expval(PauliZ(0))
    def duplicate_product(tape):
        return (tape.copy(), tape.copy()), lambda results: results[0]*results[1]
    x = np.array([.37, .2])
    node = QNode(circuit, 1, max_diff=2).with_transform(duplicate_product)
    expected = [[-2*np.cos(2*x[0])*np.cos(x[1])**2, np.sin(2*x[0])*np.sin(2*x[1])],
                [np.sin(2*x[0])*np.sin(2*x[1]), -2*np.cos(2*x[1])*np.cos(x[0])**2]]
    np.testing.assert_allclose(node.compute_hessian(x), expected, atol=1e-11)
    np.testing.assert_allclose(node.compute_hvp(np.array([.3, -.2]), x), np.asarray(expected) @ [.3, -.2], atol=1e-11)
    assert node.last_metadata["executed_tape_count"] == 2
    node.shots, node.seed = 100, 7
    with pytest.raises(UnsupportedFeature, match="linear quantum-output"): node.compute_hessian(x)


def test_parameter_dependent_weighted_shot_allocation_rejects_before_execution(monkeypatch):
    def circuit(t, angle):
        t.ry(angle, 0)
        return t.expval(Hamiltonian([(angle, PauliX(0)), (.2, PauliZ(0))]))
    node = split_non_commuting(QNode(circuit, 1, max_diff=2, shots=100, seed=9), shot_dist="weighted")
    monkeypatch.setattr(node.device, "sample", lambda *a, **k: pytest.fail("allocation derivative must reject before sample"))
    with pytest.raises(UnsupportedFeature, match="integer shot allocation"): node.compute_hessian(.37)


def test_zero_first_classical_derivative_retains_nonzero_second_map_term():
    def circuit(t, x):
        t.ry(x*x, 0)
        return t.expval(PauliX(0))
    node = QNode(circuit, 1, max_diff=2)
    np.testing.assert_allclose(node.compute_hessian(0.), 2., atol=1e-11)
    np.testing.assert_allclose(node.compute_hvp(.3, 0.), .6, atol=1e-11)
    assert node.last_metadata["first_shifted_evaluation_count"] == 2
    assert node.last_metadata["second_shifted_evaluation_count"] == 0


def test_shared_occurrence_pair_expansion_stops_at_budget_before_quantum(monkeypatch):
    def circuit(t, angle):
        for _ in range(200): t.ry(angle, 0)
        return t.expval(PauliZ(0))
    node = QNode(circuit, 1, max_diff=2, higher_order_limits=HigherOrderLimits(max_shifted_circuits=100))
    monkeypatch.setattr(node.device, "expectation", lambda *a, **k: pytest.fail("pair preflight must not execute"))
    with pytest.raises(MemoryError, match="max_shifted_circuits"): node.compute_hessian(.3)
