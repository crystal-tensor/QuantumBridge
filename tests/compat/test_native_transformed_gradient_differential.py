# Copyright 2026 QuantumBridge Contributors.
# Licensed under the Apache License, Version 2.0.
"""Public quantum-gradient oracles only; native production uses no SDK."""

import numpy as np
import pytest
qml = pytest.importorskip("pennylane")

from quantumbridge import qchem
from quantumbridge.qml import QNode
from quantumbridge.transforms import split_non_commuting,merge_rotations
from quantumbridge.utils.math import Hamiltonian,PauliX,PauliZ,PauliString


def public_node(function,wires=2,shots=None):
    node = qml.QNode(function,qml.device("default.qubit",wires=wires,shots=shots,seed=19),
                     interface="autograd",diff_method="parameter-shift")
    return qml.transforms.split_non_commuting(node,grouping_strategy="qwc")


def gradient(oracle,x=.37):
    return float(qml.grad(oracle)(qml.numpy.array(x,requires_grad=True)))


def test_public_qwc_transformed_shift_derivative_matches_native_quantum_means():
    def public(x):
        qml.RY(x,0)
        return qml.expval(.7*qml.X(0)+.2*qml.X(0)@qml.Z(1))
    def native(tape,x):
        tape.ry(x,0)
        return tape.expval(Hamiltonian([(.7,PauliX(0)),(.2,PauliX(0).tensor(PauliZ(1)))]))
    node = split_non_commuting(QNode(native,2,diff_method="parameter-shift"))
    assert node.gradient(.37) == pytest.approx(gradient(public_node(public)),abs=1e-12)


def test_public_shared_nonlinear_angles_survive_native_merge_and_grouping():
    def public(x):
        qml.RY(qml.numpy.sin(x),0)
        qml.RY(2*x,0)
        return qml.expval(.7*qml.Z(0)+.2*qml.X(0))
    def native(tape,x):
        tape.ry(np.sin(x),0)
        tape.ry(2*x,0)
        return tape.expval(Hamiltonian([(.7,PauliZ(0)),(.2,PauliX(0))]))
    node = split_non_commuting(merge_rotations(QNode(native,2)))
    assert node.gradient(.37) == pytest.approx(gradient(public_node(public)),abs=1e-12)


def test_public_same_input_controls_gate_and_trainable_hamiltonian_coefficients():
    def public(x):
        qml.RY(x,0)
        return qml.expval(qml.Hamiltonian([x,x*x],[qml.X(0),qml.Z(0)]))
    def native(tape,x):
        tape.ry(x,0)
        return tape.expval(Hamiltonian([(x,PauliX(0)),(x*x,PauliZ(0))]))
    assert split_non_commuting(QNode(native,2)).gradient(.37) == pytest.approx(gradient(public_node(public)),abs=1e-12)


def test_public_multiple_outputs_cotangent_cost_matches_native_vjp():
    def public(x):
        qml.RY(x,0)
        return qml.expval(qml.Z(0)),qml.expval(qml.X(0))
    oracle = public_node(public)
    def cost(x):
        a,b = oracle(x)
        return 2*a+3*b
    def native(tape,x):
        tape.ry(x,0)
        return (tape.expval(PauliZ(0)),tape.expval(PauliX(0)))
    assert split_non_commuting(QNode(native,2)).compute_vjp((2.,3.),.37) == pytest.approx(gradient(cost),abs=1e-12)


def test_public_analytic_variance_gradient_uses_the_mean_chain_rule():
    def public(x):
        qml.RY(x,0)
        return qml.var(qml.Z(0))
    def native(tape,x):
        tape.ry(x,0)
        return tape.var(PauliZ(0))
    assert split_non_commuting(QNode(native,2)).gradient(.37) == pytest.approx(gradient(public_node(public)),abs=1e-12)


def test_public_identity_duplicate_and_trainable_offset_derivatives():
    def public(x):
        qml.RY(x,0)
        return qml.expval(qml.Hamiltonian([1.,2.,x*x],[qml.Z(0),qml.Z(0),qml.Identity(0)]))
    def native(tape,x):
        tape.ry(x,0)
        return tape.expval(Hamiltonian([(1.,PauliZ(0)),(2.,PauliZ(0)),(x*x,PauliString([]))]))
    assert split_non_commuting(QNode(native,2)).gradient(.37) == pytest.approx(gradient(public_node(public)),abs=1e-12)


def test_public_finite_shot_shift_gradient_is_a_statistical_not_bitwise_oracle():
    def public(x):
        qml.RY(x,0)
        return qml.expval(.7*qml.X(0)+.2*qml.X(0)@qml.Z(1))
    def native(tape,x):
        tape.ry(x,0)
        return tape.expval(Hamiltonian([(.7,PauliX(0)),(.2,PauliX(0).tensor(PauliZ(1)))]))
    expected = gradient(public_node(public,shots=10001))
    actual = split_non_commuting(QNode(native,2,shots=10001,seed=19,diff_method="parameter-shift")).gradient(.37)
    assert abs(actual-expected) < .05
    assert abs(actual-.9*np.cos(.37)) < .05


def test_public_geometry_h2_excitation_energy_gradient_after_qwc_grouping():
    problem = qchem.molecular_hamiltonian_native(qchem.Molecule(["H","H"],[(0,0,0),(0,0,1.4)],unit="bohr"))
    coefficients,words = [],[]
    for coefficient,word in problem.hamiltonian.to_quantumbridge().terms:
        factors = [{"X":qml.X,"Y":qml.Y,"Z":qml.Z}[label](wire) for wire,label in word.terms if label != "I"]
        coefficients.append(coefficient)
        words.append(qml.prod(*factors) if factors else qml.Identity(0))
    hamiltonian = qml.Hamiltonian(coefficients,words)
    def public(x):
        qml.X(0)
        qml.X(1)
        qml.DoubleExcitation(-x,[0,1,2,3])
        return qml.expval(hamiltonian)
    def native(tape,x):
        tape.x(0)
        tape.x(1)
        qchem.apply_fermionic_excitation(tape,x,[0,1,2,3])
        return tape.expval(problem.hamiltonian)
    assert split_non_commuting(QNode(native,4)).gradient(.37) == pytest.approx(gradient(public_node(public,wires=4)),abs=2e-11)
