# Copyright 2026 QuantumBridge Contributors.
# Licensed under the Apache License, Version 2.0.
"""Ordinary framework graphs must not bypass explicit query-only budgets."""

import numpy as np
import pytest

from quantumbridge import Hamiltonian, PauliX, PauliZ, StatevectorDevice
from quantumbridge.execution import DerivativeExecutionError, UnifiedExecutionLimits as Limits
from quantumbridge.qml import QNode
from quantumbridge.transforms import split_non_commuting


def node(interface, limits):
    def fn(t, x):
        t.ry(x[0], 0)
        return t.expval(PauliZ(0))
    return QNode(fn, 1, interface=interface, max_diff=2, unified_limits=limits)


def test_torch_forward_memory_rejects_before_native_allocation(monkeypatch):
    torch = pytest.importorskip("torch")
    qnode = node("torch", Limits(max_total_memory_bytes=1))
    monkeypatch.setattr(StatevectorDevice, "statevector", lambda *a, **k: pytest.fail("unified preflight must block allocation"))
    with pytest.raises(DerivativeExecutionError) as failure:
        qnode(torch.tensor([.3], dtype=torch.float64, requires_grad=True))
    assert failure.value.code == 3 and failure.value.receipt["live_memory_bytes"] == 0


def test_torch_first_backward_cannot_get_a_fresh_work_budget():
    torch = pytest.importorskip("torch")
    qnode = node("torch", Limits(max_derivative_work=1))
    x = torch.tensor([.3], dtype=torch.float64, requires_grad=True)
    value = qnode(x)
    np.testing.assert_allclose(value.detach(), np.cos(.3), atol=1e-12)
    with pytest.raises(DerivativeExecutionError) as failure:
        torch.autograd.grad(value, x)
    assert failure.value.code == 3 and x.grad is None


def test_torch_second_backward_shares_forward_and_first_backward_account():
    torch = pytest.importorskip("torch")
    qnode = node("torch", Limits(max_derivative_work=3))
    x = torch.tensor([.3], dtype=torch.float64, requires_grad=True)
    first = torch.autograd.grad(qnode(x), x, create_graph=True)[0]
    np.testing.assert_allclose(first.detach(), [-np.sin(.3)], atol=1e-12)
    with pytest.raises(DerivativeExecutionError) as failure:
        torch.autograd.grad(first.sum(), x)
    assert failure.value.code == 3 and x.grad is None
    assert failure.value.receipt["consumed_derivative_work"] == 3


def test_torch_transformed_valid_overbudget_valid_recovers_math_and_ownership():
    torch = pytest.importorskip("torch")
    def fn(t, x):
        t.ry(x[0], 0)
        return t.expval(Hamiltonian([(.7+.1*x[0], PauliX(0)), (.2, PauliX(0).tensor(PauliZ(1)))]))
    qnode = split_non_commuting(QNode(fn, 2, interface="torch", max_diff=2, unified_limits=Limits()))
    def gradient():
        x = torch.tensor([.3], dtype=torch.float64, requires_grad=True)
        return torch.autograd.grad(qnode(x), x)[0].detach().numpy()
    initial = gradient()
    qnode.unified_limits = Limits(max_total_memory_bytes=1)
    with pytest.raises(DerivativeExecutionError): gradient()
    qnode.unified_limits = Limits()
    np.testing.assert_allclose(gradient(), initial, atol=1e-12)
    receipt = qnode.last_metadata["unified_resource_receipt"]
    assert receipt["live_memory_bytes"] == receipt["active_tapes"] == 0


def test_autograd_forward_memory_rejects_before_native_allocation(monkeypatch):
    autograd = pytest.importorskip("autograd")
    anp = pytest.importorskip("autograd.numpy")
    qnode = node("autograd", Limits(max_total_memory_bytes=1))
    monkeypatch.setattr(StatevectorDevice, "statevector", lambda *a, **k: pytest.fail("unified preflight must block allocation"))
    with pytest.raises(DerivativeExecutionError) as failure:
        autograd.grad(lambda x: qnode(x))(anp.array([.3]))
    assert failure.value.code == 3 and failure.value.receipt["live_memory_bytes"] == 0


def test_autograd_first_backward_cannot_get_a_fresh_work_budget():
    autograd = pytest.importorskip("autograd")
    anp = pytest.importorskip("autograd.numpy")
    qnode = node("autograd", Limits(max_derivative_work=1))
    with pytest.raises(DerivativeExecutionError) as failure:
        autograd.grad(lambda x: qnode(x))(anp.array([.3]))
    assert failure.value.code == 3


