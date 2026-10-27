# Copyright 2026 QuantumBridge Contributors. Apache-2.0.
"""Public whole-QNode tensor execution, with unchanged independent oracles."""

import json
from pathlib import Path

import numpy as np
import pytest

import quantumbridge as qb
from quantumbridge.qml import QNode

tf = pytest.importorskip("tensorflow")
CASES = json.loads((Path(__file__).parents[1] / "information/data/tf_native_tensor_execution_oracles.json").read_text())["cases"]
CASES = [case for case in CASES if case["name"] in {"requested0.5", "controlled0", "controlled1"}]


def build(case, width=4, max_diff=2):
    p, q = qb.ParameterVector("angles", 2)
    body = qb.Circuit(1).rx(p, 0).rz(q*q+0.4, 0).ry(-p, 0)
    body.global_phase = case["phase_offset"]+case["phase_scale"]*p*q
    gate = body.to_gate().power(case["power"], annotated=True)
    source = qb.QuantumCircuit(width)
    target = width-1
    if case.get("control") is not None:
        source.h(0)
        source.append(gate.control(ctrl_state=case["control"]), (0, target))
        other = qb.PauliX(0)
    else:
        source.append(gate, (target,))
        other = qb.PauliX(target)
    base = QNode.from_circuit(source, qb.PauliZ(target), max_diff=max_diff, interface="tensorflow", diff_method="adjoint")
    builder = base.fn
    def program(tape, point):
        first = builder(tape, point)
        return first, tape.expval(other)
    node = QNode(program, width, max_diff=max_diff, interface="tensorflow", diff_method="adjoint")
    return source, node


def no_host(monkeypatch):
    from quantumbridge.interfaces.native_host import NativeHostKernel
    from quantumbridge.interfaces.tensorflow_graph import TensorFlowGraphKernel
    def forbidden(*args, **kwargs):
        pytest.fail("A supported whole-QNode tensor graph used a host quantum callback or dense Gate")
    monkeypatch.setattr(NativeHostKernel, "run", forbidden)
    monkeypatch.setattr(NativeHostKernel, "run_second", forbidden)
    monkeypatch.setattr(TensorFlowGraphKernel, "evaluate", forbidden)
    monkeypatch.setattr(qb.StatevectorDevice, "statevector", forbidden)
    from quantumbridge.core.gates import Gate
    monkeypatch.setattr(Gate, "to_matrix", forbidden)
    monkeypatch.setattr(tf, "numpy_function", forbidden)
    monkeypatch.setattr(tf, "py_function", forbidden)


def assert_graph(function):
    graph = function.get_concrete_function(tf.TensorSpec((2,), tf.float64)).graph.as_graph_def()
    ops = {node.op for node in graph.node}
    ops.update(node.op for item in graph.library.function for node in item.node_def)
    assert not ops & {"PyFunc", "PyFuncStateless", "EagerPyFunc", "Eig", "MatrixLogarithm"}


