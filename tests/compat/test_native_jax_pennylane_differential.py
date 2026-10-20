# Copyright 2026 QuantumBridge Contributors.
# Licensed under the Apache License, Version 2.0.
# Independently authored public-API black-box scenarios; no upstream test ports.

import numpy as np
import pytest

from quantumbridge import Hamiltonian, PauliX, PauliZ
from quantumbridge.qml import QNode
from quantumbridge.transforms import split_non_commuting


def frameworks():
    return pytest.importorskip("jax"), pytest.importorskip("jax.numpy"), pytest.importorskip("pennylane")


def pair(native, public, pl, wires=1):
    return QNode(native, wires, interface="jax", diff_method="parameter-shift"), pl.QNode(
        public, pl.device("default.qubit", wires=wires), interface="jax", diff_method="parameter-shift")


def close(a, b):
    np.testing.assert_allclose(a, b, atol=3e-6, rtol=0)


def test_public_jax_ry_expectation_and_native_quantum_gradient():
    jax, jnp, pl = frameworks()
    def native(t, x):
        t.ry(x, 0)
        return t.expval(PauliZ(0))
    def public(x):
        pl.RY(x, wires=0)
        return pl.expval(pl.Z(0))
    a, b = pair(native, public, pl)
    close(jax.value_and_grad(a)(jnp.asarray(.37)), jax.value_and_grad(b)(jnp.asarray(.37)))


def test_public_jax_nonlinear_shared_preprocessing_and_outer_loss():
    jax, jnp, pl = frameworks()
    def native(t, x):
        t.ry(jnp.sin(x), 0); t.ry(2 * x, 0)
        return t.expval(PauliZ(0))
    def public(x):
        pl.RY(jnp.sin(x), wires=0); pl.RY(2 * x, wires=0)
        return pl.expval(pl.Z(0))
    a, b = pair(native, public, pl)
    close(jax.grad(lambda x: a(x) ** 2)(jnp.asarray(.37)), jax.grad(lambda x: b(x) ** 2)(jnp.asarray(.37)))


def test_public_jax_trainable_gate_and_hamiltonian_coefficient_product_rule():
    jax, jnp, pl = frameworks()
    def native(t, x):
        t.ry(x, 0)
        return t.expval(Hamiltonian([(.7 + .1 * x, PauliX(0)), (.2, PauliX(0).tensor(PauliZ(1)))]))
    def public(x):
        pl.RY(x, wires=0)
        return pl.expval(pl.Hamiltonian([.7 + .1 * x, .2], [pl.X(0), pl.X(0) @ pl.Z(1)]))
    a, b = pair(native, public, pl, wires=2)
    a, b = split_non_commuting(a), pl.transforms.split_non_commuting(b)
    close(jax.value_and_grad(a)(jnp.asarray(.37)), jax.value_and_grad(b)(jnp.asarray(.37)))


def test_public_jax_array_weights_and_keyword_feature():
    jax, jnp, pl = frameworks()
    def native(t, weights, *, feature):
        t.ry(weights[0] * feature, 0); t.rx(weights[1], 0)
        return t.expval(PauliZ(0))
    def public(weights, *, feature):
        pl.RY(weights[0] * feature, wires=0); pl.RX(weights[1], wires=0)
        return pl.expval(pl.Z(0))
    a, b = pair(native, public, pl)
    values = jnp.asarray([.2, .3])
    close(jax.grad(lambda x: a(x, feature=.7))(values), jax.grad(lambda x: b(x, feature=.7))(values))


def test_public_jax_probability_vector_jacobian():
    jax, jnp, pl = frameworks()
    def native(t, x):
        t.ry(x, 0)
        return t.probs([0])
    def public(x):
        pl.RY(x, wires=0)
        return pl.probs(wires=[0])
    a, b = pair(native, public, pl)
    def native_vector(x):
        value = a(x)
        return jnp.stack([value["0"], value["1"]])
    close(jax.jacrev(native_vector)(jnp.asarray(.37)), jax.jacrev(b)(jnp.asarray(.37)))


def test_public_jax_qwc_child_gradient_two_noncommuting_groups():
    jax, jnp, pl = frameworks()
    def native(t, x):
        t.ry(x, 0)
        return t.expval(Hamiltonian([(.7, PauliX(0)), (.2, PauliZ(0))]))
    def public(x):
        pl.RY(x, wires=0)
        return pl.expval(.7 * pl.X(0) + .2 * pl.Z(0))
    a, b = pair(native, public, pl)
    a, b = split_non_commuting(a), pl.transforms.split_non_commuting(b)
    close(jax.value_and_grad(a)(jnp.asarray(.37)), jax.value_and_grad(b)(jnp.asarray(.37)))
    assert a.last_metadata["executed_tape_count"] == 2


def test_public_jax_jit_actual_native_value_and_gradient():
    jax, jnp, pl = frameworks()
    def native(t, x):
        t.ry(x, 0)
        return t.expval(PauliZ(0))
    def public(x):
        pl.RY(x, wires=0)
        return pl.expval(pl.Z(0))
    a, b = pair(native, public, pl)
    for x in [.2, -.6]:
        close(jax.jit(jax.value_and_grad(a))(jnp.asarray(x)), jax.jit(jax.value_and_grad(b))(jnp.asarray(x)))


def test_public_jax_vmap_grad_and_forward_jvp():
    jax, jnp, pl = frameworks()
    def native(t, x):
        t.ry(x, 0)
        return t.expval(PauliZ(0))
    def public(x):
        pl.RY(x, wires=0)
        return pl.expval(pl.Z(0))
    a, b = pair(native, public, pl)
    values = jnp.asarray([.1, .4, -.7])
    # The public eager shift/vmap path can reject tracers in these versions.
    # Backprop is only the external value oracle, never our quantum engine.
    batched_oracle = pl.QNode(public, pl.device("default.qubit", wires=1), interface="jax", diff_method="backprop")
    close(jax.vmap(jax.grad(a))(values), jax.vmap(jax.grad(batched_oracle))(values))
    close(jax.jvp(a, (jnp.asarray(.3),), (jnp.asarray(2.),)), jax.jvp(b, (jnp.asarray(.3),), (jnp.asarray(2.),)))


def test_public_eager_parameter_shift_vmap_capability_is_reported_separately():
    jax, jnp, pl = frameworks()
    def public(x):
        pl.RY(x, wires=0)
        return pl.expval(pl.Z(0))
    oracle = pl.QNode(public, pl.device("default.qubit", wires=1), interface="jax", diff_method="parameter-shift")
    values = jnp.asarray([.1, .4, -.7])
    try:
        result = jax.vmap(jax.grad(oracle))(values)
    except ValueError as exc:
        if "Converting a JAX array to a NumPy array not supported" not in str(exc):
            raise
        pytest.xfail("Public PennyLane " + pl.__version__ + " eager shift/vmap rejects abstract tracer conversion; not native failure or matching-oracle evidence")
    close(result, -jnp.sin(values))
