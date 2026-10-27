# Copyright 2026 QuantumBridge Contributors. Apache-2.0.
"""Real frozen native plans, not an independent hardcoded quantum circuit."""

import numpy as np
import pytest
import json
from pathlib import Path

import quantumbridge as qb
from quantumbridge.qml import QNode

from test_native_tf_managed_cached_execution import CASE, make_node, tf

POINTS = json.loads((Path(__file__).parents[1]/"information/data/tf_inline_qnode_oracles.json").read_text())["cases"]


def inline_node(**options):
    node, source = make_node(**options)
    handle = node.compile_tensorflow_inline(parameters=tuple(source.parameters),
        input_signature=[tf.TensorSpec((2,), tf.float64)])
    return node, source, handle


def forbid_rebuild(monkeypatch):
    import quantumbridge.diff.compiled_parameters as compiled
    import quantumbridge.interfaces.tensorflow_native_execution as local
    import quantumbridge.interfaces.tensorflow_whole_execution as whole
    from test_native_tf_managed_cached_execution import forbid_quantum_hosts
    forbid_quantum_hosts(monkeypatch)
    def refuse(*args, **kwargs):
        pytest.fail("Frozen inline execution rebuilt/copied a quantum plan or invoked a cached scalar mapper")
    monkeypatch.setattr(QNode, "_construct", refuse)
    monkeypatch.setattr(compiled, "record_compiled_parameters", refuse)
    monkeypatch.setattr(local, "record_compiled_parameters", refuse)
    monkeypatch.setattr(whole, "record_compiled_parameters", refuse)
    monkeypatch.setattr(qb.Circuit, "copy", refuse)
    monkeypatch.setattr(qb.Circuit, "lowered", refuse)
    monkeypatch.setattr(qb.Circuit, "assign_parameters", refuse)
    import quantumbridge.core.circuit_metadata as metadata
    monkeypatch.setattr(metadata, "execution_copy", refuse)


@pytest.mark.parametrize("traced", [False, True])
@pytest.mark.parametrize("mode", ["for", "rof", "tape"])
@pytest.mark.parametrize("loss_kind", ["square", "exponential_cubic"])
def test_real_native_inline_mixed_loss_has_independent_chain_rule(traced, mode, loss_kind, monkeypatch):
    node, source, handle = inline_node()
    before = source.to_ir().to_json()
    forbid_rebuild(monkeypatch)
    direction = tf.constant([0.4, -0.3], tf.float64)
    weights = tf.constant([0.7, -0.2], tf.float64)
    def evaluate(point):
        def loss():
            y = tf.stack(handle(point))
            return tf.reduce_sum(weights*((y-0.3)**2 if loss_kind == "square" else tf.exp(y)+0.2*y**3))
        if mode == "for":
            with tf.autodiff.ForwardAccumulator(point, direction) as fw:
                with tf.GradientTape() as reverse:
                    reverse.watch(point)
                    loss_value = loss()
                gradient = reverse.gradient(loss_value, point)
            return fw.jvp(gradient)
        if mode == "rof":
            with tf.GradientTape() as reverse:
                reverse.watch(point)
                with tf.autodiff.ForwardAccumulator(point, direction) as fw:
                    loss_value = loss()
                tangent = fw.jvp(loss_value)
            return reverse.gradient(tangent, point)
        with tf.GradientTape() as outer:
            outer.watch(point)
            with tf.GradientTape() as inner:
                inner.watch(point)
                loss_value = loss()
            gradient = inner.gradient(loss_value, point)
            projected = tf.reduce_sum(gradient*direction)
        return outer.gradient(projected, point)
    function = tf.function(evaluate, input_signature=[tf.TensorSpec((2,), tf.float64)], autograph=False, jit_compile=False) if traced else evaluate
    for case in (*POINTS, POINTS[0]):
        y, j, h = np.array(case["outputs"]), np.array(case["jacobian"]), np.array(case["hessians"])
        first, second = (2*(y-0.3), np.full(2, 2.)) if loss_kind == "square" else (np.exp(y)+0.6*y*y, np.exp(y)+1.2*y)
        expected = j.T @ (np.array([0.7, -0.2])*second*(j @ [0.4, -0.3]))+np.einsum("o,oij,j->i", np.array([0.7, -0.2])*first, h, [0.4, -0.3])
        result = function(tf.constant(case["point"], tf.float64))
        assert result is not None
        np.testing.assert_allclose(result, expected, atol=2e-9, rtol=0)
    if traced:
        assert function.experimental_get_tracing_count() == 1
        names = [f.signature.name for f in function.get_concrete_function().graph.as_graph_def().library.function]
        assert not any("prepare" in name or "inner_model" in name for name in names)
    assert source.to_ir().to_json() == before
    assert node.max_diff == 2


