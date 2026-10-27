# Copyright 2026 QuantumBridge Contributors. Apache-2.0.
"""Protect the supported TF nested-reverse MPS path with wide directives."""

import json
from pathlib import Path

import numpy as np
import pytest

import quantumbridge as qb
from quantumbridge.information import MatrixProductState
from quantumbridge.qml import QNode

ORACLE = json.loads((Path(__file__).parents[1] / "information/data/native_mixed_power_oracles.json").read_text())


@pytest.mark.parametrize("with_delay", [False, True])
def test_actual_tf_graph_second_derivative_ignores_barrier_entanglement_cost(with_delay, monkeypatch):
    tf = pytest.importorskip("tensorflow")
    from quantumbridge.core.gates import Gate
    from quantumbridge.information import Operator
    p, q = qb.Parameter("p"), qb.Parameter("q")
    source = qb.QuantumCircuit(100)
    source.append(qb.Circuit(1).rx(p, 0).rz(q, 0).to_gate().power(0.5, annotated=True), (99,))
    source.barrier()
    if with_delay:
        source.delay(3, 99)
    node = QNode.from_circuit(source, qb.PauliZ(99), interface="tensorflow", max_diff=2,
        device=qb.MatrixProductStateDevice(max_bond_dim=None, cutoff=0))
    def forbidden(*args, **kwargs):
        pytest.fail("Dense materialization in 100-wire MPS graph")
    for cls, name in [(MatrixProductState, "statevector"), (MatrixProductState, "reduced_density_matrix"),
                      (Gate, "to_matrix"), (Operator, "__init__"),
                      (qb.StatevectorDevice, "statevector"), (qb.DensityMatrixDevice, "density_matrix")]:
        monkeypatch.setattr(cls, name, forbidden)
    @tf.function(autograph=False, jit_compile=False)
    def evaluate(point):
        with tf.GradientTape() as outer:
            outer.watch(point)
            with tf.GradientTape() as inner:
                inner.watch(point)
                value = node(point)
            gradient = inner.gradient(value, point)
            contraction = tf.reduce_sum(gradient*tf.constant([0.4, -0.3], tf.float64))
        return value, gradient, outer.gradient(contraction, point)
    value, gradient, hvp = evaluate(tf.constant(ORACLE["point"], tf.float64))
    expected = ORACLE["su2"][0]
    np.testing.assert_allclose(value, expected["value"], atol=8e-12, rtol=0)
    np.testing.assert_allclose(gradient, expected["gradient"], atol=8e-11, rtol=0)
    np.testing.assert_allclose(hvp, np.array(expected["hessian"]) @ [0.4, -0.3], atol=2e-9, rtol=0)