@pytest.mark.parametrize("traced", [False, True])
@pytest.mark.parametrize("mode", ["for", "rof", "tape_tape"])
@pytest.mark.parametrize("loss_kind", ["square", "exponential_cubic"])
@pytest.mark.parametrize("case", CASES, ids=lambda case: case["name"])
def test_public_two_output_qnode_complete_mixed_chain_rule(case, mode, loss_kind, traced, monkeypatch):
    source, node = build(case)
    before = source.to_ir().to_json()
    no_host(monkeypatch)
    monkeypatch.setattr(tf.GradientTape, "jacobian", lambda *a, **k: pytest.fail("Streamed HVP materialized a full Hessian"))
    y, j, h = np.array(case["outputs"]), np.array(case["jacobian"]), np.array(case["hessians"])
    weights, direction = np.array([0.7, -0.2]), np.array([0.4, -0.3])
    first, second = (2*(y-0.3), np.full(2, 2.)) if loss_kind == "square" else (np.exp(y)+0.6*y*y, np.exp(y)+1.2*y)
    expected = j.T @ (weights*second*(j @ direction))+np.einsum("i,ijk,k->j", weights*first, h, direction)
    def execute(point):
        d = tf.constant(direction, tf.float64)
        def loss():
            y = tf.stack(node(point))
            terms = (y-0.3)**2 if loss_kind == "square" else tf.exp(y)+0.2*y**3
            return tf.reduce_sum(tf.constant(weights, tf.float64)*terms)
        if mode == "for":
            with tf.autodiff.ForwardAccumulator(point, d) as forward:
                with tf.GradientTape() as reverse:
                    reverse.watch(point)
                    value = loss()
                derivative = reverse.gradient(value, point)
            return forward.jvp(derivative)
        if mode == "rof":
            with tf.GradientTape() as reverse:
                reverse.watch(point)
                with tf.autodiff.ForwardAccumulator(point, d) as forward:
                    value = loss()
                derivative = forward.jvp(value)
            return reverse.gradient(derivative, point)
        with tf.GradientTape() as outer:
            outer.watch(point)
            with tf.GradientTape() as inner:
                inner.watch(point)
                value = loss()
            derivative = inner.gradient(value, point)
            contraction = tf.reduce_sum(derivative*d)
        return outer.gradient(contraction, point)
    fn = tf.function(execute, autograph=False, jit_compile=False) if traced else execute
    actual = fn(tf.constant(case["point"], tf.float64))
    assert actual is not None
    np.testing.assert_allclose(actual, expected, atol=2e-9, rtol=0)
    assert node.last_metadata["native_tensor_execution"]
    assert source.to_ir().to_json() == before
    if traced:
        assert_graph(fn)


@pytest.mark.parametrize("traced", [False, True])
def test_genuine_public_third_derivative_still_refuses(traced):
    _, node = build(CASES[0])
    def execute(point):
        with tf.GradientTape() as outer:
            outer.watch(point)
            with tf.GradientTape() as middle:
                middle.watch(point)
                with tf.GradientTape() as inner:
                    inner.watch(point)
                    value = tf.reduce_sum(tf.stack(node(point)))
                first = inner.gradient(value, point)
                first_sum = tf.reduce_sum(first)
            second = middle.gradient(first_sum, point)
            second_sum = tf.reduce_sum(second)
        return outer.gradient(second_sum, point)
    fn = tf.function(execute, autograph=False, jit_compile=False) if traced else execute
    from quantumbridge.core.classical import UnsupportedFeature
    with pytest.raises(UnsupportedFeature, match="third-point"):
        fn(tf.constant(CASES[0]["point"], tf.float64))


@pytest.mark.parametrize("traced", [False, True])
def test_public_whole_quantum_jacobian_hessian_jvp_vjp(traced, monkeypatch):
    case = CASES[0]
    _, node = build(case)
    no_host(monkeypatch)
    def execute(point):
        with tf.GradientTape(persistent=True) as outer:
            outer.watch(point)
            with tf.GradientTape(persistent=True) as inner:
                inner.watch(point)
                value = tf.stack(node(point))
            j = inner.jacobian(value, point, experimental_use_pfor=False)
        h = outer.jacobian(j, point, experimental_use_pfor=False)
        vjp = inner.gradient(value, point, output_gradients=tf.constant([0.7, -0.2], tf.float64))
        with tf.autodiff.ForwardAccumulator(point, tf.constant([0.4, -0.3], tf.float64)) as forward:
            raw = tf.stack(node(point))
        return value, j, h, vjp, forward.jvp(raw)
    fn = tf.function(execute, autograph=False, jit_compile=False) if traced else execute
    result = fn(tf.constant(case["point"], tf.float64))
    j = np.array(case["jacobian"])
    expected = (case["outputs"], j, case["hessians"], j.T @ [0.7, -0.2], j @ [0.4, -0.3])
    for actual, reference in zip(result, expected):
        assert actual is not None
        np.testing.assert_allclose(actual, reference, atol=2e-9, rtol=0)


