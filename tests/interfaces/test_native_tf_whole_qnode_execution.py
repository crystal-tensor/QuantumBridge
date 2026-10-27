# Copyright 2026 QuantumBridge Contributors. Apache-2.0.
"""Full native circuit/state/format lineage, independently generated fixtures."""

import json
from pathlib import Path

import numpy as np
import pytest

import quantumbridge as qb
from quantumbridge.qml import QNode
from quantumbridge.interfaces.tensorflow_whole_execution import TensorFlowStatevectorPlan

tf = pytest.importorskip("tensorflow")
CASES = json.loads((Path(__file__).parents[1] / "information/data/tf_whole_qnode_oracles.json").read_text())["cases"]


def source_and_observables(case):
    p, q = qb.ParameterVector("angles", 2)
    body = qb.Circuit(1).ry(-p, 0).rz(q*q+0.4, 0).rx(p, 0)
    gate = body.to_gate().power(0.5, annotated=True)
    source = qb.QuantumCircuit(case["width"])
    if case["name"] == "requested_reverse":
        source.append(gate, (1,))
        return source, (qb.PauliZ(1), qb.PauliX(1))
    source.h(0)
    source.global_phase = 0.17*p*q
    if case["name"] == "full_entangling":
        source.cx(0, 3)
        source.append(gate, (2,))
        source.ry(p*q, 0)
        source.cx(2, 1)
        source.rz(p-q, 3)
        other = qb.Hamiltonian([(1., qb.PauliString(((0, "X"), (3, "X")))), (0.2, qb.PauliString(((1, "Y"), (2, "Z"))))])
        return source, (qb.PauliZ(2), other)
    source.x(2)
    source.append(gate.control(2, ctrl_state="01" if case["name"] == "open_control" else "11"), (2, 0, 3))
    source.cx(3, 1)
    return source, (qb.PauliZ(3), qb.PauliX(0))


def node_for(source, observables):
    builder = QNode.from_circuit(source, observables[0]).fn
    def program(tape, point):
        first = builder(tape, point)
        return first, tape.expval(observables[1])
    return QNode(program, source.num_qubits, interface="tensorflow", max_diff=2, diff_method="adjoint")


def restore(source, transport):
    if transport == "ir":
        from quantumbridge.compat.qiskit_adapter import circuit_from_ir
        from quantumbridge.ir.qb_ir import IRProgram
        return circuit_from_ir(IRProgram.from_json(source.to_ir().to_json()))
    if transport == "qpy":
        from quantumbridge.serialization import qpy_dumps, qpy_loads
        return qpy_loads(qpy_dumps(source))[0]
    return source


def vector_signature(source):
    return tuple((p.uuid, p.index, p.vector._root_uuid, p.vector.name, len(p.vector)) for p in source.parameters)


@pytest.mark.parametrize("case", CASES, ids=lambda case: case["name"])
@pytest.mark.parametrize("traced", [False, True])
def test_complete_state_and_all_complex_jets_from_actual_compiled_plan(case, traced):
    source, observables = source_and_observables(case)
    before, identities = source.to_ir().to_json(), vector_signature(source)
    node = node_for(source, observables)
    def state(point):
        plan = node._construct((point,), {})
        whole = TensorFlowStatevectorPlan(plan)
        assert whole.operation_signatures == tuple((op.name, op.wires) for op in plan.circuit.lowered().operations)
        return whole.state(tf.stack(plan.recorder.angles))
    def execute(point):
        with tf.GradientTape(persistent=True) as outer:
            outer.watch(point)
            with tf.GradientTape(persistent=True) as inner:
                inner.watch(point)
                value = state(point)
                parts = tf.concat([tf.math.real(value), tf.math.imag(value)], 0)
            jacobian = inner.jacobian(parts, point, experimental_use_pfor=False)
        hessian = outer.jacobian(jacobian, point, experimental_use_pfor=False)
        return value, jacobian, hessian
    fn = tf.function(execute, autograph=False, jit_compile=False) if traced else execute
    value, j, h = fn(tf.constant(case["point"], tf.float64))
    raw = np.array(case["state"])[:, 0]
    np.testing.assert_allclose(value, raw[:, 0]+1j*raw[:, 1], atol=3e-12, rtol=0)
    np.testing.assert_allclose(j, case["state_jacobian"], atol=5e-10, rtol=0)
    np.testing.assert_allclose(h, case["state_hessians"], atol=8e-10, rtol=0)
    assert source.to_ir().to_json() == before and vector_signature(source) == identities


