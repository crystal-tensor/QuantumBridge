# Copyright 2026 QuantumBridge Contributors.
# Licensed under the Apache License, Version 2.0.
"""Public PennyLane APIs are optional black-box references, not native engines."""

import numpy as np
import pytest

qml = pytest.importorskip("pennylane")

from quantumbridge import Hamiltonian, PauliX, PauliZ
from quantumbridge.execution import DerivativeExecutionRequest as Request
from quantumbridge.qml import QNode


def native_hessian(fn, point, width):
    node = QNode(fn, width, max_diff=2)
    return node.device.execute_derivatives(Request(node, (point,), method="second_adjoint",
        derivative_order=2, derivative_kind="hessian")).derivative


def public_hessian(fn, point, width):
    oracle = qml.QNode(fn, qml.device("default.qubit", wires=width), interface="autograd", diff_method="backprop", max_diff=2)
    try:
        return qml.jacobian(qml.jacobian(oracle))(qml.numpy.array(point, requires_grad=True))
    except TypeError as error:
        if qml.__version__ == "0.42.3" and "complex" in str(error) and "NotImplementedType" in str(error):
            pytest.xfail("Observed public PL 0.42.3 / Autograd complex NotImplementedType failure; native result computed first, not an oracle match.")
        raise


def test_device_scalar_rotation_hessian_public_black_box():
    def native(t, x):
        t.ry(x, 0)
        return t.expval(PauliZ(0))
    def public(x):
        qml.RY(x, wires=0)
        return qml.expval(qml.PauliZ(0))
    actual = native_hessian(native, .3, 1)
    np.testing.assert_allclose(actual, public_hessian(public, .3, 1), atol=1e-10, rtol=0)


def test_device_mixed_rotation_observable_hessian_public_black_box():
    def native(t, x):
        t.ry(x[0], 0); t.rz(x[1], 0)
        return t.expval(Hamiltonian([(1., PauliX(0)), (.3, PauliZ(0))]))
    def public(x):
        qml.RY(x[0], wires=0); qml.RZ(x[1], wires=0)
        return qml.expval(qml.PauliX(0)+.3*qml.PauliZ(0))
    point = np.array([.3, -.2])
    actual = native_hessian(native, point, 1)
    np.testing.assert_allclose(actual, public_hessian(public, point, 1), atol=1e-10, rtol=0)


def test_device_entangled_variance_hessian_public_black_box():
    def native(t, x):
        t.rxx(x, 0, 1)
        return t.var(PauliZ(0))
    def public(x):
        qml.IsingXX(x, wires=[0, 1])
        return qml.var(qml.PauliZ(0))
    actual = native_hessian(native, .3, 2)
    np.testing.assert_allclose(actual, public_hessian(public, .3, 2), atol=1e-10, rtol=0)


def test_device_nonlinear_coefficient_curvature_public_black_box():
    def native(t, x):
        t.ry(x[0]*x[1], 0)
        return t.expval(Hamiltonian([(.7+x[1]**2, PauliX(0))]))
    def public(x):
        qml.RY(x[0]*x[1], wires=0)
        return qml.expval(qml.Hamiltonian([.7+x[1]**2], [qml.PauliX(0)]))
    point = np.array([.3, -.2])
    actual = native_hessian(native, point, 1)
    np.testing.assert_allclose(actual, public_hessian(public, point, 1), atol=1e-10, rtol=0)


def test_public_torch_second_oracles_for_complex_autograd_limited_problems():
    torch = pytest.importorskip("torch")
    # Additional actual public oracles for the same two mathematical problems;
    # these do not convert the retained Autograd xfails into matches.
    def native_mixed(t, x):
        t.ry(x[0], 0); t.rz(x[1], 0)
        return t.expval(Hamiltonian([(1., PauliX(0)), (.3, PauliZ(0))]))
    def public_mixed(x):
        qml.RY(x[0], wires=0); qml.RZ(x[1], wires=0)
        return qml.expval(qml.PauliX(0)+.3*qml.PauliZ(0))
    def native_variance(t, x):
        t.rxx(x, 0, 1)
        return t.var(PauliZ(0))
    def public_variance(x):
        qml.IsingXX(x, wires=[0, 1])
        return qml.var(qml.PauliZ(0))
    for native, public, point, width in ((native_mixed, public_mixed, np.array([.3, -.2]), 1),
                                        (native_variance, public_variance, .3, 2)):
        actual = native_hessian(native, point, width)
        oracle = qml.QNode(public, qml.device("default.qubit", wires=width), interface="torch", diff_method="backprop", max_diff=2)
        expected = torch.autograd.functional.hessian(oracle, torch.tensor(point, dtype=torch.float64, requires_grad=True))
        np.testing.assert_allclose(actual, expected.detach().numpy(), atol=1e-10, rtol=0)
