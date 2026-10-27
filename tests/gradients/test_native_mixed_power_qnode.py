# Copyright 2026 QuantumBridge Contributors. Apache-2.0.
"""Two independent input parameters, analytic SU(2) oracle and streamed HVP."""

import json
from pathlib import Path

import numpy as np
import pytest

import quantumbridge as qb
from quantumbridge.diff import HigherOrderLimits
from quantumbridge.qml import QNode
from quantumbridge.information import Operator

ORACLE = json.loads(
    (
        Path(__file__).parents[1] / "information/data/native_mixed_power_oracles.json"
    ).read_text()
)


def reference(point, power):
    p, q = point
    cp, sp, cq, sq = np.cos(p / 2), np.sin(p / 2), np.cos(q / 2), np.sin(q / 2)
    t = cp * cq
    dt = np.array([-0.5 * sp * cq, -0.5 * cp * sq])
    ddt = np.array([[-0.25 * t, 0.25 * sp * sq], [0.25 * sp * sq, -0.25 * t]])
    w = np.arccos(t)
    s, c = np.sin(w), np.cos(w)
    dw = -dt / s
    ddw = -ddt / s - t * np.outer(dt, dt) / s**3
    h = np.sin(power * w) / s
    dh = power * np.cos(power * w) / s - np.sin(power * w) * c / s**2
    ddh = (
        (1 - power * power) * h
        - 2 * power * np.cos(power * w) * c / s**2
        + 2 * np.sin(power * w) * c * c / s**3
    )
    r, dr, ddr = (
        sp * sp,
        np.array([0.5 * np.sin(p), 0.0]),
        np.diag([0.5 * np.cos(p), 0.0]),
    )
    value = 1 - 2 * r * h * h
    gradient = -2 * dr * h * h - 4 * r * h * dh * dw
    hessian = (
        -2 * ddr * h * h
        - 4 * h * dh * (np.outer(dr, dw) + np.outer(dw, dr))
        - 4 * r * ((dh * dh + h * ddh) * np.outer(dw, dw) + h * dh * ddw)
    )
    u = np.diag([cq - 1j * sq, cq + 1j * sq]) @ np.array(
        [[cp, -1j * sp], [-1j * sp, cp]]
    )
    matrix = (np.cos(power * w) - t * h) * np.eye(2) + h * u
    return value, gradient, hessian, matrix


def build(power=0.5, interface="numpy", **options):
    p, q = qb.Parameter("p"), qb.Parameter("q")
    body = qb.Circuit(1).rx(p, 0).rz(q, 0)
    source = qb.QuantumCircuit(1)
    source.append(body.to_gate().power(power, annotated=True), (0,))
    return source, QNode.from_circuit(
        source,
        qb.PauliZ(0),
        interface=interface,
        diff_method="adjoint",
        max_diff=2,
        **options,
    )


@pytest.mark.parametrize("point", [(0.37, 0.82), (1.3, -0.7), (4.7, 2.1)])
@pytest.mark.parametrize("power", [0.5, -0.5, 1.5])
def test_independent_parameters_reach_actual_matrix_jacobian_mixed_hessian_and_hvp(
    point, power
):
    source, node = build(power)
    point = np.asarray(point)
    before = source.to_ir().to_json()
    value, gradient, hessian, matrix = reference(point, power)
    assert node(point) == pytest.approx(value, abs=8e-12)
    np.testing.assert_allclose(
        node.compute_jacobian(point), gradient, atol=8e-11, rtol=0
    )
    np.testing.assert_allclose(node.compute_hessian(point), hessian, atol=2e-9, rtol=0)
    direction = np.array([0.4, -0.3])
    np.testing.assert_allclose(
        node.compute_hvp(direction, point), hessian @ direction, atol=2e-9, rtol=0
    )
    np.testing.assert_allclose(
        node.compute_jvp(direction, point), gradient @ direction, atol=8e-11, rtol=0
    )
    np.testing.assert_allclose(
        node.compute_vjp(0.7, point), 0.7 * gradient, atol=8e-11, rtol=0
    )
    plan = node._construct((point,), {})
    actual = Operator(
        plan.circuit.bind(
            dict(zip(plan.recorder.parameters, plan.recorder.native_values()))
        )
    ).data
    np.testing.assert_allclose(actual, matrix, atol=8e-12, rtol=0)
    assert source.to_ir().to_json() == before


