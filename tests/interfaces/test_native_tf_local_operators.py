# Copyright 2026 QuantumBridge Contributors. Apache-2.0.
"""Existing native plans feed actual TF local matrices, not another circuit."""

import json
from pathlib import Path

import numpy as np
import pytest

import quantumbridge as qb
from quantumbridge.qml import QNode
from quantumbridge.interfaces.tensorflow_native_execution import TensorFlowLocalOperator

tf = pytest.importorskip("tensorflow")
CASES = json.loads((Path(__file__).parents[1] / "information/data/tf_native_tensor_execution_oracles.json").read_text())["cases"][1:]


def native_matrix(point, case, transport=None):
    p, q = qb.ParameterVector("angles", 2)
    body = qb.Circuit(1).rx(p, 0).rz(q if case["body"] == "su2" else q*q+0.4, 0)
    if case["body"] == "requested":
        body.ry(-p, 0)
    body.global_phase = case["phase_offset"]+case["phase_scale"]*p*q
    operation = body.to_gate().power(case["power"], annotated=True)
    controlled = case.get("control") is not None
    if controlled:
        operation = operation.control(ctrl_state=case["control"])
    source = qb.QuantumCircuit(2 if controlled else 1)
    source.append(operation, tuple(range(source.num_qubits)))
    before = source.to_ir().to_json()
    original = source
    identities = tuple(value.uuid for value in source.parameters)
    if transport == "ir":
        from quantumbridge.compat.qiskit_adapter import circuit_from_ir
        from quantumbridge.ir.qb_ir import IRProgram
        source = circuit_from_ir(IRProgram.from_json(before))
    elif transport == "qpy":
        from quantumbridge.serialization import qpy_dumps, qpy_loads
        source = qpy_loads(qpy_dumps(source))[0]
    assert tuple(value.uuid for value in source.parameters) == identities
    restored_before = source.to_ir().to_json()
    frame = source.operations[0]
    node = QNode.from_circuit(source, qb.PauliZ(source.num_qubits-1), interface="tensorflow", max_diff=2, diff_method="adjoint")
    plan = node._construct((point,), {})
    kernel = TensorFlowLocalOperator(plan, 0)
    assert kernel.source_parameter_uuids == tuple(map(str, identities))
    assert kernel.wires == tuple(range(source.num_qubits))
    assert kernel.compiled_operation_names == ("native_matrix_power",)
    matrix = kernel(tf.stack(plan.recorder.angles))
    assert original.to_ir().to_json() == before
    assert source.to_ir().to_json() == restored_before
    assert source.operations[0] is frame
    return matrix


def decoded(case):
    raw = np.asarray(case["operator"])
    matrix = raw[..., 0]+1j*raw[..., 1]
    if case.get("control") is not None:
        result = np.eye(4, dtype=complex)
        start = 2*case["control"]
        result[start:start+2, start:start+2] = matrix
        return result
    return matrix


def outputs(point, case):
    matrix = native_matrix(point, case)
    if case.get("control") is not None:
        initial = tf.constant([1, 0, 1, 0], tf.complex128)/tf.sqrt(tf.constant(2., tf.complex128))
        z = tf.linalg.diag(tf.constant([1., -1., 1., -1.], tf.complex128))
        x = tf.constant([[0, 0, 1, 0], [0, 0, 0, 1], [1, 0, 0, 0], [0, 1, 0, 0]], tf.complex128)
    else:
        initial = tf.constant([1, 0], tf.complex128)
        z, x = tf.linalg.diag(tf.constant([1., -1.], tf.complex128)), tf.constant([[0, 1], [1, 0]], tf.complex128)
    state = tf.linalg.matvec(matrix, initial)
    return tf.stack([tf.math.real(tf.reduce_sum(tf.math.conj(state)*tf.linalg.matvec(observable, state))) for observable in (z, x)])


def assert_no_callbacks(function):
    graph = function.get_concrete_function(tf.TensorSpec((2,), tf.float64)).graph.as_graph_def()
    ops = {node.op for node in graph.node}
    ops.update(node.op for item in graph.library.function for node in item.node_def)
    assert not ops & {"PyFunc", "EagerPyFunc", "PyFuncStateless", "Eig", "SelfAdjointEigV2", "MatrixLogarithm"}


@pytest.mark.parametrize("traced", [False, True])
@pytest.mark.parametrize("case", CASES, ids=lambda case: case["name"])
def test_existing_plan_full_complex_operator(case, traced, monkeypatch):
    from quantumbridge.core.gates import Gate
    from quantumbridge.information import Operator
    from quantumbridge.diff import matrix_power_jet
    def forbidden(*args, **kwargs):
        pytest.fail("A trainable local TF matrix delegated to a native dense/numeric evaluator")
    monkeypatch.setattr(Gate, "to_matrix", forbidden)
    monkeypatch.setattr(Operator, "__init__", forbidden)
    monkeypatch.setattr(matrix_power_jet, "matrix_power_value", forbidden)
    monkeypatch.setattr(matrix_power_jet, "_body_directions", forbidden)
    def fn(point):
        return native_matrix(point, case)
    if traced:
        fn = tf.function(fn, autograph=False, jit_compile=False)
    actual = fn(tf.constant(case["point"], tf.float64))
    assert actual.dtype == tf.complex128
    np.testing.assert_allclose(actual, decoded(case), atol=2e-12, rtol=0)
    if traced:
        assert_no_callbacks(fn)


