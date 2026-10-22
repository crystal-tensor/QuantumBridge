# Copyright 2026 QuantumBridge Contributors.
# Licensed under the Apache License, Version 2.0.
"""Symbolic ASTs reach native complex operators and independent quantum calculus."""

import numpy as np
import pytest

from quantumbridge import Circuit, Parameter, ParameterVector, PauliZ, UnsupportedFeature
from quantumbridge.compiler import native_transpile
from quantumbridge.information import Operator, Statevector, DensityMatrix
from quantumbridge.qml import QNode
import math


POINTS = [(.4, -.2), (-.7, .5), (.8, 1.1)]


def circuit_fixture():
    vector = ParameterVector("v", 2)
    p, q = vector
    expression = (p*q+p*p).sin()+(2*p-q).exp()
    circuit = Circuit(2).ry(expression, 0).rx(p*q, 1).cz(0, 1)
    circuit.global_phase = p.sin()/7
    return vector, expression, circuit


def independent_reference(p, q):
    a, b = p*q+p*p, 2*p-q
    da, db = np.array([q+2*p, p]), np.array([2., -1.])
    f, g = np.sin(a)+np.exp(b), p*q
    df = np.cos(a)*da+np.exp(b)*db
    hf = -np.sin(a)*np.outer(da, da)+np.cos(a)*np.array([[2., 1.], [1., 0.]])+np.exp(b)*np.outer(db, db)
    dg, hg = np.array([q, p]), np.array([[0., 1.], [1., 0.]])
    expected = np.cos(f)*np.cos(g)
    gradient = -np.sin(f)*np.cos(g)*df-np.cos(f)*np.sin(g)*dg
    hessian = (-np.cos(f)*np.cos(g)*(np.outer(df, df)+np.outer(dg, dg))
               +np.sin(f)*np.sin(g)*(np.outer(df, dg)+np.outer(dg, df))
               -np.sin(f)*np.cos(g)*hf-np.cos(f)*np.sin(g)*hg)
    ry = np.array([[np.cos(f/2), -np.sin(f/2)], [np.sin(f/2), np.cos(f/2)]])
    rx = np.array([[np.cos(g/2), -1j*np.sin(g/2)], [-1j*np.sin(g/2), np.cos(g/2)]])
    matrix = np.exp(1j*np.sin(p)/7)*np.diag([1, 1, 1, -1])@np.kron(ry, rx)
    return expected, gradient, hessian, matrix


@pytest.mark.parametrize("method", ["parameter-shift", "adjoint"])
@pytest.mark.parametrize("pvalue,qvalue", POINTS)
def test_symbolic_functions_reach_native_gradient_mixed_hessian_and_streamed_hvp(method, pvalue, qvalue):
    vector, expression, circuit = circuit_fixture()
    observable = PauliZ(0).tensor(PauliZ(1))
    node = QNode.from_circuit(circuit, observable, diff_method=method, max_diff=2)
    point, tangent = np.array([pvalue, qvalue]), np.array([.4, -.2])
    expected, gradient, hessian, matrix = independent_reference(*point)
    assert node(point) == pytest.approx(expected, abs=2e-14)
    np.testing.assert_allclose(node.compute_jacobian(point), gradient, atol=8e-11, rtol=0)
    np.testing.assert_allclose(node.compute_hessian(point), hessian, atol=6e-10, rtol=0)
    np.testing.assert_allclose(node.compute_hvp(tangent, point), hessian@tangent, atol=6e-10, rtol=0)
    assert node(point) == pytest.approx(expected, abs=2e-14)
    partial = circuit.assign_parameters({vector[0]: pvalue})
    partial_node = QNode.from_circuit(partial, observable, diff_method=method)
    assert partial_node(qvalue) == pytest.approx(expected, abs=2e-14)
    assert partial_node.compute_jacobian(qvalue) == pytest.approx(gradient[1], abs=8e-11)
    np.testing.assert_allclose(Operator(partial.assign_parameters({vector[1]: qvalue})).data, matrix, atol=5e-15, rtol=0)