def test_streamed_mixed_hvp_does_not_materialize_a_hessian(monkeypatch):
    from quantumbridge.diff.qnode_engine import ExecutionPlan

    _, node = build(higher_order_limits=HigherOrderLimits(max_hessian_elements=1))
    original = ExecutionPlan.second_derivatives
    calls = []

    def guarded(self, values, *args, **kwargs):
        assert kwargs.get("direction") is not None
        result = original(self, values, *args, **kwargs)
        assert result[2].shape == (1, 2, 1)
        calls.append(result[2].shape)
        return result

    monkeypatch.setattr(ExecutionPlan, "second_derivatives", guarded)
    point, direction = np.array([0.37, 0.82]), np.array([0.4, -0.3])
    expected = reference(point, 0.5)[2] @ direction
    np.testing.assert_allclose(
        node.compute_hvp(direction, point), expected, atol=2e-9, rtol=0
    )
    assert calls and node.last_metadata["hvp_streamed"]


@pytest.mark.parametrize("case", ORACLE["su2"])
def test_closed_form_su2_oracle_agrees_with_independent_high_precision(case):
    value, gradient, hessian, _ = reference(ORACLE["point"], case["power"])
    np.testing.assert_allclose(value, case["value"], atol=3e-15, rtol=0)
    np.testing.assert_allclose(gradient, case["gradient"], atol=3e-15, rtol=0)
    np.testing.assert_allclose(hessian, case["hessian"], atol=3e-15, rtol=0)


def two_wire_source(power, control):
    p, q = qb.ParameterVector("angles", 2)
    body = qb.Circuit(2).rx(p, 0).rz(q, 1).rxx(p * q, 0, 1)
    body.global_phase = 0.13 * p * q
    operation = body.to_gate().power(power, annotated=True)
    if control is not None:
        operation = operation.control(ctrl_state=control)
    source = qb.QuantumCircuit(operation.num_qubits)
    if control is not None:
        source.h(0)
    source.append(operation, range(operation.num_qubits))
    return source


@pytest.mark.parametrize("control", [None, 0, 1])
@pytest.mark.parametrize("case", ORACLE["two_wire"])
def test_entangling_two_wire_mixed_jets_and_coherent_global_phase_match_70_digit_oracle(
    case, control
):
    source = two_wire_source(case["power"], control)
    before = source.to_ir().to_json()
    node = QNode.from_circuit(
        source,
        qb.PauliZ(1) if control is None else qb.PauliX(0),
        max_diff=2,
        diff_method="best",
    )
    point, direction = np.array(ORACLE["point"]), np.array([0.4, -0.3])
    expected = case["ordinary" if control is None else "controlled"]
    np.testing.assert_allclose(node(point), expected["value"], atol=2e-11, rtol=0)
    np.testing.assert_allclose(
        node.compute_jacobian(point), expected["gradient"], atol=2e-10, rtol=0
    )
    np.testing.assert_allclose(
        node.compute_hessian(point), expected["hessian"], atol=3e-9, rtol=0
    )
    np.testing.assert_allclose(
        node.compute_hvp(direction, point),
        np.array(expected["hessian"]) @ direction,
        atol=3e-9,
        rtol=0,
    )
    plan = node._construct((point,), {})
    actual = Operator(
        plan.circuit.bind(
            dict(zip(plan.recorder.parameters, plan.recorder.native_values()))
        )
    ).data
    encoded = np.asarray(case["matrix"])
    matrix = encoded[:, :, 0] + 1j * encoded[:, :, 1]
    if control is not None:
        expected_matrix = np.eye(8, dtype=complex)
        expected_matrix[
            4 * control : 4 * control + 4, 4 * control : 4 * control + 4
        ] = matrix
        matrix = expected_matrix @ np.kron(
            np.array([[1, 1], [1, -1]]) / np.sqrt(2), np.eye(4)
        )
    np.testing.assert_allclose(actual, matrix, atol=2e-11, rtol=0)
    assert source.to_ir().to_json() == before