@pytest.mark.parametrize("case", CASES, ids=lambda case: case["name"])
@pytest.mark.parametrize("transport", [None, "ir", "qpy"])
def test_restored_public_qnode_hvp_uses_tf_whole_plan(case, transport, monkeypatch):
    source, observables = source_and_observables(case)
    original = source
    before, identities = source.to_ir().to_json(), vector_signature(source)
    source = restore(source, transport)
    restored_before = source.to_ir().to_json()
    assert vector_signature(source) == identities
    node = node_for(source, observables).compile(optimization_level=0,
        basis_gates=("rx", "ry", "rz", "sx", "phase", "cx", "crx", "native_matrix_power"))
    from quantumbridge.interfaces.tensorflow_graph import TensorFlowGraphKernel
    from quantumbridge.interfaces.native_host import NativeHostKernel
    def forbidden(*args, **kwargs):
        pytest.fail("Restored whole-QNode used a quantum host callback or full Hessian")
    monkeypatch.setattr(TensorFlowGraphKernel, "evaluate", forbidden)
    monkeypatch.setattr(NativeHostKernel, "run", forbidden)
    monkeypatch.setattr(NativeHostKernel, "run_second", forbidden)
    monkeypatch.setattr(tf.GradientTape, "jacobian", forbidden)
    @tf.function(autograph=False, jit_compile=False)
    def execute(point):
        with tf.GradientTape() as reverse:
            reverse.watch(point)
            with tf.autodiff.ForwardAccumulator(point, tf.constant([0.4, -0.3], tf.float64)) as forward:
                value = tf.stack(node(point))
                loss = tf.reduce_sum(tf.constant([0.7, -0.2], tf.float64)*(tf.exp(value)+0.2*value**3))
            tangent = forward.jvp(loss)
        return value, reverse.gradient(tangent, point)
    y, j, h = np.array(case["outputs"]), np.array(case["jacobian"]), np.array(case["hessians"])
    direction, weights = np.array([0.4, -0.3]), np.array([0.7, -0.2])
    expected = j.T @ (weights*(np.exp(y)+1.2*y)*(j @ direction))+np.einsum("i,ijk,k->j", weights*(np.exp(y)+0.6*y*y), h, direction)
    value, hvp = execute(tf.constant(case["point"], tf.float64))
    np.testing.assert_allclose(value, y, atol=3e-12, rtol=0)
    np.testing.assert_allclose(hvp, expected, atol=2e-9, rtol=0)
    assert node.last_metadata["native_tensor_execution"]
    assert original.to_ir().to_json() == before
    assert source.to_ir().to_json() == restored_before


@pytest.mark.parametrize("case", CASES, ids=lambda case: case["name"])
def test_partial_bind_retains_one_real_parameter_and_its_actual_derivatives(case):
    source, observables = source_and_observables(case)
    source = source.assign_parameters({source.parameters[1]: case["point"][1]})
    assert len(source.parameters) == 1 and source.parameters[0].index == 0
    node = node_for(source, observables)
    point = tf.constant([case["point"][0]], tf.float64)
    with tf.GradientTape(persistent=True) as outer:
        outer.watch(point)
        with tf.GradientTape(persistent=True) as inner:
            inner.watch(point)
            value = tf.stack(node(point))
        j = inner.jacobian(value, point, experimental_use_pfor=False)
    h = outer.jacobian(j, point, experimental_use_pfor=False)
    np.testing.assert_allclose(value, case["outputs"], atol=3e-12, rtol=0)
    np.testing.assert_allclose(j, np.array(case["jacobian"])[:, :1], atol=2e-9, rtol=0)
    np.testing.assert_allclose(h, np.array(case["hessians"])[:, :1, :1], atol=2e-9, rtol=0)


@pytest.mark.parametrize("change", ["remove", "reorder"])
def test_actual_plan_edits_change_the_executed_circuit_instead_of_hardcoded_math(change):
    case = CASES[1]
    source, observables = source_and_observables(case)
    if change == "remove":
        del source.operations[2]
    else:
        source.operations[0], source.operations[1] = source.operations[1], source.operations[0]
    point = np.array(case["point"])
    bound = source.assign_parameters(dict(zip(source.parameters, point)))
    device = qb.StatevectorDevice()
    expected = [device.expectation(bound, observable) for observable in observables]
    actual = node_for(source, observables)(tf.constant(point, tf.float64))
    np.testing.assert_allclose(actual, expected, atol=3e-12, rtol=0)
    assert not np.allclose(actual, case["outputs"], atol=1e-5, rtol=0)


def test_state_global_phase_pole_has_a_runtime_refusal_instead_of_nan_state():
    source, observables = source_and_observables(CASES[0])
    plan = node_for(source, observables)._construct((np.array([0.37, 0.82]),), {})
    plan.circuit.global_phase = 1/(plan.recorder.parameters[0]-0.37)
    whole = TensorFlowStatevectorPlan(plan)
    with pytest.raises(tf.errors.InvalidArgumentError, match="Nonfinite"):
        whole.state(tf.constant([0.37, 0.82], tf.float64))
