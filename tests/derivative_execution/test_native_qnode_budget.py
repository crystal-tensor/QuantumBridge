# Copyright 2026 QuantumBridge Contributors.
# Licensed under the Apache License, Version 2.0.
"""Direct native QNode methods must enforce the same explicit resource limits."""

import numpy as np
import pytest

from quantumbridge import PauliZ, StatevectorDevice
from quantumbridge.execution import DerivativeExecutionError, UnifiedExecutionLimits as Limits
from quantumbridge.qml import QNode


@pytest.mark.parametrize("operation", ["value", "jacobian", "hessian", "hvp"])
def test_direct_native_qnode_budget_rejects_before_simulation(operation, monkeypatch):
    def fn(t, x):
        t.ry(x, 0)
        return t.expval(PauliZ(0))
    node = QNode(fn, 1, interface="numpy", max_diff=2, unified_limits=Limits(max_total_memory_bytes=1))
    def forbidden(*a, **k): pytest.fail("explicit native QNode budget was ignored")
    monkeypatch.setattr(StatevectorDevice, "statevector", forbidden)
    with pytest.raises(DerivativeExecutionError) as failed:
        if operation == "value": node(.3)
        elif operation == "jacobian": node.jacobian(.3)
        elif operation == "hessian": node.compute_hessian(.3)
        else: node.compute_hvp(.4, .3)
    assert failed.value.code == 3 and failed.value.receipt["live_memory_bytes"] == 0


def test_native_budgeted_selected_and_keyword_inputs_keep_the_same_layout():
    def fn(t, x, fixed, *, y):
        t.ry(x*y+fixed, 0)
        return t.expval(PauliZ(0))
    node = QNode(fn, 1, interface="numpy", max_diff=2, diff_method="adjoint", unified_limits=Limits())
    x, y, fixed = .2, .3, .1
    angle = x*y+fixed
    expected = -np.cos(angle)*np.outer([y, x], [y, x])-np.sin(angle)*np.array([[0., 1.], [1., 0.]])
    actual = node.compute_hessian(x, fixed, y=y, argnums=(0,), argnames=("y",))
    np.testing.assert_allclose(actual, expected, atol=1e-12)
    product = node.compute_hvp((.4, -.1), x, fixed, y=y, argnums=(0,), argnames=("y",))
    np.testing.assert_allclose(product, expected @ [.4, -.1], atol=1e-12)
    assert node.last_metadata["unified_resource_receipt"]["live_memory_bytes"] == 0
