# Copyright 2026 QuantumBridge Contributors.
# Licensed under the Apache License, Version 2.0.
"""Native graph storage survives callbacks, but not its owning graph."""

import gc
import weakref

import numpy as np
import pytest

from quantumbridge import PauliZ
from quantumbridge.execution import UnifiedExecutionLimits as Limits
from quantumbridge.qml import QNode


def capture_accounts(monkeypatch):
    from quantumbridge.interfaces import ordinary_resources
    original = ordinary_resources.managed_framework_plan
    references, accounts = [], []
    def capture(plan):
        managed = original(plan)
        references.append(weakref.ref(managed))
        accounts.append(managed.ledger)
        return managed
    monkeypatch.setattr(ordinary_resources, "managed_framework_plan", capture)
    return references, accounts


def node(interface):
    def fn(tape, x):
        tape.ry(x[0], 0)
        return tape.expval(PauliZ(0))
    return QNode(fn, 1, interface=interface, max_diff=2, unified_limits=Limits())


def test_torch_graph_keeps_native_snapshot_accounted_until_graph_is_gone(monkeypatch):
    torch = pytest.importorskip("torch")
    references, accounts = capture_accounts(monkeypatch)
    qnode = node("torch")
    point = torch.tensor([.3], dtype=torch.float64, requires_grad=True)
    value = qnode(point)
    assert accounts[0].receipt()["live_memory_bytes"] >= 8
    first = torch.autograd.grad(value, point, retain_graph=True)[0]
    np.testing.assert_allclose(first, [-np.sin(.3)], atol=1e-12)
    assert accounts[0].receipt()["live_memory_bytes"] >= 8
    del value, first
    gc.collect()
    assert references[0]() is None
    assert accounts[0].receipt()["live_memory_bytes"] == 0


def test_autograd_pullback_keeps_native_snapshot_accounted(monkeypatch):
    autograd = pytest.importorskip("autograd")
    references, accounts = capture_accounts(monkeypatch)
    qnode = node("autograd")
    pullback, value = autograd.make_vjp(qnode)(np.array([.3]))
    assert accounts[0].receipt()["live_memory_bytes"] >= 8
    np.testing.assert_allclose(pullback(1.), [-np.sin(.3)], atol=1e-12)
    assert accounts[0].receipt()["live_memory_bytes"] >= 8
    del pullback, value
    gc.collect()
    assert references[0]() is None
    assert accounts[0].receipt()["live_memory_bytes"] == 0


def test_autograd_finished_invocations_do_not_leave_plan_owners_alive(monkeypatch):
    autograd = pytest.importorskip("autograd")
    references, accounts = capture_accounts(monkeypatch)
    qnode = node("autograd")
    for _ in range(3):
        np.testing.assert_allclose(autograd.grad(qnode)(np.array([.3])), [-np.sin(.3)], atol=1e-12)
    gc.collect()
    assert all(reference() is None for reference in references)
    assert all(account.receipt()["live_memory_bytes"] == 0 for account in accounts)


@pytest.mark.parametrize("dtype", ["float32", "float64"])
def test_torch_double_backward_and_finished_invocations_release_owners(monkeypatch, dtype):
    torch = pytest.importorskip("torch")
    references, accounts = capture_accounts(monkeypatch)
    qnode = node("torch")
    point = torch.tensor([.3], dtype=getattr(torch, dtype), requires_grad=True)
    def derivative():
        value = qnode(point)
        first = torch.autograd.grad(value, point, create_graph=True)[0]
        second = torch.autograd.grad(first.sum(), point)[0]
        np.testing.assert_allclose(second, [-np.cos(.3)], atol=2e-7)
    for _ in range(3): derivative()
    gc.collect()
    assert all(reference() is None for reference in references)
    assert all(account.receipt()["live_memory_bytes"] == 0 for account in accounts)
    assert all(account.receipt()["consumed_derivative_work"] == 11 for account in accounts)


def test_autograd_retained_gradient_array_keeps_only_its_storage_lease(monkeypatch):
    autograd = pytest.importorskip("autograd")
    references, accounts = capture_accounts(monkeypatch)
    qnode = node("autograd")
    pullback, value = autograd.make_vjp(qnode)(np.array([.3]))
    result = pullback(1.)
    consumed = accounts[0].receipt()["consumed_derivative_work"]
    np.testing.assert_allclose(pullback(1.), result, atol=1e-12)
    assert accounts[0].receipt()["consumed_derivative_work"] > consumed
    del pullback, value
    gc.collect()
    assert references[0]() is None
    assert accounts[0].receipt()["live_memory_bytes"] <= result.nbytes
    del result
    gc.collect()
    assert accounts[0].receipt()["live_memory_bytes"] == 0


@pytest.mark.parametrize("interface", ["torch", "autograd"])
def test_failed_second_backward_can_be_released_and_fresh_graph_recovers(monkeypatch, interface):
    from quantumbridge.execution import DerivativeExecutionError
    references, accounts = capture_accounts(monkeypatch)
    qnode = node(interface)
    qnode.unified_limits = Limits(max_derivative_work=3)
    if interface == "torch":
        torch = pytest.importorskip("torch")
        def run():
            point = torch.tensor([.3], dtype=torch.float64, requires_grad=True)
            first = torch.autograd.grad(qnode(point), point, create_graph=True)[0]
            with pytest.raises(DerivativeExecutionError) as failure: torch.autograd.grad(first.sum(), point)
            assert failure.value.code == 3 and failure.value.receipt["consumed_derivative_work"] == 3
    else:
        autograd = pytest.importorskip("autograd")
        anp = pytest.importorskip("autograd.numpy")
        def run():
            with pytest.raises(DerivativeExecutionError) as failure:
                autograd.hessian(qnode)(anp.array([.3]))
            assert failure.value.code == 3 and failure.value.receipt["consumed_derivative_work"] == 3
    run()
    gc.collect()
    assert all(reference() is None for reference in references)
    assert all(account.receipt()["live_memory_bytes"] == 0 for account in accounts)
    qnode.unified_limits = Limits()
    if interface == "torch":
        point = torch.tensor([.3], dtype=torch.float64, requires_grad=True)
        np.testing.assert_allclose(torch.autograd.functional.hessian(qnode, point), [[-np.cos(.3)]], atol=1e-12)
    else:
        np.testing.assert_allclose(autograd.hessian(qnode)(anp.array([.3])), [[-np.cos(.3)]], atol=1e-12)
