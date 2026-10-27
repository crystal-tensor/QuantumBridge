# Copyright 2026 QuantumBridge Contributors. Apache-2.0.
"""Default public pfor Jacobians and nonlinear second order without callbacks."""

from dataclasses import replace

import numpy as np
import pytest

import quantumbridge as qb
from quantumbridge.diff import HigherOrderLimits
from quantumbridge.interfaces.native_host import NativeHostKernel
from quantumbridge.interfaces.tensorflow_autodiff import TensorFlowBridgeLimits
from quantumbridge.interfaces.tensorflow_whole_execution import select_tensorflow_eager_vjp
from quantumbridge.qml import QNode
from test_native_tf_eager_jacobian_reentry import assert_tf_policy_error, tf


def make_node(method="adjoint", outputs=2):
    def program(tape, point):
        tape.ry(point[0]**2+point[1], 0)
        z = tape.expval(qb.PauliZ(0))
        return (z, tape.expval(qb.PauliX(0))) if outputs == 2 else z
    return QNode(program, 1, interface="tensorflow", diff_method=method, max_diff=2)


def oracle(point, outputs):
    a, slope = point[0]**2+point[1], np.array([2*point[0], 1.])
    y = np.array([np.cos(a), np.sin(a)])[:outputs]
    j = np.array([-np.sin(a)*slope, np.cos(a)*slope])[:outputs]
    h = np.array([-np.cos(a)*np.outer(slope, slope)-np.sin(a)*np.diag([2., 0.]),
        -np.sin(a)*np.outer(slope, slope)+np.cos(a)*np.diag([2., 0.])])[:outputs]
    return y, j, h


@pytest.mark.parametrize("method", ["best", "adjoint", "parameter-shift"])
@pytest.mark.parametrize("outputs", [1, 2])
@pytest.mark.parametrize("loss", ["square", "exponential_cubic"])
def test_public_pfor_loss_hessian_contains_quantum_curvature(method, outputs, loss, monkeypatch):
    node = make_node(method, outputs)
    def forbidden(*a, **k):
        pytest.fail("Traced eager VJP called a host quantum kernel")
    for point in ([0.37, 0.82], [0.41, 0.91]):
        with monkeypatch.context() as patch:
            x = tf.constant(point, tf.float64)
            with tf.GradientTape(persistent=True) as outer:
                outer.watch(x)
                with tf.GradientTape(persistent=True) as inner:
                    inner.watch(x)
                    y = tf.stack(tf.nest.flatten(node(x)))
                    weights = tf.constant([0.7, -0.2][:outputs], tf.float64)
                    value = tf.reduce_sum(weights*((y-0.3)**2 if loss == "square" else tf.exp(y)+0.2*y**3))
                gradient = inner.gradient(value, x)
                patch.setattr(NativeHostKernel, "run", forbidden)
                patch.setattr(NativeHostKernel, "run_second", forbidden)
                jacobian = inner.jacobian(y, x, experimental_use_pfor=True)
            actual = outer.jacobian(gradient, x, experimental_use_pfor=True)
            expected_y, j, h = oracle(point, outputs)
            first = 2*(expected_y-0.3) if loss == "square" else np.exp(expected_y)+0.6*expected_y**2
            second = np.full(outputs, 2.) if loss == "square" else np.exp(expected_y)+1.2*expected_y
            expected = j.T @ np.diag(np.array([0.7, -0.2][:outputs])*second) @ j+np.einsum("o,oij->ij", np.array([0.7, -0.2][:outputs])*first, h)
            np.testing.assert_allclose(y, expected_y, atol=2e-12, rtol=0)
            expected_loss = np.sum(np.array([0.7, -0.2][:outputs])*((expected_y-0.3)**2 if loss == "square" else np.exp(expected_y)+0.2*expected_y**3))
            np.testing.assert_allclose(value, expected_loss, atol=2e-12, rtol=0)
            np.testing.assert_allclose(jacobian, j, atol=2e-11, rtol=0)
            np.testing.assert_allclose(actual, expected, atol=2e-10, rtol=0)
            assert np.linalg.norm(np.einsum("o,oij->ij", np.array([0.7, -0.2][:outputs])*first, h)) > 0.01