def test_autograd_second_backward_shares_forward_and_first_backward_account():
    autograd = pytest.importorskip("autograd")
    anp = pytest.importorskip("autograd.numpy")
    qnode = node("autograd", Limits(max_derivative_work=3))
    gradient = autograd.grad(lambda x: qnode(x))
    with pytest.raises(DerivativeExecutionError) as failure:
        autograd.grad(lambda x: anp.sum(gradient(x)))(anp.array([.3]))
    assert failure.value.code == 3
    assert failure.value.receipt["consumed_derivative_work"] == 3


def test_autograd_transformed_valid_overbudget_valid_recovers_math_and_ownership():
    autograd = pytest.importorskip("autograd")
    anp = pytest.importorskip("autograd.numpy")
    def fn(t, x):
        t.ry(x[0], 0)
        return t.expval(Hamiltonian([(.7+.1*x[0], PauliX(0)), (.2, PauliX(0).tensor(PauliZ(1)))]))
    qnode = split_non_commuting(QNode(fn, 2, interface="autograd", max_diff=2, unified_limits=Limits()))
    gradient = autograd.grad(lambda x: qnode(x))
    initial = gradient(anp.array([.3]))
    qnode.unified_limits = Limits(max_total_memory_bytes=1)
    with pytest.raises(DerivativeExecutionError): gradient(anp.array([.3]))
    qnode.unified_limits = Limits()
    np.testing.assert_allclose(gradient(anp.array([.3])), initial, atol=1e-12)
    receipt = qnode.last_metadata["unified_resource_receipt"]
    assert receipt["live_memory_bytes"] == receipt["active_tapes"] == 0


def test_torch_successful_second_graph_still_reaches_native_hvp_with_shared_receipt():
    torch = pytest.importorskip("torch")
    qnode = node("torch", Limits())
    x = torch.tensor([.3], dtype=torch.float64, requires_grad=True)
    first = torch.autograd.grad(qnode(x), x, create_graph=True)[0]
    product = torch.autograd.grad((first*.4).sum(), x)[0]
    np.testing.assert_allclose(product.detach(), [-.4*np.cos(.3)], atol=1e-12)
    receipt = qnode.last_metadata["unified_resource_receipt"]
    assert receipt["consumed_derivative_work"] == receipt["consumed_tapes"] == 11
    assert receipt["live_memory_bytes"] == 0


def test_autograd_successful_second_graph_still_reaches_native_hvp_with_shared_receipt():
    autograd = pytest.importorskip("autograd")
    anp = pytest.importorskip("autograd.numpy")
    qnode = node("autograd", Limits())
    first = autograd.grad(lambda x: qnode(x))
    product = autograd.grad(lambda x: anp.sum(.4*first(x)))(anp.array([.3]))
    np.testing.assert_allclose(product, [-.4*np.cos(.3)], atol=1e-12)
    receipt = qnode.last_metadata["unified_resource_receipt"]
    assert receipt["consumed_derivative_work"] == receipt["consumed_tapes"] == 11
    assert receipt["live_memory_bytes"] == 0


def test_torch_repeated_backward_retains_consumption_but_fresh_invocation_recovers():
    torch = pytest.importorskip("torch")
    qnode = node("torch", Limits(max_derivative_work=3))
    point = torch.tensor([.3], dtype=torch.float64, requires_grad=True)
    value = qnode(point)
    first = torch.autograd.grad(value, point, retain_graph=True)[0]
    np.testing.assert_allclose(first, [-np.sin(.3)], atol=1e-12)
    with pytest.raises(DerivativeExecutionError) as failure:
        torch.autograd.grad(value, point, retain_graph=True)
    assert failure.value.code == 3
    assert failure.value.receipt["consumed_derivative_work"] == 3
    assert failure.value.receipt["live_memory_bytes"] == 0
    recovered = torch.autograd.grad(qnode(point), point)[0]
    np.testing.assert_allclose(recovered, first, atol=1e-12)


def test_autograd_reused_pullback_cannot_refund_prior_derivative_work():
    autograd = pytest.importorskip("autograd")
    anp = pytest.importorskip("autograd.numpy")
    qnode = node("autograd", Limits(max_derivative_work=3))
    pullback, _ = autograd.make_vjp(qnode)(anp.array([.3]))
    first = pullback(1.)
    np.testing.assert_allclose(first, [-np.sin(.3)], atol=1e-12)
    with pytest.raises(DerivativeExecutionError) as failure: pullback(1.)
    assert failure.value.code == 3 and failure.value.receipt["consumed_derivative_work"] == 3
    assert failure.value.receipt["live_memory_bytes"] == 0
    np.testing.assert_allclose(autograd.grad(qnode)(anp.array([.3])), first, atol=1e-12)