@pytest.mark.parametrize("format", ["ir", "qpy"])
@pytest.mark.parametrize("control", [0, 1])
@pytest.mark.parametrize("case", ORACLE["two_wire"])
def test_two_parameter_vector_power_roundtrip_reaches_actual_hvp(case, control, format):
    from quantumbridge.compat.qiskit_adapter import circuit_from_ir
    from quantumbridge.ir.qb_ir import IRProgram
    from quantumbridge.serialization import qpy_dumps, qpy_loads

    source = two_wire_source(case["power"], control)
    restored = (
        qpy_loads(qpy_dumps(source))[0]
        if format == "qpy"
        else circuit_from_ir(IRProgram.from_json(source.to_ir().to_json()))
    )
    assert tuple(p.uuid for p in restored.parameters) == tuple(
        p.uuid for p in source.parameters
    )
    node = QNode.from_circuit(restored, qb.PauliX(0), max_diff=2, diff_method="adjoint")
    point, direction = np.array(ORACLE["point"]), np.array([0.4, -0.3])
    expected = case["controlled"]
    np.testing.assert_allclose(node(point), expected["value"], atol=2e-11, rtol=0)
    np.testing.assert_allclose(
        node.compute_jacobian(point), expected["gradient"], atol=2e-10, rtol=0
    )
    np.testing.assert_allclose(
        node.compute_hvp(direction, point),
        np.array(expected["hessian"]) @ direction,
        atol=3e-9,
        rtol=0,
    )


@pytest.mark.parametrize("limit", ["max_adjoint_operations", "max_memory_bytes"])
def test_mixed_direction_work_and_workspace_are_rejected_before_simulation(
    limit, monkeypatch
):
    _, node = build(higher_order_limits=HigherOrderLimits(**{limit: 100}))
    monkeypatch.setattr(
        node.device, "statevector", lambda *a, **k: pytest.fail("unadmitted simulation")
    )
    monkeypatch.setattr(
        node.device,
        "expectation",
        lambda *a, **k: pytest.fail("unadmitted expectation"),
    )
    with pytest.raises(MemoryError, match=limit):
        node.compute_hvp(np.array([0.4, -0.3]), np.array(ORACLE["point"]))


@pytest.mark.parametrize("power", [0.5, -0.5, 1.5])
def test_nonlinear_symbolic_sin_exp_and_repeated_parameters_include_the_source_chain_rule(
    power,
):
    p, q = qb.Parameter("p"), qb.Parameter("q")
    body = qb.Circuit(1).rx(p.sin() + 0.2 * p * q, 0).rz(q.exp() + 0.4 * q * q, 0)
    source = qb.QuantumCircuit(1)
    source.append(body.to_gate().power(power, annotated=True), (0,))
    point = np.array([0.37, 0.18])
    x, y = point
    mapped = np.array([np.sin(x) + 0.2 * x * y, np.exp(y) + 0.4 * y * y])
    _, gradient, hessian, _ = reference(mapped, power)
    jacobian = np.array([[np.cos(x) + 0.2 * y, 0.2 * x], [0.0, np.exp(y) + 0.8 * y]])
    map_hessians = np.array(
        [[[-np.sin(x), 0.2], [0.2, 0.0]], [[0.0, 0.0], [0.0, np.exp(y) + 0.8]]]
    )
    expected_gradient = jacobian.T @ gradient
    expected_hessian = jacobian.T @ hessian @ jacobian + sum(
        g * h for g, h in zip(gradient, map_hessians)
    )
    node = QNode.from_circuit(source, qb.PauliZ(0), diff_method="adjoint", max_diff=2)
    np.testing.assert_allclose(
        node.compute_jacobian(point), expected_gradient, atol=2e-10, rtol=0
    )
    np.testing.assert_allclose(
        node.compute_hessian(point), expected_hessian, atol=3e-9, rtol=0
    )
    direction = np.array([0.4, -0.3])
    np.testing.assert_allclose(
        node.compute_hvp(direction, point),
        expected_hessian @ direction,
        atol=3e-9,
        rtol=0,
    )
    for index in range(2):
        bound = source.assign_parameters({(p, q)[1 - index]: point[1 - index]})
        partial = QNode.from_circuit(
            bound, qb.PauliZ(0), diff_method="adjoint", max_diff=2
        )
        np.testing.assert_allclose(
            partial.compute_jacobian(point[index]),
            expected_gradient[index],
            atol=2e-10,
            rtol=0,
        )
        np.testing.assert_allclose(
            partial.compute_hessian(point[index]),
            expected_hessian[index, index],
            atol=3e-9,
            rtol=0,
        )


