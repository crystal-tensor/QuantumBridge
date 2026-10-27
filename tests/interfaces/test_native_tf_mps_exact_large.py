# Copyright 2026 QuantumBridge Contributors. Apache-2.0.
"""Actual large physical chains; independent two-active-wire mathematical oracle."""

import numpy as np
import pytest

import quantumbridge as qb
from quantumbridge.diff import HigherOrderLimits
from quantumbridge.interfaces.tensorflow_mps_execution import TensorFlowMPSPlan
from quantumbridge.qml import QNode
from test_native_tf_mps_exact_closure import fixture, POINT, tf
from test_native_tf_mps_tensor_chain import no_dense_or_host


@pytest.mark.parametrize("width", [20, 100])
def test_remote_fixed_matrix_large_chain_matches_full_local_jets(width, monkeypatch, record_property):
    source_small, small = fixture(2, 2)
    dense = QNode(small.fn, 2, max_diff=2, device=qb.StatevectorDevice())
    y, j, h = np.array(dense(POINT)), np.array(dense.jacobian(POINT)), np.array(dense.hessian(POINT))
    expected_state = qb.StatevectorDevice().statevector(source_small,
        dict(zip(source_small.parameters, POINT)))
    source, node = fixture(width, 2, interface="tensorflow")
    node.higher_order_limits = HigherOrderLimits(max_hessian_elements=1,
        max_adjoint_operations=1_000_000_000, max_memory_bytes=512*1024**2)
    plan = node._construct((POINT,), {})
    tensor_plan = TensorFlowMPSPlan(plan)
    no_dense_or_host(monkeypatch)
    monkeypatch.setattr(tf.GradientTape, "jacobian", lambda *a, **k: pytest.fail("A large MPS stream materialized a Hessian"))
    chain, scale = tensor_plan.chain(tf.constant(plan.recorder.native_values()))
    assert len(chain) == width and all(t.shape[1] == 2 for t in chain)
    observed = max(t.shape[2] for t in chain)
    record_property("observed_representation_bond", observed)
    record_property("predicted_bond_bound", tensor_plan.work["mps_bond_bound"])
    record_property("routing_steps", tensor_plan.work["mps_routed_two_site_steps"])
    assert observed <= tensor_plan.work["mps_bond_bound"] <= 16
    # Project only the known inactive vacuum, retaining just two physical axes.
    # The largest exposed physical output is four amplitudes, not 2**width.
    active = chain[0]
    for site in chain[1:-1]:
        active = tf.tensordot(active, site[:, 0, :], axes=([-1], [0]))
    active = tf.tensordot(active, chain[-1], axes=([-1], [0]))
    np.testing.assert_allclose(tf.reshape(active, (4,))*scale, expected_state, atol=2e-11, rtol=0)
    probability = tf.ones((1, 1), tf.complex128)
    for wire, site in enumerate(chain):
        projector = tf.eye(2, dtype=tf.complex128) if wire in {0, width-1} else tf.constant([[1., 0.], [0., 0.]], tf.complex128)
        probability = tf.einsum("ab,air,ij,bjs->rs", probability, tf.math.conj(site), projector, site)
    np.testing.assert_allclose(tf.math.real(probability[0, 0]*tf.math.conj(scale)*scale), 1., atol=2e-11, rtol=0)
    @tf.function(autograph=False)
    def graph(point, direction, cotangent, loss_weights):
        def loss(value):
            terms = (loss_weights[0]*value+loss_weights[1]*(value-.3)**2
                +loss_weights[2]*(tf.exp(value)+.2*value**3))
            return tf.reduce_sum(cotangent*terms)
        with tf.autodiff.ForwardAccumulator(point, direction) as forward:
            with tf.GradientTape() as reverse:
                reverse.watch(point)
                value = tf.stack(node(point))
                selected_loss = loss(value)
            vjp = reverse.gradient(selected_loss, point)
        for_value = forward.jvp(vjp)
        with tf.GradientTape() as reverse:
            reverse.watch(point)
            with tf.autodiff.ForwardAccumulator(point, direction) as forward:
                value = tf.stack(node(point))
                selected_loss = loss(value)
            jvp = forward.jvp(value)
            weighted = forward.jvp(selected_loss)
        return value, vjp, jvp, for_value, reverse.gradient(weighted, point)
    for loss_weights in np.eye(3):
        cotangents = (np.array([.7, -.2]), np.array([1., 0.]), np.array([0., 1.])) if loss_weights[0] else (np.array([.7, -.2]),)
        first = loss_weights[0]+2*loss_weights[1]*(y-.3)+loss_weights[2]*(np.exp(y)+.6*y*y)
        second = 2*loss_weights[1]+loss_weights[2]*(np.exp(y)+1.2*y)
        for direction in (np.array([.4, -.3]), np.array([-.1, .8]), np.zeros(2)):
            for cotangent in cotangents:
                actual = graph(tf.constant(POINT), tf.constant(direction), tf.constant(cotangent), tf.constant(loss_weights))
                hvp = j.T @ (cotangent*second*(j @ direction))+np.einsum("i,ijk,k->j", cotangent*first, h, direction)
                expected = (y, j.T @ (cotangent*first), j @ direction, hvp, hvp)
                for result, reference in zip(actual, expected):
                    assert result is not None
                    np.testing.assert_allclose(result, reference, atol=3e-9, rtol=0)
    assert graph.experimental_get_tracing_count() == 1
    assert node.last_metadata["tensor_plan_work"]["physical_tensor_count"] == width
    assert source.num_qubits == width