@pytest.mark.parametrize("traced", [False, True])
def test_complete_complex_state_and_real_imag_jets_are_native_frozen_math(traced, monkeypatch):
    node, _, handle = inline_node()
    forbid_rebuild(monkeypatch)
    def evaluate(point):
        with tf.GradientTape(persistent=True) as outer:
            outer.watch(point)
            with tf.GradientTape(persistent=True) as inner:
                inner.watch(point)
                state = handle.state(point)
                parts = tf.concat([tf.math.real(state), tf.math.imag(state)], 0)
            jacobian = inner.jacobian(parts, point, experimental_use_pfor=False)
        return state, jacobian, outer.jacobian(jacobian, point, experimental_use_pfor=False)
    function = tf.function(evaluate, input_signature=[tf.TensorSpec((2,), tf.float64)], autograph=False, jit_compile=False) if traced else evaluate
    for case in POINTS:
        state, jacobian, hessian = function(tf.constant(case["point"], tf.float64))
        raw = np.array(case["state"])[:, 0]
        np.testing.assert_allclose(state, raw[:, 0]+1j*raw[:, 1], atol=3e-12, rtol=0)
        np.testing.assert_allclose(jacobian, case["state_jacobian"], atol=5e-10, rtol=0)
        np.testing.assert_allclose(hessian, case["state_hessians"], atol=8e-10, rtol=0)
    assert node.max_diff == 2


def test_jvp_vjp_and_mixed_output_hessians_use_independent_native_oracles(monkeypatch):
    node, _, handle = inline_node()
    forbid_rebuild(monkeypatch)
    point = tf.constant(CASE["point"], tf.float64)
    with tf.GradientTape(persistent=True) as outer:
        outer.watch(point)
        with tf.GradientTape(persistent=True) as inner:
            inner.watch(point)
            with tf.autodiff.ForwardAccumulator(point, tf.constant([0.4, -0.3], tf.float64)) as forward:
                value = tf.stack(handle(point))
        jacobian = inner.jacobian(value, point, experimental_use_pfor=False)
        vjp = inner.gradient(value, point, output_gradients=tf.constant([0.7, -0.2], tf.float64))
    np.testing.assert_allclose(jacobian, CASE["jacobian"], atol=5e-10, rtol=0)
    np.testing.assert_allclose(forward.jvp(value), np.array(CASE["jacobian"]) @ [0.4, -0.3], atol=5e-10, rtol=0)
    np.testing.assert_allclose(vjp, np.array(CASE["jacobian"]).T @ [0.7, -0.2], atol=5e-10, rtol=0)
    np.testing.assert_allclose(outer.jacobian(jacobian, point, experimental_use_pfor=False), CASE["hessians"], atol=2e-9, rtol=0)
    assert node.max_diff == 2