@pytest.mark.parametrize("traced", [False, True])
def test_max_diff_one_retains_first_vjp_and_second_order_refusal(traced):
    case = CASES[0]
    _, node = build(case, max_diff=1)
    def first(point):
        with tf.GradientTape() as inner:
            inner.watch(point)
            value = tf.stack(node(point))
        return inner.gradient(value, point, output_gradients=tf.constant([0.7, -0.2], tf.float64))
    fn = tf.function(first, autograph=False, jit_compile=False) if traced else first
    point = tf.constant(case["point"], tf.float64)
    np.testing.assert_allclose(fn(point), np.array(case["jacobian"]).T @ [0.7, -0.2], atol=2e-9, rtol=0)
    from quantumbridge.core.classical import UnsupportedFeature
    def second(x):
        with tf.GradientTape() as outer:
            outer.watch(x)
            total = tf.reduce_sum(first(x))
        return outer.gradient(total, x)
    second_fn = tf.function(second, autograph=False, jit_compile=False) if traced else second
    with pytest.raises(UnsupportedFeature, match="max_diff=2"):
        second_fn(point)


@pytest.mark.parametrize("traced", [False, True])
def test_public_zero_direction_has_a_real_zero_hvp(traced, monkeypatch):
    _, node = build(CASES[0])
    no_host(monkeypatch)
    def execute(point):
        with tf.autodiff.ForwardAccumulator(point, tf.zeros_like(point)) as forward:
            with tf.GradientTape() as reverse:
                reverse.watch(point)
                value = tf.reduce_sum(tf.exp(tf.stack(node(point))))
            first = reverse.gradient(value, point)
        return forward.jvp(first)
    fn = tf.function(execute, autograph=False, jit_compile=False) if traced else execute
    actual = fn(tf.constant(CASES[0]["point"], tf.float64))
    assert actual is not None
    np.testing.assert_array_equal(actual, np.zeros(2))


@pytest.mark.parametrize("bad", ["nan", "cut"])
def test_public_cached_graph_checks_runtime_values_and_recovers(bad, monkeypatch):
    import math
    _, node = build(CASES[0])
    no_host(monkeypatch)
    fn = tf.function(node, input_signature=[tf.TensorSpec((2,), tf.float64)], autograph=False, jit_compile=False)
    good = tf.constant(CASES[0]["point"], tf.float64)
    first = tf.stack(fn(good))
    point = [float("nan"), 0.82] if bad == "nan" else [0., math.sqrt(2*math.pi-0.4)]
    with pytest.raises(tf.errors.InvalidArgumentError):
        fn(tf.constant(point, tf.float64))
    np.testing.assert_array_equal(tf.stack(fn(good)), first)
    assert fn.experimental_get_tracing_count() == 1


@pytest.mark.parametrize("method", ["best", "adjoint", "parameter-shift", "backprop"])
def test_method_selection_is_explicit_for_the_supported_moving_power_domain(method):
    _, node = build(CASES[0])
    node.diff_method = method
    point = tf.constant(CASES[0]["point"], tf.float64)
    if method in {"parameter-shift", "backprop"}:
        from quantumbridge.core.classical import UnsupportedFeature
        with pytest.raises(UnsupportedFeature):
            node(point)
    else:
        np.testing.assert_allclose(node(point), CASES[0]["outputs"], atol=3e-12, rtol=0)
        assert node.last_metadata["native_tensor_execution"]
        assert node.last_metadata["requested_gradient_method"] == method


