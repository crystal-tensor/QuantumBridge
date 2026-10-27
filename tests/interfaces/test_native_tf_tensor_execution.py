# Copyright 2026 QuantumBridge Contributors. Apache-2.0.
"""Real low-qubit QNodes; pure tensor probes cannot satisfy this contract."""

import json
from pathlib import Path

import numpy as np
import pytest

import quantumbridge as qb
from quantumbridge.qml import QNode

tf = pytest.importorskip("tensorflow")
ORACLE = json.loads((Path(__file__).parents[1] / "information/data/native_mixed_power_oracles.json").read_text())


@pytest.mark.parametrize("width", [2, 4])
@pytest.mark.parametrize("mode", ["for", "rof", "tape_tape"])
@pytest.mark.parametrize("loss_kind", ["square", "exponential_cubic"])
def test_real_low_qubit_qnode_moving_power_mixed_ad(width, mode, loss_kind):
    p, q = qb.Parameter("p"), qb.Parameter("q")
    body = qb.Circuit(1).rx(p, 0).rz(q, 0)
    source = qb.QuantumCircuit(width)
    source.append(body.to_gate().power(0.5, annotated=True), (width-1,))
    node = QNode.from_circuit(source, qb.PauliZ(width-1), interface="tensorflow", max_diff=2, diff_method="adjoint")
    before = source.to_ir().to_json()
    identities = tuple(parameter.uuid for parameter in source.parameters)
    frame = source.data[0].operation
    case = ORACLE["su2"][0]
    gradient, hessian = np.asarray(case["gradient"]), np.asarray(case["hessian"])
    value = case["value"]
    first, second = ((2*(value-0.3), 2.) if loss_kind == "square"
        else (np.exp(value)+0.6*value**2, np.exp(value)+1.2*value))
    direction = np.asarray([0.4, -0.3])
    expected = (first*hessian+second*np.outer(gradient, gradient)) @ direction

    @tf.function(autograph=False, jit_compile=False)
    def execute(point):
        d = tf.constant(direction, tf.float64)
        def loss():
            result = node(point)
            return (result-0.3)**2 if loss_kind == "square" else tf.exp(result)+0.2*result**3
        if mode == "for":
            with tf.autodiff.ForwardAccumulator(point, d) as forward:
                with tf.GradientTape() as reverse:
                    reverse.watch(point)
                    result = loss()
                derivative = reverse.gradient(result, point)
            return forward.jvp(derivative)
        if mode == "rof":
            with tf.GradientTape() as reverse:
                reverse.watch(point)
                with tf.autodiff.ForwardAccumulator(point, d) as forward:
                    result = loss()
                derivative = forward.jvp(result)
            return reverse.gradient(derivative, point)
        with tf.GradientTape() as outer:
            outer.watch(point)
            with tf.GradientTape() as inner:
                inner.watch(point)
                result = loss()
            derivative = inner.gradient(result, point)
            contraction = tf.reduce_sum(derivative*d)
        return outer.gradient(contraction, point)

    try:
        actual = execute(tf.constant(ORACLE["point"], tf.float64))
        assert actual is not None
        np.testing.assert_allclose(actual, expected, atol=2e-9, rtol=0)
    finally:
        assert source.to_ir().to_json() == before
        assert tuple(parameter.uuid for parameter in source.parameters) == identities
        assert source.data[0].operation is frame
