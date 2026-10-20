# Copyright 2026 QuantumBridge Contributors.
# Licensed under the Apache License, Version 2.0.
# Real nonlinear 100-wire framework HVPs; dense device APIs are forbidden.

import numpy as np
import pytest

from quantumbridge import Hamiltonian, PauliZ, StatevectorDevice, DensityMatrixDevice, MatrixProductStateDevice
from quantumbridge.diff import HigherOrderLimits
from quantumbridge.diff.qnode_engine import ExecutionPlan
from quantumbridge.information.matrix_product_state import MatrixProductState
from quantumbridge.qml import QNode
from quantumbridge.transforms import TransformProgram, merge_rotations, split_non_commuting


@pytest.mark.parametrize("interface", ["torch", "autograd", "jax", "tf"])
def test_nonlinear_100_wire_hvp_is_real_directional_mps_execution(interface, monkeypatch):
    framework = pytest.importorskip({"torch": "torch", "autograd": "autograd", "jax": "jax", "tf": "tensorflow"}[interface])
    sin = framework.sin if interface in {"torch", "tf"} else pytest.importorskip("autograd.numpy" if interface == "autograd" else "jax.numpy").sin
    def forbidden(*args, **kwargs): raise AssertionError("Dense expansion forbidden during a real framework HVP")
    for cls, name in [(StatevectorDevice, "statevector"), (DensityMatrixDevice, "density_matrix"),
                      (MatrixProductState, "statevector"), (MatrixProductState, "reduced_density_matrix")]:
        monkeypatch.setattr(cls, name, forbidden)
    original, executions = ExecutionPlan.second_derivatives, []
    def observed(self, values, *args, **kwargs):
        assert kwargs.get("direction") is not None
        result = original(self, values, *args, **kwargs)
        assert result[2].shape[-1] == 1
        executions.extend(self.metadata["second_order_evaluations"])
        return result
    monkeypatch.setattr(ExecutionPlan, "second_derivatives", observed)
    def circuit(t, x):
        t.h(0)
        for wire in range(99): t.cx(wire, wire+1)
        t.ry(sin(x), 99); t.ry(2*x, 99)
        return t.expval(Hamiltonian([(1., PauliZ(0).tensor(PauliZ(99))), (.2, PauliZ(0))]))
    device = MatrixProductStateDevice(max_memory_mb=2, max_bond_dim=4, cutoff=0)
    node = TransformProgram((merge_rotations, split_non_commuting))(
        QNode(circuit, 100, device=device, interface=interface, max_diff=2,
              higher_order_limits=HigherOrderLimits(max_hessian_elements=1)))
    if interface == "torch":
        x = framework.tensor(.3, dtype=framework.float64, requires_grad=True)
        value = node(x)
        first = framework.autograd.grad(value, x, create_graph=True)[0]
        product = framework.autograd.grad(.4*first, x)[0].detach().numpy()
        value = value.detach().numpy()
    elif interface == "autograd":
        value = node(.3)
        product = framework.grad(lambda x: .4*framework.grad(node)(x))(.3)
    elif interface == "jax":
        jnp = pytest.importorskip("jax.numpy")
        x = jnp.asarray(.3)
        value = node(x)
        product = framework.jvp(framework.grad(node), (x,), (jnp.asarray(.4),))[1]
    else:
        x = framework.Variable(.3, dtype=framework.float64)
        with framework.GradientTape() as outer:
            with framework.GradientTape() as inner:
                value = node(x)
            first = inner.gradient(value, x)
            contracted = .4*first
        product = outer.gradient(contracted, x).numpy()
    angle, gp = np.sin(.3)+.6, np.cos(.3)+2
    expected = .4*(-np.cos(angle)*gp**2+np.sin(angle)*np.sin(.3))
    tolerance = 4e-6 if interface == "jax" else 1e-10
    np.testing.assert_allclose([value, product], [np.cos(angle), expected], atol=tolerance, rtol=0)
    assert executions
    for execution in executions:
        part = execution["partitions"][0]
        resources = part["resources"]
        assert part["physical_shots"] == 0 and resources["max_bond_observed"] == 2
        assert resources["max_tensor_bytes"] < 2*1024*1024
        assert resources["max_truncations"] == resources["max_discarded_weight"] == 0