def test_eight_parameter_hvp_streams_directions_with_full_hessian_entry_patched_to_fail(
    monkeypatch,
):
    parameters = qb.ParameterVector("x", 8)
    a, b = np.linspace(0.2, -0.1, 8), np.linspace(0.1, 0.3, 8)
    body = (
        qb.Circuit(1)
        .rx(sum(v * p for v, p in zip(a, parameters)), 0)
        .rz(sum(v * p for v, p in zip(b, parameters)), 0)
    )
    source = qb.QuantumCircuit(1)
    source.append(body.to_gate().power(0.5, annotated=True), (0,))
    node = QNode.from_circuit(
        source,
        qb.PauliZ(0),
        max_diff=2,
        diff_method="adjoint",
        higher_order_limits=HigherOrderLimits(max_hessian_elements=1),
    )
    monkeypatch.setattr(
        node,
        "compute_hessian",
        lambda *a, **k: pytest.fail("HVP may not compute a full Hessian"),
    )
    point = np.linspace(0.1, 0.8, 8)
    mapping = np.stack([a, b])
    expected_hessian = mapping.T @ reference(mapping @ point, 0.5)[2] @ mapping
    for direction in (np.linspace(-0.2, 0.4, 8), np.linspace(0.3, -0.1, 8)):
        np.testing.assert_allclose(
            node.compute_hvp(direction, point),
            expected_hessian @ direction,
            atol=3e-9,
            rtol=0,
        )
        assert node.last_metadata["hvp_streamed"]
        assert node.last_metadata["second_order_work"]["adjoint_second_sweeps"] == 1


def test_same_named_wrong_uuid_binding_is_rejected_without_changing_source():
    source, _ = build()
    before = source.to_ir().to_json()
    with pytest.raises((KeyError, ValueError)):
        source.assign_parameters({qb.Parameter("p"): 0.37})
    assert source.to_ir().to_json() == before


@pytest.mark.parametrize("kind", ["iterable", "shape", "complex", "nonfinite"])
def test_invalid_direction_intake_fails_before_matrix_jet_work(kind, monkeypatch):
    from quantumbridge.diff import matrix_power_jet as jets

    source, _ = build()
    annotation = source.operations[0].metadata["annotated_operation"]
    metadata = jets.recorded_matrix_power(annotation).definition.operations[0].metadata

    class Unbounded:
        def __iter__(self):
            pytest.fail("Unbounded direction intake must not iterate")

    direction = (
        Unbounded()
        if kind == "iterable"
        else np.array([0.4])
        if kind == "shape"
        else np.array([0.4 + 1j, -0.3])
        if kind == "complex"
        else np.array([np.inf, -0.3])
    )
    monkeypatch.setattr(
        jets,
        "_body_directions",
        lambda *a, **k: pytest.fail("Invalid direction reached the matrix jet"),
    )
    with pytest.raises((TypeError, ValueError)):
        jets.matrix_power_directions((0.37, 0.82), metadata, (1.0, 0.0), direction)


def test_foreign_direction_array_cannot_dispatch_numpy_callbacks():
    from quantumbridge.diff import matrix_power_jet as jets

    source, _ = build()
    metadata = (
        jets.recorded_matrix_power(source.operations[0].metadata["annotated_operation"])
        .definition.operations[0]
        .metadata
    )

    class Foreign(np.ndarray):
        def __array_function__(self, *a, **k):
            pytest.fail("Foreign array function dispatched")

        def __array_ufunc__(self, *a, **k):
            pytest.fail("Foreign array ufunc dispatched")

    normal = np.array([0.4, -0.3])
    received = jets.matrix_power_directions(
        (0.37, 0.82), metadata, (1.0, 0.0), normal.view(Foreign)
    )
    expected = jets.matrix_power_directions((0.37, 0.82), metadata, (1.0, 0.0), normal)
    for actual, reference_matrix in zip(received, expected):
        np.testing.assert_allclose(actual, reference_matrix, atol=3e-12, rtol=0)


