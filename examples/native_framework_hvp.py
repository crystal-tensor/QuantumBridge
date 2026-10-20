# Copyright 2026 QuantumBridge Contributors.
# Licensed under the Apache License, Version 2.0.
"""Actual framework HVPs, optionally sharing one fixed-geometry native H2 build."""

import argparse
from contextlib import nullcontext
import json
from unittest.mock import patch

import numpy as np

from quantumbridge import Hamiltonian, PauliX, PauliZ, qchem
from quantumbridge.diff import HigherOrderLimits
from quantumbridge.qml import QNode
from quantumbridge.transforms import TransformProgram, merge_rotations, split_non_commuting


def framework_product(interface, program, point, direction):
    node = TransformProgram((merge_rotations, split_non_commuting))(
        QNode(program, 4, interface=interface, max_diff=2, diff_method="parameter-shift",
              higher_order_limits=HigherOrderLimits(max_hessian_elements=1)))
    if interface == "torch":
        import torch
        x = torch.tensor(point, dtype=torch.float64, requires_grad=True)
        value = node(x)
        first = torch.autograd.grad(value, x, create_graph=True)[0]
        product = torch.autograd.grad(torch.sum(first*torch.as_tensor(direction, dtype=x.dtype)), x)[0].detach().numpy()
        value = value.detach().numpy()
    elif interface == "autograd":
        import autograd
        import autograd.numpy as anp
        value = node(point)
        product = autograd.grad(lambda x: anp.sum(autograd.grad(node)(x)*direction))(anp.array(point))
    elif interface == "jax":
        import jax
        import jax.numpy as jnp
        x = jnp.asarray(point)
        value = node(x)
        product = jax.jvp(jax.grad(node), (x,), (jnp.asarray(direction, dtype=x.dtype),))[1]
    else:
        import tensorflow as tf
        x = tf.Variable(point, dtype=tf.float64)
        with tf.GradientTape() as outer:
            with tf.GradientTape() as inner:
                value = node(x)
            first = inner.gradient(value, x)
            contracted = tf.reduce_sum(first*tf.convert_to_tensor(direction, dtype=x.dtype))
        product = outer.gradient(contracted, x)
    return float(value), np.asarray(product, dtype=float)


def main(interfaces=("torch",), chemistry=False):
    builds = 0
    if chemistry:
        problem = qchem.molecular_hamiltonian_native(qchem.Molecule(["H", "H"], [(0, 0, 0), (0, 0, 1.4)], unit="bohr"))
        builds += 1
        matrix = problem.hamiltonian.matrix()
        def circuit(t, angle):
            t.x(0); t.x(1)
            qchem.apply_fermionic_excitation(t, angle, [0, 1, 2, 3])
            return t.expval(problem.hamiltonian)
        point, direction = .3, .4
        a, d, b = matrix[12, 12].real, matrix[3, 3].real, matrix[12, 3].real
        expected_value = (a+d)/2+(a-d)*np.cos(point)/2+b*np.sin(point)
        expected = direction*(-(a-d)*np.cos(point)/2-b*np.sin(point))
    else:
        def circuit(t, x):
            t.ry(x[0]*x[1], 0)
            return t.expval(Hamiltonian([(.7+.1*x[0], PauliX(0)), (.2, PauliZ(0))]))
        point, direction = np.array([.7, .2]), np.array([.4, -.3])
        angle, a = point.prod(), .7+.1*point[0]
        gradient = np.array([point[1], point[0]])
        first, second = a*np.cos(angle)-.2*np.sin(angle), -a*np.sin(angle)-.2*np.cos(angle)
        cross = np.array([.1, 0.])
        hessian = second*np.outer(gradient, gradient)+first*np.array([[0., 1.], [1., 0.]])+np.cos(angle)*(np.outer(cross, gradient)+np.outer(gradient, cross))
        expected_value, expected = a*np.sin(angle)+.2*np.cos(angle), hessian @ direction
    receipts = []
    guard = patch.object(qchem, "molecular_hamiltonian_native", side_effect=AssertionError("Fixed-geometry integrals must not be rebuilt during framework HVPs")) if chemistry else nullcontext()
    with guard:
        for interface in interfaces:
            value, product = framework_product(interface, circuit, point, direction)
            tolerance = 5e-6 if interface == "jax" else 3e-10
            np.testing.assert_allclose(value, expected_value, atol=tolerance, rtol=0)
            np.testing.assert_allclose(product, expected, atol=tolerance, rtol=0)
            receipts.append({"interface": interface, "value": value, "hvp": product.tolist(), "native_full_hessian_budget": 1})
    result = {"geometry_builds": builds, "fixed_geometry": bool(chemistry), "receipts": receipts}
    print(json.dumps(result, indent=2))
    return result


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--interface", choices=("torch", "autograd", "jax", "tf", "all"), default="torch")
    parser.add_argument("--chemistry", action="store_true")
    args = parser.parse_args()
    selected = ("torch", "autograd", "jax", "tf") if args.interface == "all" else (args.interface,)
    main(selected, args.chemistry)
