# Copyright 2026 QuantumBridge Contributors.
# Licensed under the Apache License, Version 2.0.

import numpy as np
import pytest

from quantumbridge import PauliX, PauliZ
from quantumbridge.qml import QNode
from quantumbridge.transforms import split_non_commuting
from quantumbridge.utils.math import Hamiltonian


def simple_node():
    def circuit(tape, x):
        tape.ry(x, 0)
        return tape.expval(PauliZ(0))
    return QNode(circuit, 1, interface="jax", diff_method="parameter-shift")


def test_jit_value_and_native_gradient_use_each_runtime_parameter():
    jax = pytest.importorskip("jax")
    jnp = pytest.importorskip("jax.numpy")
    node = simple_node()
    forward, gradient = jax.jit(node), jax.jit(jax.grad(node))
    for x in [.3, -.7, 1.1]:
        np.testing.assert_allclose(forward(jnp.asarray(x)), np.cos(x), atol=2e-6, rtol=0)
        np.testing.assert_allclose(gradient(jnp.asarray(x)), -np.sin(x), atol=2e-6, rtol=0)
    assert "not guaranteed" in node.last_metadata["jit_callback_execution_count"]


def test_vmap_forward_and_gradients_do_not_share_stale_parameters():
    jax = pytest.importorskip("jax")
    jnp = pytest.importorskip("jax.numpy")
    node = simple_node()
    values = jnp.asarray([.2, -.5, 1.2])
    np.testing.assert_allclose(jax.vmap(node)(values), np.cos(values), atol=2e-6, rtol=0)
    np.testing.assert_allclose(jax.vmap(jax.grad(node))(values), -np.sin(values), atol=2e-6, rtol=0)
    np.testing.assert_allclose(jax.jit(jax.vmap(jax.grad(node)))(values), -np.sin(values), atol=2e-6, rtol=0)


def test_jit_qwc_gradient_preserves_gate_and_coefficient_product_rule():
    jax = pytest.importorskip("jax")
    jnp = pytest.importorskip("jax.numpy")
    def circuit(tape, x):
        tape.ry(x, 0)
        return tape.expval(Hamiltonian([(.7 + .1 * x, PauliX(0)), (.2, PauliX(0).tensor(PauliZ(1)))]))
    node = split_non_commuting(QNode(circuit, 2, interface="jax"))
    evaluate = jax.jit(jax.value_and_grad(node))
    for x in [.1, .5, -.2]:
        value, gradient = evaluate(jnp.asarray(x))
        np.testing.assert_allclose(value, (.9 + .1 * x) * np.sin(x), atol=2e-6, rtol=0)
        np.testing.assert_allclose(gradient, .1 * np.sin(x) + (.9 + .1 * x) * np.cos(x), atol=2e-6, rtol=0)


def test_jit_nested_measurement_tree_retains_each_leaf_shape():
    jax = pytest.importorskip("jax")
    jnp = pytest.importorskip("jax.numpy")
    def circuit(tape, x):
        tape.ry(x, 0)
        return {"z": tape.expval(PauliZ(0)), "p": [tape.probs([0])]}
    node = QNode(circuit, 1, interface="jax")
    result = jax.jit(node)(jnp.asarray(.3))
    np.testing.assert_allclose(result["z"], np.cos(.3), atol=2e-6, rtol=0)
    np.testing.assert_allclose(result["p"][0]["1"], np.sin(.15) ** 2, atol=2e-6, rtol=0)


def test_jit_jvp_is_a_real_forward_mode_native_jacobian_product():
    jax = pytest.importorskip("jax")
    jnp = pytest.importorskip("jax.numpy")
    node = simple_node()
    def product(x, tangent): return jax.jvp(node, (x,), (tangent,))
    value, tangent = jax.jit(product)(jnp.asarray(.3), jnp.asarray(2.))
    np.testing.assert_allclose([value, tangent], [np.cos(.3), -2 * np.sin(.3)], atol=2e-6, rtol=0)


def test_vmap_trainable_coefficients_have_independent_actual_primals():
    jax = pytest.importorskip("jax")
    jnp = pytest.importorskip("jax.numpy")
    def circuit(tape, x):
        tape.ry(x, 0)
        return tape.expval(Hamiltonian([(x, PauliX(0))]))
    node = split_non_commuting(QNode(circuit, 1, interface="jax"))
    values = jnp.asarray([.1, .6, -.2])
    result = jax.vmap(jax.grad(node))(values)
    np.testing.assert_allclose(result, np.sin(values) + values * np.cos(values), atol=2e-6, rtol=0)


def test_vmap_partial_batching_keeps_shared_nontrainable_feature():
    jax = pytest.importorskip("jax")
    jnp = pytest.importorskip("jax.numpy")
    def circuit(tape, x, feature):
        tape.ry(x * feature, 0)
        return tape.expval(PauliZ(0))
    node = QNode(circuit, 1, interface="jax")
    values = jnp.asarray([.2, .4, -.7])
    np.testing.assert_allclose(jax.vmap(node, in_axes=(0, None))(values, 2.), np.cos(2 * values), atol=2e-6, rtol=0)


def test_jit_forward_and_reverse_jacobians_agree_for_array_weights():
    jax = pytest.importorskip("jax")
    jnp = pytest.importorskip("jax.numpy")
    def circuit(tape, x):
        tape.ry(x[0], 0); tape.rx(x[1], 0)
        return tape.expval(PauliZ(0)), tape.expval(PauliX(0))
    node = QNode(circuit, 1, interface="jax")
    values = jnp.asarray([.2, .3])
    left, right = jax.jit(jax.jacrev(node))(values), jax.jit(jax.jacfwd(node))(values)
    for a, b in zip(left, right): np.testing.assert_allclose(a, b, atol=2e-6, rtol=0)


def test_jit_captures_owned_device_and_gradient_options_not_mutable_external_state():
    jax = pytest.importorskip("jax")
    jnp = pytest.importorskip("jax.numpy")
    node = simple_node()
    evaluate = jax.jit(jax.value_and_grad(node))
    first = evaluate(jnp.asarray(.3))
    node.gradient_kwargs["method"] = "finite-diff"
    node.device.max_memory_mb = 1e-9
    # A compiled static definition keeps its owned original configuration.
    np.testing.assert_array_equal(evaluate(jnp.asarray(.3)), first)
    np.testing.assert_allclose(first, [np.cos(.3), -np.sin(.3)], atol=2e-6, rtol=0)