@pytest.mark.parametrize("offset", [-0.03, 0.03])
def test_two_sided_near_cut_derivatives_preserve_the_actual_spectral_branch(offset):
    p, q = qb.Parameter("p"), qb.Parameter("q")
    source = qb.QuantumCircuit(2)
    source.h(0)
    source.append(
        qb.Circuit(1)
        .ry(-p, 0)
        .rz(q, 0)
        .ry(p, 0)
        .to_gate()
        .power(0.5, annotated=True)
        .control(),
        (0, 1),
    )
    node = QNode.from_circuit(source, qb.PauliX(0), max_diff=2, diff_method="adjoint")
    point = np.array([0.37, 2 * np.pi + offset])
    phase = -0.5 * np.angle(np.exp(-0.5j * point[1]))
    expected_gradient = np.array([0.0, -0.25 * np.sin(phase)])
    np.testing.assert_allclose(node(point), np.cos(phase), atol=8e-11, rtol=0)
    np.testing.assert_allclose(
        node.compute_jacobian(point), expected_gradient, atol=8e-11, rtol=0
    )
    expected_hessian = np.diag([0.0, -0.0625 * np.cos(phase)])
    np.testing.assert_allclose(
        node.compute_hessian(point), expected_hessian, atol=3e-9, rtol=0
    )


@pytest.mark.parametrize("offset", [-1e-4, 1e-4])
def test_ill_conditioned_near_cut_derivatives_refuse_wrong_finite_results(offset):
    p, q = qb.Parameter("p"), qb.Parameter("q")
    source = qb.QuantumCircuit(2)
    source.h(0)
    source.append(
        qb.Circuit(1)
        .ry(-p, 0)
        .rz(q, 0)
        .ry(p, 0)
        .to_gate()
        .power(0.5, annotated=True)
        .control(),
        (0, 1),
    )
    node = QNode.from_circuit(source, qb.PauliX(0), max_diff=2, diff_method="adjoint")
    point = np.array([0.37, 2 * np.pi + offset])
    before = source.to_ir().to_json()
    phase = -0.5 * np.angle(np.exp(-0.5j * point[1]))
    # Values can resolve while derivatives do not. This previously returned
    # a finite first derivative wrong by4.3e-9 and second derivative by1e-4.
    np.testing.assert_allclose(node(point), np.cos(phase), atol=8e-11, rtol=0)
    with pytest.raises(np.linalg.LinAlgError, match="ill-conditioned.*branch"):
        node.compute_jacobian(point)
    with pytest.raises(np.linalg.LinAlgError, match="ill-conditioned.*branch"):
        node.compute_hessian(point)
    assert source.to_ir().to_json() == before


def test_exact_two_parameter_branch_cut_refuses_without_mutating_owner():
    p, q = qb.Parameter("p"), qb.Parameter("q")
    source = qb.QuantumCircuit(1)
    source.append(
        qb.Circuit(1).ry(-p, 0).rz(q, 0).ry(p, 0).to_gate().power(0.5, annotated=True),
        (0,),
    )
    node = QNode.from_circuit(source, qb.PauliZ(0), max_diff=2, diff_method="adjoint")
    before = source.to_ir().to_json()
    with pytest.raises((ValueError, np.linalg.LinAlgError), match="branch"):
        node.compute_hessian(np.array([0.37, 2 * np.pi]))
    assert source.to_ir().to_json() == before


@pytest.mark.parametrize("kind", ["duplicate", "swapped"])
def test_malformed_multi_uuid_map_fails_before_direction_evaluation(kind, monkeypatch):
    from copy import deepcopy
    from quantumbridge.diff import matrix_power_jet as jets

    source, _ = build()
    before = source.to_ir().to_json()
    metadata = deepcopy(
        jets.recorded_matrix_power(source.operations[0].metadata["annotated_operation"])
        .definition.operations[0]
        .metadata
    )
    identities = metadata["matrix_power_source"]["parameter_uuids"]
    identities[:] = (
        [identities[0], identities[0]] if kind == "duplicate" else identities[::-1]
    )
    monkeypatch.setattr(
        jets,
        "_body_directions",
        lambda *a, **k: pytest.fail("Malformed UUID map reached derivatives"),
    )
    with pytest.raises(ValueError, match="identit"):
        jets.matrix_power_directions((0.37, 0.82), metadata, (1.0, 0.0), (0.0, 1.0))
    assert source.to_ir().to_json() == before
