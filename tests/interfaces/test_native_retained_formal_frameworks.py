# Copyright 2026 QuantumBridge Contributors. Apache-2.0.
"""Real framework derivatives keep retained-only directions mathematically zero."""

import numpy as np
import pytest

import quantumbridge as qb
from quantumbridge.qml import QNode


def setup(interface,partial,mps):
    q,r = qb.Parameter("q"),qb.Parameter("r")
    angle = (r.sin()+q*q).gradient(r)
    if partial:
        angle = angle.assign(r,.31)
    source = qb.Circuit(1).rx(angle,0)
    device = qb.MatrixProductStateDevice(max_bond_dim=2,cutoff=0) if mps else qb.StatevectorDevice()
    node = QNode.from_circuit(source,qb.PauliZ(0),max_diff=2,interface=interface,
        diff_method="mps-tangent" if mps else "adjoint",device=device)
    point = np.array([.2] if partial else [.2,.31])
    gradient = np.zeros(len(point))
    hessian = np.zeros((len(point),len(point)))
    if not partial:
        gradient[1] = np.sin(np.cos(.31))*np.sin(.31)
        hessian[1,1] = -np.cos(np.cos(.31))*np.sin(.31)**2+np.sin(np.cos(.31))*np.cos(.31)
    return node,point,gradient,hessian


@pytest.mark.parametrize("partial", [False,True])
@pytest.mark.parametrize("mps", [False,True])
def test_actual_torch_formal_zero_and_nonzero_hessian(partial,mps):
    torch = pytest.importorskip("torch")
    node,point,gradient,hessian = setup("torch",partial,mps)
    x = torch.tensor(point,dtype=torch.float64,requires_grad=True)
    y = node(x)
    actual = torch.autograd.grad(y,x,create_graph=True)[0]
    second = torch.autograd.functional.hessian(node,x)
    np.testing.assert_allclose(y.detach(),np.cos(np.cos(.31)),atol=3e-13,rtol=0)
    np.testing.assert_allclose(actual.detach(),gradient,atol=2e-10,rtol=0)
    np.testing.assert_allclose(second.detach(),hessian,atol=4e-10,rtol=0)


@pytest.mark.parametrize("partial", [False,True])
@pytest.mark.parametrize("mps", [False,True])
def test_actual_autograd_formal_zero_and_nonzero_hessian(partial,mps):
    autograd = pytest.importorskip("autograd")
    node,point,gradient,hessian = setup("autograd",partial,mps)
    np.testing.assert_allclose(node(point),np.cos(np.cos(.31)),atol=3e-13,rtol=0)
    np.testing.assert_allclose(autograd.grad(node)(point),gradient,atol=2e-10,rtol=0)
    np.testing.assert_allclose(autograd.hessian(node)(point),hessian,atol=4e-10,rtol=0)


@pytest.mark.parametrize("partial", [False,True])
@pytest.mark.parametrize("mps", [False,True])
def test_actual_jax_jit_formal_zero_and_nonzero_hessian(partial,mps):
    jax = pytest.importorskip("jax")
    import jax.numpy as jnp
    assert jax.config.x64_enabled
    node,point,gradient,hessian = setup("jax",partial,mps)
    x = jnp.asarray(point,dtype=jnp.float64)
    np.testing.assert_allclose(jax.jit(node)(x),np.cos(np.cos(.31)),atol=3e-13,rtol=0)
    np.testing.assert_allclose(jax.jit(jax.grad(node))(x),gradient,atol=2e-10,rtol=0)
    np.testing.assert_allclose(jax.jit(jax.hessian(node))(x),hessian,atol=4e-10,rtol=0)