@pytest.mark.parametrize("method", ["best", "parameter-shift"])
def test_ordinary_pauli_rotation_keeps_its_actual_existing_method_contract(method, monkeypatch):
    def program(tape, point):
        tape.ry(point, 0)
        return tape.expval(qb.PauliZ(0))
    point = tf.constant(0.3, tf.float64)
    from quantumbridge.interfaces import tensorflow_whole_execution
    def measured(node):
        with tf.GradientTape() as tape:
            tape.watch(point)
            value = node(point)
        return tape.gradient(value, point), dict(node.last_metadata)
    with monkeypatch.context() as patch:
        patch.setattr(tensorflow_whole_execution, "select_tensorflow_statevector", lambda *args: None)
        baseline = measured(QNode(program, 1, interface="tensorflow", max_diff=2, diff_method=method))
    node = QNode(program, 1, interface="tensorflow", max_diff=2, diff_method=method)
    derivative, metadata = measured(node)
    np.testing.assert_allclose(derivative, -np.sin(0.3), atol=1e-12, rtol=0)
    np.testing.assert_array_equal(derivative, baseline[0])
    assert metadata["gradient_method"] == baseline[1]["gradient_method"]
    if method == "parameter-shift":
        assert metadata["gradient_method"] == method
    assert not node.last_metadata.get("native_tensor_execution", False)


def test_managed_scope_is_not_silently_treated_as_an_admitted_tf_graph(monkeypatch):
    from quantumbridge.execution.resource_context import ResourceScope
    from quantumbridge.execution.resource_ledger import UnifiedResourceLedger
    from quantumbridge.core.classical import UnsupportedFeature
    _, node = build(CASES[0])
    point = tf.constant(CASES[0]["point"], tf.float64)
    no_host(monkeypatch)
    ledger = UnifiedResourceLedger()
    graph = tf.function(node, autograph=False, jit_compile=False)
    with ResourceScope(ledger), pytest.raises(UnsupportedFeature, match="shared request ledger"):
        graph(point)
    receipt = ledger.receipt()
    assert receipt["consumed_tapes"] == receipt["consumed_shots"] == receipt["consumed_derivative_work"] == 0


def test_trainable_observable_coefficients_keep_the_existing_complete_host_path(monkeypatch):
    from quantumbridge.interfaces import tensorflow_whole_execution
    source = qb.QuantumCircuit(1)
    source.append(qb.Circuit(1).ry(qb.Parameter("theta"), 0).to_gate().power(0.5, annotated=True), (0,))
    builder = QNode.from_circuit(source, qb.PauliZ(0)).fn
    def program(tape, point):
        builder(tape, point[:1])
        return tape.expval(qb.Hamiltonian([(point[1], qb.PauliZ(0))]))
    point = tf.constant([0.37, 0.82], tf.float64)
    def measured(node):
        with tf.GradientTape() as tape:
            tape.watch(point)
            value = node(point)
        return value, tape.gradient(value, point)
    with monkeypatch.context() as patch:
        patch.setattr(tensorflow_whole_execution, "select_tensorflow_statevector", lambda *args: None)
        baseline = measured(QNode(program, 1, interface="tensorflow", max_diff=2))
    node = QNode(program, 1, interface="tensorflow", max_diff=2)
    actual = measured(node)
    for value, reference in zip(actual, baseline):
        assert value is not None
        np.testing.assert_array_equal(value, reference)
    np.testing.assert_allclose(actual[0], 0.82*np.cos(0.37/2), atol=2e-12, rtol=0)
    np.testing.assert_allclose(actual[1], [-0.41*np.sin(0.37/2), np.cos(0.37/2)], atol=2e-12, rtol=0)
    assert not node.last_metadata.get("native_tensor_execution", False)


@pytest.mark.parametrize("traced", [False, True])
def test_nonfinite_observable_result_is_not_returned_as_a_supported_output(traced, monkeypatch):
    p, q = qb.Parameter("p"), qb.Parameter("q")
    source = qb.QuantumCircuit(1)
    source.append(qb.Circuit(1).rx(p, 0).rz(q, 0).to_gate().power(0.5, annotated=True), (0,))
    observable = qb.Hamiltonian([(1e308, qb.PauliString(())), (1e308, qb.PauliZ(0))])
    node = QNode.from_circuit(source, observable, interface="tensorflow", max_diff=2, diff_method="adjoint")
    no_host(monkeypatch)
    fn = tf.function(node, autograph=False, jit_compile=False) if traced else node
    with pytest.raises(tf.errors.InvalidArgumentError, match="Nonfinite"):
        fn(tf.constant([0.37, 0.82], tf.float64))
