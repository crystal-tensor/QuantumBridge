# Copyright 2026 QuantumBridge Contributors. Apache-2.0.
"""Existing observable conversions under the new fixed-matrix tensor rule."""

import numpy as np
import pytest

import quantumbridge as qb
from quantumbridge import qml
from quantumbridge.operators import SparsePauliOperator
from quantumbridge.qml import QNode
from test_native_tf_mps_exact_closure import POINT, fixture, tf
from test_native_tf_mps_tensor_chain import no_dense_or_host


@pytest.mark.parametrize("width", [2, 6])
def test_fixed_real_observable_forms_keep_full_multioutput_curvature(width, monkeypatch):
    _, base = fixture(width, 2)
    word = qb.PauliY(0).tensor(qb.PauliZ(width - 1))
    total = qml.Hamiltonian([.31, -.27, .4],
        [qml.Hadamard(0), word, qml.Identity(width - 1)])
    sparse = SparsePauliOperator.from_list([
        ("X" + "I" * (width - 2) + "Y", .17), ("I" * width, -.21)])
    observables = (qb.PauliString(()), word, total, sparse)

    def program(tape, point):
        base.fn(tape, point)
        return tuple(tape.expval(observable) for observable in observables)

    dense = QNode(program, width, max_diff=2, device=qb.StatevectorDevice())
    y, j, h = (np.array(dense(POINT)), np.array(dense.jacobian(POINT)),
        np.array(dense.hessian(POINT)))
    node = QNode(program, width, max_diff=2, interface="tensorflow",
        device=qb.MatrixProductStateDevice(max_bond_dim=16, cutoff=0))
    no_dense_or_host(monkeypatch)
    point = tf.constant(POINT)
    with tf.GradientTape(persistent=True) as second:
        second.watch(point)
        with tf.GradientTape(persistent=True) as first:
            first.watch(point)
            value = tf.stack(node(point))
        jacobian = first.jacobian(value, point, experimental_use_pfor=False)
    hessian = second.jacobian(jacobian, point, experimental_use_pfor=False)
    for actual, expected in zip((value, jacobian, hessian), (y, j, h)):
        np.testing.assert_allclose(actual, expected, atol=2e-9, rtol=0)
    np.testing.assert_allclose(value[0], 1., atol=2e-12, rtol=0)
    np.testing.assert_allclose(jacobian[0], 0., atol=2e-10, rtol=0)
    np.testing.assert_allclose(hessian[0], 0., atol=2e-9, rtol=0)
    assert node.last_metadata["tensor_plan_work"]["outputs"] == 4
    assert node.last_metadata["tensor_plan_work"]["observable_contraction_bytes_bound"] > 0