@pytest.mark.parametrize("method", ["adjoint", "parameter-shift"])
def test_actual_native_vjp_graph_has_no_callback_and_immutable_decision(method):
    node = make_node(method)
    source, recorder, program = node._construct((tf.constant([0.37, 0.82], tf.float64),), {}, prepare_only=True)
    kernel = NativeHostKernel(node, source, recorder, program, TensorFlowBridgeLimits(), interface="tensorflow")
    function, decision = select_tensorflow_eager_vjp(kernel)
    with pytest.raises(TypeError):
        decision["gradient_method"] = "backprop"
    graph = tf.function(function, input_signature=[tf.TensorSpec((kernel.size,), tf.float64),
        tf.TensorSpec((kernel.output_size,), tf.float64)], autograph=False).get_concrete_function().graph.as_graph_def()
    assert not any(n.op in {"PyFunc", "EagerPyFunc", "PyFuncStateless"} for n in list(graph.node)+[
        node for f in graph.library.function for node in f.node_def])
    assert decision["gradient_method"] == method
    assert decision["resource_accounting"] == "OUT_OF_SCOPE"


@pytest.mark.parametrize("method", ["adjoint", "parameter-shift"])
@pytest.mark.parametrize("field", ["max_memory_bytes", "max_adjoint_operations", "max_total_tapes"])
def test_static_native_pfor_budget_refuses_before_tensor_math(method, field, monkeypatch):
    node = make_node(method)
    source, recorder, program = node._construct((tf.constant([0.37, 0.82], tf.float64),), {}, prepare_only=True)
    kernel = NativeHostKernel(node, source, recorder, program, TensorFlowBridgeLimits(), interface="tensorflow")
    _, work = select_tensorflow_eager_vjp(kernel)
    amount = work[{"max_memory_bytes": "workspace_bytes", "max_adjoint_operations": "planned_work", "max_total_tapes": "logical_evaluations"}[field]]
    kernel.node.higher_order_limits = replace(HigherOrderLimits(), **{field: amount-1})
    from quantumbridge.interfaces.tensorflow_whole_execution import TensorFlowStatevectorPlan
    monkeypatch.setattr(TensorFlowStatevectorPlan, "values", lambda *a, **k: pytest.fail("Rejected native plan emitted math"))
    with pytest.raises(MemoryError, match=field):
        select_tensorflow_eager_vjp(kernel)


@pytest.mark.parametrize("attribute,value", [("diff_method", "parameter-shift"), ("max_diff", 1)])
def test_live_forward_owner_change_refuses_new_traced_differentiation(attribute, value):
    node, x = make_node(), tf.constant([0.37, 0.82], tf.float64)
    with tf.GradientTape() as reverse:
        reverse.watch(x)
        y = tf.stack(node(x))
    setattr(node, attribute, value)
    with pytest.raises(Exception, match="owner configuration") as failure:
        reverse.jacobian(y, x)
    assert_tf_policy_error(failure.value, "tensorflow_compiled_owner_changed")


def test_genuine_pfor_third_point_does_not_return_a_finite_answer():
    node, x = make_node(), tf.constant([0.37, 0.82], tf.float64)
    with tf.GradientTape(persistent=True) as third:
        third.watch(x)
        with tf.GradientTape(persistent=True) as second:
            second.watch(x)
            with tf.GradientTape() as first:
                first.watch(x)
                y = tf.stack(node(x))
            jacobian = first.jacobian(y, x)
        hessians = second.jacobian(jacobian, x)
    np.testing.assert_allclose(hessians, oracle([0.37, 0.82], 2)[2], atol=2e-10, rtol=0)
    with pytest.raises(Exception, match="third-point") as failure:
        third.jacobian(hessians, x)
    assert_tf_policy_error(failure.value, "higher_order_derivatives")


