# Copyright 2026 QuantumBridge Contributors.
# Licensed under the Apache License, Version 2.0.
# Independent analytic second-order scalar and directional chain-rule tests.

import numpy as np
import pytest

from quantumbridge.core.classical import UnsupportedFeature
from quantumbridge.diff.higher_order_limits import HigherOrderLimits
from quantumbridge.diff.second_trace import SecondContext


def test_nonlinear_gate_and_coefficient_second_chain_rule():
    context = SecondContext(1)
    x = context.variable(.37, 0)
    g = np.sin(x)+2*x
    result = (.9+.1*x)*np.sin(g)
    a, angle, first = .937, np.sin(.37)+.74, np.cos(.37)+2
    expected = .2*np.cos(angle)*first-a*np.sin(angle)*first**2-a*np.cos(angle)*np.sin(.37)
    np.testing.assert_allclose(result.second, [[expected]], atol=1e-12, rtol=0)


def test_multivariable_mixed_partials_match_analytic_reference():
    context = SecondContext(2)
    x, y = context.variable(.7, 0), context.variable(.2, 1)
    result = np.sin(x*y)+np.exp(x)+y**3
    expected = [[np.exp(.7)-.04*np.sin(.14), np.cos(.14)-.14*np.sin(.14)],
                [np.cos(.14)-.14*np.sin(.14), 1.2-.49*np.sin(.14)]]
    np.testing.assert_allclose(result.second, expected, atol=1e-12, rtol=0)
    np.testing.assert_allclose(result.derivative, [.2*np.cos(.14)+np.exp(.7), .7*np.cos(.14)+.12], atol=1e-12)


def test_directional_trace_does_not_construct_full_hessian(monkeypatch):
    monkeypatch.setattr(np, "eye", lambda *a, **k: pytest.fail("HVP trace must not allocate an identity/Hessian"))
    context = SecondContext(2, [.4, -.3])
    x, y = context.variable(.7, 0), context.variable(.2, 1)
    result = np.sin(x*y)+np.exp(x)+y**3
    expected = np.array([[np.exp(.7)-.04*np.sin(.14), np.cos(.14)-.14*np.sin(.14)],
                         [np.cos(.14)-.14*np.sin(.14), 1.2-.49*np.sin(.14)]]) @ [.4, -.3]
    assert result.second.shape == (2, 1)
    np.testing.assert_allclose(result.second[:, 0], expected, atol=1e-12, rtol=0)


@pytest.mark.parametrize("function,point,expected", [
    (lambda x: 1/x, .7, 2/.7**3),
    (lambda x: np.log(x), .7, -1/.7**2),
    (lambda x: np.sqrt(x), .7, -.25/.7**1.5),
    (lambda x: np.tan(x), .3, 2*np.tan(.3)/np.cos(.3)**2),
    (lambda x: x**2, 0., 2.),
    (lambda x: x**0, 0., 0.),
    (lambda x: x**1, 0., 0.),
    (lambda x: abs(x), -.3, 0.),
    (lambda x: 2**x, .3, 2**.3*np.log(2)**2),
])
def test_unary_and_power_second_derivatives(function, point, expected):
    context = SecondContext(1)
    result = function(context.variable(point, 0))
    np.testing.assert_allclose(result.second, [[expected]], atol=1e-11, rtol=0)


def test_variable_power_full_mixed_hessian():
    context = SecondContext(2)
    x, y = context.variable(.7, 0), context.variable(1.3, 1)
    result = x**y
    expected = [[1.3*.3*.7**(-.7), .7**.3*(1+1.3*np.log(.7))],
                [.7**.3*(1+1.3*np.log(.7)), .7**1.3*np.log(.7)**2]]
    np.testing.assert_allclose(result.second, expected, atol=1e-12, rtol=0)


def test_structural_dependency_survives_stationary_zero_direction():
    context = SecondContext(1, [0.])
    x, constant = context.variable(0., 0), context.constant(.2)
    for result in (x*x, np.cos(x), constant+x*x, constant*x*x, -(x*x), 2**(x*x)):
        assert result.depends_on_inputs
        np.testing.assert_array_equal(result.derivative, [0.])
        np.testing.assert_array_equal(result.second, [[0.]])
    assert not constant.depends_on_inputs
    assert not (constant+constant).depends_on_inputs
    assert not (x**0).depends_on_inputs
    assert (x**1).depends_on_inputs
    with pytest.raises(UnsupportedFeature, match="positive base"):
        (-2)**(x*x)


def test_injected_derivative_dependency_defaults_and_invalid_flag():
    from quantumbridge.diff.second_trace import SecondDual
    context = SecondContext(1, [0.])
    assert SecondDual(1., [1.], [[0.]], context).depends_on_inputs
    assert not SecondDual(1., [0.], [[0.]], context).depends_on_inputs
    with pytest.raises(TypeError, match="boolean"):
        SecondDual(1., [0.], [[0.]], context, depends_on_inputs=1)


def test_reservations_reject_before_computing_the_next_result():
    context = SecondContext(2, limits=HigherOrderLimits(max_memory_bytes=100))
    x = context.variable(.3, 0)
    before = context.nodes
    with pytest.raises(MemoryError, match="max_memory_bytes"): x*x
    assert context.nodes == before
    with pytest.raises(MemoryError, match="max_parameter_graph_nodes"):
        limited = SecondContext(1, limits=HigherOrderLimits(max_parameter_graph_nodes=1))
        limited.variable(.3, 0)+1


def test_invalid_contexts_nonfinite_and_nonsmooth_inputs_reject():
    for options in ({"max_derivative_order": 3}, {"max_input_parameters": False}, {"max_memory_bytes": 0}):
        with pytest.raises(ValueError): HigherOrderLimits(**options)
    with pytest.raises(MemoryError): SecondContext(2, limits=HigherOrderLimits(max_input_parameters=1))
    with pytest.raises(ValueError): SecondContext(2, [1.])
    with pytest.raises(ValueError): SecondContext(1, [float("nan")])
    with pytest.raises(TypeError): SecondContext(1, limits={})
    context = SecondContext(1)
    with pytest.raises(ValueError): context.variable(float("nan"), 0)
    with pytest.raises(UnsupportedFeature): abs(context.variable(0., 0))
    with pytest.raises(UnsupportedFeature): float(context.variable(.3, 0))
    with pytest.raises(UnsupportedFeature): bool(context.variable(.3, 0))
    with pytest.raises(ValueError): context.variable(.3, 0)+SecondContext(1).variable(.4, 0)