@pytest.mark.parametrize("pvalue,qvalue", POINTS)
def test_symbolic_composites_phase_compiler_and_mixed_state_keep_full_complex_algebra(pvalue, qvalue):
    vector, expression, circuit = circuit_fixture()
    bound = circuit.assign_parameters({vector: [pvalue, qvalue]})
    _, _, _, matrix = independent_reference(pvalue, qvalue)
    controlled = np.eye(8, dtype=complex)
    controlled[4:, 4:] = matrix
    np.testing.assert_allclose(Operator(bound.control()).data, controlled, atol=7e-15, rtol=0)
    parent = Circuit(2).append(circuit.to_instruction(), (0, 1)).append(circuit.to_instruction(), (0, 1))
    parent = parent.assign_parameters({vector[0]: pvalue}).assign_parameters({vector[1]: qvalue})
    np.testing.assert_allclose(Operator(parent).data, matrix@matrix, atol=7e-15, rtol=0)
    initial = np.array([1, 2j, -3, .4+.7j]); initial /= np.linalg.norm(initial)
    mixed = .3*np.outer(initial, initial.conj())+.7*np.eye(4)/4
    np.testing.assert_allclose(Statevector(initial).evolve(bound).data, matrix@initial, atol=5e-15, rtol=0)
    np.testing.assert_allclose(DensityMatrix(mixed).evolve(bound).data, matrix@mixed@matrix.conj().T, atol=5e-15, rtol=0)
    compiled = native_transpile(circuit, basis_gates=["rx", "ry", "rz", "phase", "cx", "h"], optimization_level=1)
    np.testing.assert_allclose(Operator(compiled.assign_parameters({vector: [pvalue, qvalue]})).data, matrix, atol=8e-15, rtol=0)


@pytest.mark.parametrize("pvalue,qvalue", POINTS)
def test_symbolic_instruction_formal_mapping_inverse_and_power_remain_executable(pvalue, qvalue):
    vector, _, circuit = circuit_fixture()
    target, other = Parameter("target"), Parameter("other")
    instruction = circuit.to_instruction(parameter_map={vector[0]: target.sin(), vector[1]: other.exp()})
    mapped = Circuit(2).append(instruction, (0, 1))
    bound = mapped.assign_parameters({target: pvalue}).assign_parameters({other: qvalue})
    _, _, _, expected = independent_reference(np.sin(pvalue), np.exp(qvalue))
    np.testing.assert_allclose(Operator(bound).data, expected, atol=7e-15, rtol=0)
    inverse = mapped.inverse().assign_parameters({target: pvalue, other: qvalue})
    np.testing.assert_allclose(Operator(inverse).data, expected.conj().T, atol=7e-15, rtol=0)
    powered = mapped.power(2).assign_parameters({target: pvalue, other: qvalue})
    np.testing.assert_allclose(Operator(powered).data, expected@expected, atol=8e-15, rtol=0)


ELEMENTARY = [
    ("sin", math.sin, math.cos, lambda x: -math.sin(x)),
    ("cos", math.cos, lambda x: -math.sin(x), lambda x: -math.cos(x)),
    ("tan", math.tan, lambda x: 1/math.cos(x)**2, lambda x: 2*math.tan(x)/math.cos(x)**2),
    ("exp", math.exp, math.exp, math.exp),
    ("log", math.log, lambda x: 1/x, lambda x: -1/x**2),
    ("arcsin", math.asin, lambda x: 1/math.sqrt(1-x*x), lambda x: x/(1-x*x)**1.5),
    ("arccos", math.acos, lambda x: -1/math.sqrt(1-x*x), lambda x: -x/(1-x*x)**1.5),
    ("arctan", math.atan, lambda x: 1/(1+x*x), lambda x: -2*x/(1+x*x)**2),
    ("abs", abs, lambda x: 1, lambda x: 0),
    ("sign", lambda x: 1, lambda x: 0, lambda x: 0),
    ("conjugate", lambda x: x, lambda x: 1, lambda x: 0),
]


@pytest.mark.parametrize("value", [.2, .4, .8])
@pytest.mark.parametrize("name,forward,first,second", ELEMENTARY)
@pytest.mark.parametrize("method", ["parameter-shift", "adjoint"])
def test_each_elementary_family_reaches_native_quantum_second_chain_rule(name, forward, first, second, method, value):
    p = Parameter("p")
    node = QNode.from_circuit(Circuit(1).ry(getattr(p, name)(), 0), PauliZ(0), diff_method=method, max_diff=2)
    f, df, ddf = forward(value), first(value), second(value)
    assert node(value) == pytest.approx(math.cos(f), abs=2e-14)
    assert node.compute_jacobian(value) == pytest.approx(-math.sin(f)*df, abs=8e-11)
    assert node.compute_hvp(.4, value) == pytest.approx(.4*(-math.cos(f)*df**2-math.sin(f)*ddf), abs=5e-10)


@pytest.mark.parametrize("name,point", [("abs", 0.), ("sign", 0.), ("arcsin", 1.), ("arccos", 1.)])
def test_native_quantum_forward_does_not_make_nondifferentiable_inputs_smooth(name, point):
    p = Parameter("p")
    node = QNode.from_circuit(Circuit(1).ry(getattr(p, name)(), 0), PauliZ(0), max_diff=2)
    assert math.isfinite(node(point))
    with pytest.raises((ValueError, UnsupportedFeature), match="zero|strictly inside"):
        node.compute_hvp(.4, point)