@pytest.mark.parametrize("method", ["best", "adjoint", "parameter-shift"])
def test_actual_loss_gradient_allows_second_recording_but_refuses_third(method):
    node, point = make_node(method), tf.constant([0.37, 0.82], tf.float64)
    with tf.GradientTape() as third:
        third.watch(point)
        with tf.GradientTape() as second:
            second.watch(point)
            with tf.GradientTape() as first:
                first.watch(point)
                loss = tf.reduce_sum(tf.exp(tf.stack(node(point))))
            gradient = first.gradient(loss, point)
        hessian = second.jacobian(gradient, point)
    value, j, h = oracle([0.37, 0.82], 2)
    expected = j.T @ np.diag(np.exp(value)) @ j+np.einsum("o,oij->ij", np.exp(value), h)
    np.testing.assert_allclose(hessian, expected, atol=2e-10, rtol=0)
    with pytest.raises(Exception, match="third") as failure:
        third.jacobian(hessian, point)
    assert_tf_policy_error(failure.value, "higher_order_derivatives")


@pytest.mark.parametrize("case", ["ordinary_rotation", "generic_gate", "controlled_gate", "fixed_projector", "multi_output"])
@pytest.mark.parametrize("method", ["best", "adjoint", "parameter-shift"])
def test_default_gate_families_keep_pfor_quantum_hessians(case, method, monkeypatch):
    from test_native_tf_default_capability_selection import source_node
    node, point, expected, expected_jacobian = source_node(case, method)
    x = tf.constant(point, tf.float64)
    def forbidden(*args, **kwargs):
        pytest.fail("Traced gate-family derivative returned to the host quantum kernel")
    with tf.GradientTape() as outer:
        outer.watch(x)
        with tf.GradientTape() as inner:
            inner.watch(x)
            y = tf.reshape(tf.stack(tf.nest.flatten(node(x))), (-1,))
        monkeypatch.setattr(NativeHostKernel, "run", forbidden)
        monkeypatch.setattr(NativeHostKernel, "run_second", forbidden)
        jacobian = inner.jacobian(y, x)
    hessians = outer.jacobian(jacobian, x)
    np.testing.assert_allclose(jacobian, expected_jacobian, atol=2e-11, rtol=0)
    np.testing.assert_allclose(hessians, -(0.25**2 if case == "fixed_projector" else 1.)*expected,
        atol=2e-10, rtol=0)


@pytest.mark.parametrize("method", ["best", "adjoint", "parameter-shift"])
@pytest.mark.parametrize("loss", ["square", "exponential_cubic"])
@pytest.mark.parametrize("direction", [[0.4, -0.3], [-0.1, 0.8]])
def test_pfor_directional_loss_product_never_materializes_input_hessian(method, loss, direction, monkeypatch):
    node = make_node(method)
    node.higher_order_limits = HigherOrderLimits(max_hessian_elements=1)
    point, weights = tf.constant([0.37, 0.82], tf.float64), tf.constant([0.7, -0.2], tf.float64)
    with tf.GradientTape() as outer:
        outer.watch(point)
        with tf.GradientTape() as inner:
            inner.watch(point)
            y = tf.stack(node(point))
        jacobian = inner.jacobian(y, point)
        slopes = 2*(y-0.3) if loss == "square" else tf.exp(y)+0.6*y*y
        gradient = tf.linalg.matvec(jacobian, weights*slopes, transpose_a=True)
    def forbidden(*args, **kwargs):
        pytest.fail("A native directional product requested a full input Hessian or host second kernel")
    monkeypatch.setattr(QNode, "compute_hessian", forbidden)
    monkeypatch.setattr(tf.GradientTape, "jacobian", forbidden)
    monkeypatch.setattr(NativeHostKernel, "run_second", forbidden)
    actual = outer.gradient(gradient, point, output_gradients=tf.constant(direction, tf.float64))
    value, j, h = oracle([0.37, 0.82], 2)
    first = 2*(value-0.3) if loss == "square" else np.exp(value)+0.6*value**2
    second = np.full(2, 2.) if loss == "square" else np.exp(value)+1.2*value
    expected = j.T @ (np.array([0.7, -0.2])*second*(j @ direction))+np.einsum("o,oij,j->i", np.array([0.7, -0.2])*first, h, direction)
    np.testing.assert_allclose(actual, expected, atol=2e-10, rtol=0)
