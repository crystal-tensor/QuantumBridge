# Copyright 2026 QuantumBridge Contributors. Apache-2.0.
"""Actual public unitary entry retains the existing TF exact MPS execution."""

import numpy as np
import pytest

import quantumbridge as qb
from quantumbridge.diff import HigherOrderLimits
from quantumbridge.interfaces.tensorflow_mps_execution import TensorFlowMPSPlan
from quantumbridge.qml import QNode
from quantumbridge.utils.math import gate_matrix
from test_native_tf_mps_tensor_chain import no_dense_or_host, POINT, tf


def public_node(width, local_width, interface="numpy"):
    p, q = qb.ParameterVector("public_mps", 2)
    body = qb.Circuit(1).rx(p, 0).rz(q, 0)
    body.global_phase = .04 * p * q
    source = qb.QuantumCircuit(width)
    source.h(0)
    source.append(body.to_gate().power(.5, annotated=True), [width - 1])
    matrix = (gate_matrix("sx") @ gate_matrix("rz", (.29,)) * np.exp(.13j)
        if local_width == 1 else gate_matrix("ecr") @ gate_matrix("swap") * np.exp(-.07j))
    source.unitary(matrix, [0] if local_width == 1 else [width - 1, 0], label="public-tensor")
    source.cx(0, width - 1)
    source.ry(.4 * p, 0)
    source.global_phase = .17 + .03 * p * q
    base = QNode.from_circuit(source, qb.PauliZ(width - 1), max_diff=2)

    def program(tape, point):
        first = base.fn(tape, point)
        return first, tape.expval(qb.PauliX(0).tensor(qb.PauliX(width - 1)))

    return source, QNode(program, width, interface=interface, max_diff=2,
        device=qb.MatrixProductStateDevice(max_bond_dim=16, cutoff=0),
        higher_order_limits=HigherOrderLimits(max_memory_bytes=512 * 1024**2,
            max_adjoint_operations=1_000_000_000))


@pytest.mark.parametrize("width", [2, 4, 6])
@pytest.mark.parametrize("local_width", [1, 2])
def test_public_unitary_entry_full_tf_value_j_h(width, local_width, monkeypatch):
    source, native = public_node(width, local_width)
    dense = QNode(native.fn, width, max_diff=2, device=qb.StatevectorDevice())
    expected = (np.array(dense(POINT)), np.array(dense.jacobian(POINT)), np.array(dense.hessian(POINT)))
    _, node = public_node(width, local_width, "tensorflow")
    before = source.to_ir().to_json()
    no_dense_or_host(monkeypatch)
    point = tf.constant(POINT)
    with tf.GradientTape(persistent=True) as second:
        second.watch(point)
        with tf.GradientTape(persistent=True) as first:
            first.watch(point)
            value = tf.stack(node(point))
        jacobian = first.jacobian(value, point, experimental_use_pfor=False)
    hessian = second.jacobian(jacobian, point, experimental_use_pfor=False)
    for result, reference in zip((value, jacobian, hessian), expected):
        np.testing.assert_allclose(result, reference, atol=2e-9, rtol=0)
    assert node.last_metadata["native_tensor_execution"]
    assert source.to_ir().to_json() == before


@pytest.mark.parametrize("width", [20, 100])
def test_public_unitary_large_physical_chain_mixed_ad_and_streams(width, monkeypatch, record_property):
    _, small = public_node(2, 2)
    dense = QNode(small.fn, 2, max_diff=2, device=qb.StatevectorDevice())
    y, j, h = np.array(dense(POINT)), np.array(dense.jacobian(POINT)), np.array(dense.hessian(POINT))
    _, node = public_node(width, 2, "tensorflow")
    node.higher_order_limits = HigherOrderLimits(max_hessian_elements=1,
        max_memory_bytes=512 * 1024**2, max_adjoint_operations=1_000_000_000)
    plan = node._construct((POINT,), {})
    tensors = TensorFlowMPSPlan(plan)
    no_dense_or_host(monkeypatch)
    monkeypatch.setattr(tf.GradientTape, "jacobian",
        lambda *args, **kwargs: pytest.fail("A public-entry streamed HVP built a Hessian"))
    chain, _ = tensors.chain(tf.constant(plan.recorder.native_values(), tf.float64))
    assert len(chain) == width
    record_property("physical_tensors", len(chain))
    record_property("observed_representation_bond", max(site.shape[-1] for site in chain))

    @tf.function(autograph=False)
    def graph(point, direction, weights, loss_weights):
        def loss(value):
            return tf.reduce_sum(weights * (loss_weights[0] * (value - .3)**2
                + loss_weights[1] * (tf.exp(value) + .2 * value**3)))
        with tf.autodiff.ForwardAccumulator(point, direction) as forward:
            with tf.GradientTape() as reverse:
                reverse.watch(point)
                value = tf.stack(node(point))
                total = loss(value)
            gradient = reverse.gradient(total, point)
        for_hvp = forward.jvp(gradient)
        with tf.GradientTape() as reverse:
            reverse.watch(point)
            with tf.autodiff.ForwardAccumulator(point, direction) as forward:
                value = tf.stack(node(point))
                total = loss(value)
            tangent = forward.jvp(total)
        return value, forward.jvp(value), for_hvp, reverse.gradient(tangent, point)

    weights = np.array([.7, -.2])
    for loss_weights in np.eye(2):
        first = loss_weights[0] * 2 * (y - .3) + loss_weights[1] * (np.exp(y) + .6 * y*y)
        second = loss_weights[0] * 2 + loss_weights[1] * (np.exp(y) + 1.2 * y)
        for direction in (np.array([.4, -.3]), np.array([-.1, .8]), np.zeros(2)):
            hvp = j.T @ (weights * second * (j @ direction)) + np.einsum("i,ijk,k->j", weights * first, h, direction)
            results = graph(tf.constant(POINT), tf.constant(direction), tf.constant(weights), tf.constant(loss_weights))
            for actual, expected in zip(results, (y, j @ direction, hvp, hvp)):
                assert actual is not None
                np.testing.assert_allclose(actual, expected, atol=3e-9, rtol=0)
    assert graph.experimental_get_tracing_count() == 1
    assert node.last_metadata["native_tensor_execution"]
