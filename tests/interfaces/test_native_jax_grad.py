# Copyright 2026 QuantumBridge Contributors.
# Licensed under the Apache License, Version 2.0.
# Independent native/JAX mathematical contracts, not upstream test ports.

import numpy as np
import pytest

from quantumbridge import PauliX, PauliZ
from quantumbridge.diff.qnode_engine import ExecutionPlan
from quantumbridge.qml import QNode
from quantumbridge.transforms import split_non_commuting
from quantumbridge.utils.math import Hamiltonian


def native_derivative_spy(monkeypatch):
    calls = []
    original = ExecutionPlan.jacobian

    def checked(plan, values, method=None, step=1e-6, **options):
        assert (method or plan.node.diff_method) != "finite-diff"
        calls.append(tuple(request.kind for request in plan.requests))
        return original(plan, values, method, step, **options)

    monkeypatch.setattr(ExecutionPlan, "jacobian", checked)
    return calls


def test_real_jax_value_and_grad_uses_native_quantum_derivative(monkeypatch):
    jax = pytest.importorskip("jax")
    jnp = pytest.importorskip("jax.numpy")
    calls = native_derivative_spy(monkeypatch)

    def circuit(tape, theta):
        tape.ry(theta, 0)
        return tape.expval(PauliZ(0))

    node = QNode(circuit, 1, interface="jax", diff_method="parameter-shift")
    theta = jnp.asarray(.37)
    value, gradient = jax.value_and_grad(node)(theta)
    tolerance = 2e-6 if theta.dtype == jnp.float32 else 1e-12
    assert value.dtype == theta.dtype and gradient.dtype == theta.dtype
    np.testing.assert_allclose(value, np.cos(.37), atol=tolerance, rtol=0)
    np.testing.assert_allclose(gradient, -np.sin(.37), atol=tolerance, rtol=0)
    assert calls


def test_real_jax_grad_traverses_actual_qwc_child_plans(monkeypatch):
    jax = pytest.importorskip("jax")
    jnp = pytest.importorskip("jax.numpy")
    calls = native_derivative_spy(monkeypatch)

    def circuit(tape, theta):
        tape.ry(theta, 0)
        return tape.expval(Hamiltonian([
            (.7, PauliX(0)), (.2, PauliX(0).tensor(PauliZ(1))),
        ]))

    node = split_non_commuting(QNode(circuit, 2, interface="jax", diff_method="parameter-shift"))
    theta = jnp.asarray(.37)
    value, gradient = jax.value_and_grad(node)(theta)
    tolerance = 2e-6 if theta.dtype == jnp.float32 else 1e-12
    np.testing.assert_allclose(value, .9 * np.sin(.37), atol=tolerance, rtol=0)
    np.testing.assert_allclose(gradient, .9 * np.cos(.37), atol=tolerance, rtol=0)
    assert ("pauli_group",) in calls


def test_jax_classical_preprocessing_and_outer_loss_chain_rule():
    jax = pytest.importorskip("jax")
    jnp = pytest.importorskip("jax.numpy")
    def circuit(tape, x):
        tape.ry(jnp.sin(x) + 2 * x, 0)
        return tape.expval(PauliZ(0))
    node = QNode(circuit, 1, interface="jax")
    x = jnp.asarray(.3)
    angle = np.sin(.3) + .6
    expected = -np.sin(2 * angle) * (np.cos(.3) + 2)
    np.testing.assert_allclose(jax.grad(lambda p: node(p) ** 2)(x), expected, atol=2e-6, rtol=0)


