# Copyright 2026 QuantumBridge Contributors.
# Licensed under the Apache License, Version 2.0.
"""Real C3 contracts, first run before the execution protocol exists."""

import numpy as np
import pytest

from quantumbridge import Hamiltonian, PauliX, PauliZ, StatevectorDevice
from quantumbridge.qml import QNode
from quantumbridge.transforms import split_non_commuting


def test_joint_live_budget_rejects_a_plan_that_passes_existing_local_caps(monkeypatch):
    def circuit(t, x):
        t.ry(x[0]*x[1], 0)
        t.rx(x[0]+x[1], 1)
        return t.expval(Hamiltonian([(1., PauliZ(0)), (.2, PauliX(0)),
                                    (.3, PauliZ(1))]))
    node = QNode(circuit, 2, max_diff=2).with_transform(
        lambda tape: ((tape.copy(), tape.copy()), lambda results: (results[0]+results[1])*.5))
    node = split_non_commuting(node)
    point, tangent = np.array([.2, .3]), np.array([.4, -.1])
    assert np.all(np.isfinite(node.compute_hvp(tangent, point)))
    from quantumbridge.execution import (DerivativeExecutionRequest,
        UnifiedExecutionLimits, UnifiedResourceLedger, ResourceLimitError)
    from quantumbridge.diff.qnode_engine import ExecutionPlan
    ledger = UnifiedResourceLedger(UnifiedExecutionLimits(max_total_memory_bytes=512))
    request = DerivativeExecutionRequest(node, (point,), derivative_order=2,
        derivative_kind="hvp", tangent=tangent)
    monkeypatch.setattr(ExecutionPlan, "evaluate",
        lambda *a, **k: pytest.fail("unified preflight must precede quantum execution"))
    with pytest.raises(ResourceLimitError) as caught:
        node.device.execute_derivatives(request, ledger=ledger)
    assert caught.value.category == "memory"
    assert caught.value.estimated > 512
    receipt = ledger.receipt()
    # The raising API intentionally retains its debugging traceback, including
    # the newly owned packed tangent. A returned status would detach it.
    assert receipt["live_memory_bytes"] == tangent.nbytes
    assert receipt["live_memory_bytes"] == receipt["total_reserved_memory_bytes"]-receipt["total_released_memory_bytes"]
    del caught
    import gc
    gc.collect()
    assert ledger.receipt()["live_memory_bytes"] == 0
    assert receipt["consumed_shots"] == 0


def test_jit_derivative_status_is_runtime_data_not_forward_success():
    jax = pytest.importorskip("jax")
    jnp = pytest.importorskip("jax.numpy")
    def circuit(t, x):
        t.ry(x[0], 0)
        return t.expval(PauliZ(0))
    node = QNode(circuit, 1, interface="jax", max_diff=2)
    point = jnp.array([.3])
    value, status = jax.jit(node.jax_with_status)(point)
    np.testing.assert_allclose(value, np.cos(.3), atol=1e-6)
    assert int(status) == 0
    # Forward status cannot report a later HVP budget failure.
    from quantumbridge.execution import UnifiedExecutionLimits
    node.unified_limits = UnifiedExecutionLimits(max_derivative_work=1)
    compiled = jax.jit(lambda x: node.jax_hvp_with_status(jnp.ones_like(x), x))
    failed, status = compiled(point)
    assert int(status) == 3 and np.all(np.isnan(failed))
    failed, status = compiled(jnp.array([jnp.nan]))
    assert int(status) == 1 and np.all(np.isnan(failed))
    failed, status = compiled(point)
    assert int(status) == 3 and np.all(np.isnan(failed))
    node.unified_limits = UnifiedExecutionLimits()
    recovered = jax.jit(lambda x: node.jax_hvp_with_status(jnp.ones_like(x), x))
    product, status = recovered(point)
    assert int(status) == 0
    np.testing.assert_allclose(product, [-np.cos(.3)], atol=1e-6)