def test_entangling_compiler_and_format_lineage_preserves_global_phase_and_frozen_plan(monkeypatch):
    from quantumbridge.diff import HigherOrderLimits
    from quantumbridge.execution.resource_limits import UnifiedExecutionLimits
    from test_native_tf_whole_qnode_execution import CASES, node_for, restore, source_and_observables
    case = next(c for c in CASES if c["name"] == "full_entangling")
    source, observables = source_and_observables(case)
    owners, handles = [], []
    for transport in (None, "ir", "qpy"):
        restored = restore(source, transport)
        node = node_for(restored, observables).compile(optimization_level=0,
            basis_gates=("rx", "ry", "rz", "sx", "phase", "cx", "crx", "native_matrix_power"))
        node.higher_order_limits = HigherOrderLimits(max_adjoint_operations=1_000_000_000)
        node.unified_limits = UnifiedExecutionLimits(max_derivative_work=1_000_000_000)
        owners.append(node)
        handles.append(node.compile_tensorflow_inline(parameters=tuple(restored.parameters),
            input_signature=[tf.TensorSpec((2,), tf.float64)]))
    forbid_rebuild(monkeypatch)
    raw = np.array(case["state"])[:, 0]
    for index, handle in enumerate(handles):
        point = tf.constant(case["point"], tf.float64)
        with tf.GradientTape(persistent=True) as outer:
            outer.watch(point)
            with tf.GradientTape(persistent=True) as reverse:
                reverse.watch(point)
                state = handle.state(point)
                parts = tf.concat([tf.math.real(state), tf.math.imag(state)], 0)
            jacobian = reverse.jacobian(parts, point, experimental_use_pfor=False)
        np.testing.assert_allclose(state, raw[:, 0]+1j*raw[:, 1], atol=3e-12, rtol=0)
        np.testing.assert_allclose(jacobian, case["state_jacobian"], atol=5e-10, rtol=0)
        if index == 0:
            np.testing.assert_allclose(outer.jacobian(jacobian, point, experimental_use_pfor=False), case["state_hessians"], atol=8e-10, rtol=0)
        np.testing.assert_allclose(handle(point), case["outputs"], atol=3e-12, rtol=0)
    assert len(owners) == 3


def test_eight_parameter_streamed_hvp_does_not_use_a_full_hessian(monkeypatch):
    from quantumbridge.diff import HigherOrderLimits
    from quantumbridge.execution.resource_limits import UnifiedExecutionLimits
    data = json.loads((Path(__file__).parents[1]/"information/data/native_mps_power_oracles.json").read_text())["eight"]
    parameters = qb.ParameterVector("theta", 8)
    source = qb.QuantumCircuit(1)
    for index in range(0, 8, 2):
        source.append(qb.Circuit(1).rx(parameters[index], 0).rz(parameters[index+1], 0).to_gate().power(0.5, annotated=True), (0,))
    node = QNode.from_circuit(source, qb.PauliZ(0), interface="tensorflow", diff_method="adjoint", max_diff=2,
        higher_order_limits=HigherOrderLimits(max_hessian_elements=1, max_adjoint_operations=1_000_000_000),
        unified_limits=UnifiedExecutionLimits(max_derivative_work=1_000_000_000))
    handle = node.compile_tensorflow_inline(parameters=tuple(parameters), input_signature=[tf.TensorSpec((8,), tf.float64)])
    forbid_rebuild(monkeypatch)
    def failed(*a, **k):
        pytest.fail("A directional inline HVP requested a complete Hessian/Jacobian")
    monkeypatch.setattr(tf.GradientTape, "jacobian", failed)
    monkeypatch.setattr(QNode, "compute_hessian", failed)
    point = tf.constant(data["point"], tf.float64)
    with tf.autodiff.ForwardAccumulator(point, tf.constant(data["direction"], tf.float64)) as fw:
        with tf.GradientTape() as reverse:
            reverse.watch(point)
            value = handle(point)
        first = reverse.gradient(value, point)
    np.testing.assert_allclose(value, data["value"], atol=3e-12, rtol=0)
    np.testing.assert_allclose(fw.jvp(first), data["hvp"], atol=2e-9, rtol=0)


def test_native_unary_ast_and_phase_keep_live_tf_scalar_dependencies(monkeypatch):
    p, q = qb.ParameterVector("angles", 2)
    source = qb.Circuit(1).ry(p.sin()+q.exp(), 0)
    source.global_phase = 0.17*p*q
    node = QNode.from_circuit(source, qb.PauliZ(0), interface="tensorflow", diff_method="adjoint", max_diff=2)
    handle = node.compile_tensorflow_inline(parameters=(p, q), input_signature=[tf.TensorSpec((2,), tf.float64)])
    forbid_rebuild(monkeypatch)
    point = tf.constant([0.37, 0.82], tf.float64)
    with tf.GradientTape() as reverse:
        reverse.watch(point)
        value = handle(point)
    angle = np.sin(0.37)+np.exp(0.82)
    np.testing.assert_allclose(value, np.cos(angle), atol=1e-12, rtol=0)
    np.testing.assert_allclose(reverse.gradient(value, point), -np.sin(angle)*np.array([np.cos(0.37), np.exp(0.82)]), atol=1e-12, rtol=0)