@pytest.mark.parametrize("traced", [False, True])
@pytest.mark.parametrize("case", CASES, ids=lambda case: case["name"])
def test_existing_plan_quantum_jacobian_hessian(case, traced):
    def execute(point):
        with tf.GradientTape(persistent=True) as outer:
            outer.watch(point)
            with tf.GradientTape(persistent=True) as inner:
                inner.watch(point)
                value = outputs(point, case)
            jacobian = inner.jacobian(value, point, experimental_use_pfor=False)
        hessian = outer.jacobian(jacobian, point, experimental_use_pfor=False)
        return value, jacobian, hessian
    fn = tf.function(execute, autograph=False, jit_compile=False) if traced else execute
    actual = fn(tf.constant(case["point"], tf.float64))
    for value, expected in zip(actual, (case["outputs"], case["jacobian"], case["hessians"])):
        assert value is not None
        np.testing.assert_allclose(value, expected, atol=3e-10, rtol=0)
    if traced:
        assert_no_callbacks(fn)


@pytest.mark.parametrize("traced", [False, True])
@pytest.mark.parametrize("mode", ["for", "rof", "tape_tape"])
@pytest.mark.parametrize("loss_kind", ["square", "exponential_cubic"])
@pytest.mark.parametrize("case", CASES, ids=lambda case: case["name"])
def test_existing_plan_actual_mixed_ad(case, loss_kind, mode, traced, monkeypatch):
    def forbidden(*args, **kwargs):
        pytest.fail("Direction-only local TF derivatives built a full Jacobian/Hessian")
    monkeypatch.setattr(tf.GradientTape, "jacobian", forbidden)
    direction, weights = np.array([0.4, -0.3]), np.array([0.7, -0.2])
    y, j, h = np.array(case["outputs"]), np.array(case["jacobian"]), np.array(case["hessians"])
    first, second = (2*(y-0.3), np.full(2, 2.)) if loss_kind == "square" else (np.exp(y)+0.6*y*y, np.exp(y)+1.2*y)
    expected = j.T @ (weights*second*(j @ direction))+np.einsum("i,ijk,k->j", weights*first, h, direction)
    def execute(point):
        d = tf.constant(direction, tf.float64)
        def loss():
            y = outputs(point, case)
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
    np.testing.assert_allclose(actual, expected, atol=5e-10, rtol=0)
    if traced:
        assert_no_callbacks(fn)


@pytest.mark.parametrize("transport", ["ir", "qpy"])
@pytest.mark.parametrize("case", CASES, ids=lambda case: case["name"])
def test_existing_unbound_formats_reach_tf_operator(case, transport):
    np.testing.assert_allclose(native_matrix(tf.constant(case["point"], tf.float64), case, transport), decoded(case), atol=2e-12, rtol=0)


@pytest.mark.parametrize("traced", [False, True])
@pytest.mark.parametrize("case", CASES, ids=lambda case: case["name"])
def test_existing_plan_complete_complex_matrix_jets(case, traced):
    def components(point):
        matrix = native_matrix(point, case)
        return tf.concat([tf.reshape(tf.math.real(matrix), (-1,)), tf.reshape(tf.math.imag(matrix), (-1,))], 0)
    def execute(point):
        seeds = [tf.constant([1., 0.], tf.float64), tf.constant([0., 1.], tf.float64)]
        first, second = [], []
        for seed in seeds:
            with tf.autodiff.ForwardAccumulator(point, seed) as forward:
                value = components(point)
            first.append(forward.jvp(value))
        for left in seeds:
            row = []
            for right in seeds:
                with tf.autodiff.ForwardAccumulator(point, left) as outer:
                    with tf.autodiff.ForwardAccumulator(point, right) as inner:
                        value = components(point)
                    tangent = inner.jvp(value)
                row.append(outer.jvp(tangent))
            second.append(tf.stack(row, axis=1))
        return tf.stack(first, axis=1), tf.stack(second, axis=1)
    expected_j, expected_h = np.array(case["complex_jacobian"]), np.array(case["complex_hessians"])
    if case.get("control") is not None:
        indices = []
        for part in (0, 16):
            start = 2*case["control"]
            indices.extend(part+4*(start+row)+start+col for row in range(2) for col in range(2))
        full_j, full_h = np.zeros((32, 2)), np.zeros((32, 2, 2))
        full_j[indices], full_h[indices] = expected_j, expected_h
        expected_j, expected_h = full_j, full_h
    fn = tf.function(execute, autograph=False, jit_compile=False) if traced else execute
    j, h = fn(tf.constant(case["point"], tf.float64))
    np.testing.assert_allclose(j, expected_j, atol=5e-10, rtol=0)
    np.testing.assert_allclose(h, expected_h, atol=8e-10, rtol=0)
    if traced:
        assert_no_callbacks(fn)
