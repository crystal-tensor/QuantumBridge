# Copyright 2026 QuantumBridge Contributors.
# Licensed under the Apache License, Version 2.0.
# Public numerical black boxes only; no upstream implementation/test ports.

import numpy as np
import pytest

from quantumbridge import Hamiltonian, PauliX, PauliZ
from quantumbridge.qml import QNode
from quantumbridge.transforms import split_non_commuting


@pytest.mark.parametrize("scenario", ["ry", "controlled_two_frequencies", "nonlinear_qwc_loss", "live_coefficient_qwc"])
@pytest.mark.parametrize("native_method,public_method", [
    ("parameter-shift", "parameter-shift"), ("parameter-shift", "backprop"), ("adjoint", "backprop")])
def test_public_pennylane_second_derivatives(scenario, native_method, public_method):
    pl = pytest.importorskip("pennylane")
    autograd = pytest.importorskip("autograd")
    anp = pytest.importorskip("autograd.numpy")
    def native(t, x):
        if scenario == "controlled_two_frequencies":
            t.h(0); t.crx(x[0], 0, 1)
            return t.expval(Hamiltonian([(1., PauliX(0)), (.3, PauliZ(1))]))
        if scenario in {"nonlinear_qwc_loss", "live_coefficient_qwc"}:
            t.ry(anp.sin(x[0])+2*x[1], 0)
            coefficient = .7+.1*x[0] if scenario == "live_coefficient_qwc" else .7
            return t.expval(Hamiltonian([(coefficient, PauliX(0)), (.2, PauliX(0).tensor(PauliZ(1)))]))
        t.ry(x[0], 0)
        return t.expval(PauliZ(0))
    def public(x):
        if scenario == "controlled_two_frequencies":
            pl.Hadamard(wires=0); pl.CRX(x[0], wires=[0, 1])
            return pl.expval(pl.X(0)+.3*pl.Z(1))
        if scenario in {"nonlinear_qwc_loss", "live_coefficient_qwc"}:
            pl.RY(pl.numpy.sin(x[0])+2*x[1], wires=0)
            coefficient = .7+.1*x[0] if scenario == "live_coefficient_qwc" else .7
            return pl.expval(pl.Hamiltonian([coefficient, .2], [pl.X(0), pl.X(0)@pl.Z(1)]))
        pl.RY(x[0], wires=0)
        return pl.expval(pl.Z(0))
    a = QNode(native, 2, interface="autograd", max_diff=2, diff_method=native_method)
    b = pl.QNode(public, pl.device("default.qubit", wires=2), interface="autograd", diff_method=public_method, max_diff=2)
    nonlinear = scenario in {"nonlinear_qwc_loss", "live_coefficient_qwc"}
    if nonlinear:
        a, b = split_non_commuting(a), pl.transforms.split_non_commuting(b)
    def loss(function, x):
        value = function(x)
        return value*value+.3*value if nonlinear else value
    point = [.37, .2] if nonlinear else [.37]
    left = autograd.hessian(lambda x: loss(a, x))(anp.array(point))
    if scenario == "live_coefficient_qwc":
        x, y = point
        scale, angle = .9+.1*x, np.sin(x)+2*y
        value = scale*np.sin(angle)
        gradient = np.array([.1*np.sin(angle)+scale*np.cos(angle)*np.cos(x), 2*scale*np.cos(angle)])
        mixed = .2*np.cos(angle)-2*scale*np.sin(angle)*np.cos(x)
        second = np.array([[.2*np.cos(angle)*np.cos(x)-scale*np.sin(angle)*np.cos(x)**2-scale*np.cos(angle)*np.sin(x), mixed],
                           [mixed, -4*scale*np.sin(angle)]])
        np.testing.assert_allclose(left, (2*value+.3)*second+2*np.outer(gradient, gradient), atol=1e-11)
    try:
        right = pl.jacobian(pl.grad(lambda x: loss(b, x)))(pl.numpy.array(point, requires_grad=True))
    except TypeError as error:
        if public_method == "parameter-shift" and nonlinear and "NotImplementedType" in str(error):
            pytest.xfail("Public transformed QWC shift Hessian raised NotImplementedType; not numerical parity evidence")
        raise
    if np.asarray(right).dtype.kind == "O" and any(type(value).__module__.startswith("autograd") for value in np.asarray(right).flat):
        pytest.xfail("Public transformed QWC Hessian returned unresolved ArrayBox objects; not numerical parity evidence")
    np.testing.assert_allclose(left, right, atol=2e-10, rtol=0)