def test_jax_shared_gate_and_hamiltonian_coefficient_product_rule():
    jax = pytest.importorskip("jax")
    jnp = pytest.importorskip("jax.numpy")
    def circuit(tape, x):
        tape.ry(x, 0)
        return tape.expval(Hamiltonian([
            (.7 + .1 * x, PauliX(0)), (.2, PauliX(0).tensor(PauliZ(1))),
        ]))
    node = split_non_commuting(QNode(circuit, 2, interface="jax"))
    x = jnp.asarray(.37)
    value, gradient = jax.value_and_grad(node)(x)
    np.testing.assert_allclose(value, (.9 + .037) * np.sin(.37), atol=2e-6, rtol=0)
    np.testing.assert_allclose(gradient, .1 * np.sin(.37) + .937 * np.cos(.37), atol=2e-6, rtol=0)
    assert node.last_metadata["native_postprocessing_derivative"]
    assert node.last_metadata["processing_parameter_count"] == 1


def test_jax_coefficient_only_auto_split_and_unused_input():
    jax = pytest.importorskip("jax")
    jnp = pytest.importorskip("jax.numpy")
    def circuit(tape, x, unused):
        return tape.expval(Hamiltonian([(x * x, PauliZ(0))]))
    node = QNode(circuit, 1, interface="jax")
    result = jax.grad(node, argnums=(0, 1))(jnp.asarray(.3), jnp.asarray(.7))
    np.testing.assert_allclose(result, [.6, 0.], atol=2e-6, rtol=0)


def test_jax_array_weights_kwargs_and_nontrainable_features():
    jax = pytest.importorskip("jax")
    jnp = pytest.importorskip("jax.numpy")
    def circuit(tape, weights, feature, *, scale):
        tape.ry(weights[0] * feature, 0)
        tape.ry(weights[0] + weights[1] * scale, 0)
        return tape.expval(PauliZ(0))
    node = QNode(circuit, 1, interface="jax")
    weights = jnp.asarray([.2, .3])
    result = jax.grad(lambda w: node(w, .4, scale=2.))(weights)
    np.testing.assert_allclose(result, -np.sin(.88) * np.array([1.4, 2.]), atol=2e-6, rtol=0)


def test_jax_nested_output_reverse_and_forward_jacobians_and_vjp():
    jax = pytest.importorskip("jax")
    jnp = pytest.importorskip("jax.numpy")
    def circuit(tape, x):
        tape.ry(x, 0)
        return {"z": tape.expval(PauliZ(0)), "other": [tape.expval(PauliX(0)), tape.probs([0])]}
    node = QNode(circuit, 1, interface="jax")
    x = jnp.asarray(.3)
    reverse, forward = jax.jacrev(node)(x), jax.jacfwd(node)(x)
    expected = {"z": -np.sin(.3), "other": [np.cos(.3), {"0": -.5 * np.sin(.3), "1": .5 * np.sin(.3)}]}
    for actual in (reverse, forward):
        for a, b in zip(jax.tree_util.tree_leaves(actual), jax.tree_util.tree_leaves(expected)):
            np.testing.assert_allclose(a, b, atol=2e-6, rtol=0)
    _, pullback = jax.vjp(node, x)
    cotangent = {"z": jnp.asarray(2.), "other": [jnp.asarray(3.), {"0": jnp.asarray(0.), "1": jnp.asarray(4.)}]}
    np.testing.assert_allclose(pullback(cotangent)[0], 3 * np.cos(.3), atol=2e-6, rtol=0)


def test_jax_jvp_tangent_linearity_and_nonlinear_transformed_chain():
    jax = pytest.importorskip("jax")
    jnp = pytest.importorskip("jax.numpy")
    from quantumbridge.transforms import merge_rotations, TransformProgram
    def circuit(tape, x):
        tape.ry(jnp.sin(x), 0)
        tape.ry(2 * x, 0)
        return tape.expval(PauliZ(0))
    node = TransformProgram([merge_rotations, split_non_commuting])(QNode(circuit, 1, interface="jax"))
    x = jnp.asarray(.3)
    _, tangent = jax.jvp(node, (x,), (jnp.asarray(3.),))
    expected = -3 * np.sin(np.sin(.3) + .6) * (np.cos(.3) + 2)
    np.testing.assert_allclose(tangent, expected, atol=3e-6, rtol=0)
