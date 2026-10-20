# Copyright 2026 QuantumBridge Contributors.
# Licensed under the Apache License, Version 2.0.
"""Explicit query status is returned by each actual native CPU execution."""

import numpy as np
import pytest

jax = pytest.importorskip("jax")
jnp = pytest.importorskip("jax.numpy")

from quantumbridge import Hamiltonian, PauliX, PauliZ, StatevectorDevice
from quantumbridge.execution import UnifiedExecutionLimits
from quantumbridge.qml import QNode
from quantumbridge.transforms import split_non_commuting


def test_same_jit_graph_runtime_work_budget_success_failure_success():
    def fn(t, x):
        t.ry(x[0]*x[0], 0)
        return t.expval(PauliZ(0))
    qnode = QNode(fn, 1, interface="jax", max_diff=2, diff_method="parameter-shift",
        unified_limits=UnifiedExecutionLimits(max_derivative_work=4))
    compiled = jax.jit(lambda x: qnode.jax_hvp_with_status(jnp.ones_like(x), x))
    for point, expected in ((0., 0), (.3, 3), (0., 0)):
        value, status = compiled(jnp.asarray([point]))
        assert int(status) == expected
        if expected: assert np.all(np.isnan(value))
        else: np.testing.assert_allclose(value, [0.], atol=1e-6)


def node(**options):
    def fn(t, x):
        t.ry(x[0], 0)
        return t.expval(PauliZ(0))
    return QNode(fn, 1, interface="jax", max_diff=2, **options)


def test_same_compiled_hvp_valid_invalid_valid_is_not_stale():
    qnode = node()
    compiled = jax.jit(lambda x: qnode.jax_hvp_with_status(jnp.ones_like(x), x))
    for x in (.2, np.nan, .7, .2):
        product, status = compiled(jnp.array([x]))
        assert int(status) == (1 if np.isnan(x) else 0)
        np.testing.assert_allclose(product, [np.nan if np.isnan(x) else -np.cos(x)], atol=2e-6)


def test_compiled_unsupported_finite_adjoint_is_not_success_or_runtime():
    qnode = node(diff_method="second_adjoint", shots=20, seed=9)
    product, status = jax.jit(lambda x: qnode.jax_hvp_with_status(jnp.ones_like(x), x))(jnp.array([.3]))
    assert int(status) == 2 and np.all(np.isnan(product))


def test_compiled_native_failure_has_code_four_not_invalid(monkeypatch):
    def fail(*a, **k): raise RuntimeError("test injected failure")
    monkeypatch.setattr(StatevectorDevice, "statevector", fail)
    qnode = node()
    product, status = jax.jit(lambda x: qnode.jax_hvp_with_status(jnp.ones_like(x), x))(jnp.array([.3]))
    assert int(status) == 4 and np.all(np.isnan(product))


def test_status_cotangent_is_zero_but_query_payload_extra_derivative_rejects():
    qnode = node()
    status_loss = lambda x: qnode.jax_hvp_with_status(jnp.ones_like(x), x)[1].astype(x.dtype)
    np.testing.assert_allclose(jax.jit(jax.grad(status_loss))(jnp.array([.3])), [0.])
    from quantumbridge import UnsupportedFeature
    with pytest.raises(UnsupportedFeature, match="Differentiate the QNode"):
        jax.grad(lambda x: jnp.sum(qnode.jax_hvp_with_status(jnp.ones_like(x), x)[0]))(jnp.array([.3]))


def test_jacobian_and_full_hessian_queries_use_current_input():
    qnode = node(diff_method="second_adjoint")
    # First derivatives use the existing first-adjoint method, not its order-two alias.
    first = node(diff_method="adjoint")
    jac, status = jax.jit(first.jax_jacobian_with_status)(jnp.array([.4]))
    assert int(status) == 0
    hessian, status = jax.jit(qnode.jax_hessian_with_status)(jnp.array([.4]))
    assert int(status) == 0
    np.testing.assert_allclose(jac, [-np.sin(.4)], atol=2e-6)
    np.testing.assert_allclose(hessian, [[-np.cos(.4)]], atol=2e-6)


def test_jax_nonlinear_source_and_live_coefficient_second_chain_rule():
    def fn(t, x):
        t.ry(jnp.sin(x[0])+2*x[0], 0)
        return t.expval(Hamiltonian([(.7+.1*x[0], PauliX(0)), (.2, PauliX(0).tensor(PauliZ(1)))]))
    qnode = split_non_commuting(QNode(fn, 2, interface="jax", max_diff=2, diff_method="adjoint"))
    x, v = .37, .4
    angle, first, coefficient = np.sin(x)+2*x, np.cos(x)+2, .9+.1*x
    expected = .2*np.cos(angle)*first-coefficient*np.sin(angle)*first**2-coefficient*np.cos(angle)*np.sin(x)
    product, status = jax.jit(lambda x: qnode.jax_hvp_with_status(jnp.array([v]), x))(jnp.array([x]))
    assert int(status) == 0
    np.testing.assert_allclose(product, [v*expected], atol=5e-6)


def test_vmap_derivative_status_distinguishes_each_runtime_row():
    qnode = node()
    batch = jax.jit(jax.vmap(lambda x: qnode.jax_hvp_with_status(jnp.ones_like(x), x)))
    product, status = batch(jnp.array([[.2], [np.nan], [.7]]))
    np.testing.assert_array_equal(status, [0, 1, 0])
    np.testing.assert_allclose(product, [[-np.cos(.2)], [np.nan], [-np.cos(.7)]], atol=2e-6)


def test_float32_query_preserves_dtype_and_static_shape():
    qnode = node()
    product, status = jax.jit(lambda x: qnode.jax_hvp_with_status(jnp.ones_like(x), x))(jnp.array([.3], dtype=jnp.float32))
    assert product.dtype == jnp.float32 and product.shape == (1,) and status.dtype == jnp.int32
    assert int(status) == 0


def test_ordinary_jit_rejects_unimplemented_shared_account_instead_of_ignoring_limit():
    from quantumbridge import UnsupportedFeature
    from quantumbridge.execution import UnifiedExecutionLimits
    qnode = node(unified_limits=UnifiedExecutionLimits(max_total_memory_bytes=1))
    with pytest.raises(UnsupportedFeature, match="shared request account"):
        jax.jit(qnode)(jnp.array([.3]))
