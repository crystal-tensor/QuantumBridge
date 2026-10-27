# Copyright 2026 QuantumBridge Contributors. Apache-2.0.
"""A genuinely moving eigenbasis through native QNode and adjoint Hessians."""

import cmath

import numpy as np
import pytest

import quantumbridge as qb
from quantumbridge.information import Operator
from quantumbridge.qml import QNode


def build(power=0.5, control=None, method="adjoint"):
    p = qb.Parameter("p")
    body = qb.Circuit(1).ry(-p, 0).rz(p * p + 0.4, 0).ry(p, 0)
    gate = body.to_gate()
    if control is not None:
        gate = gate.control(1, ctrl_state=control)
    circuit = qb.QuantumCircuit(gate.num_qubits)
    if control == 1:
        circuit.x(0)
    circuit.append(gate.power(power, annotated=True), range(gate.num_qubits))
    return circuit, QNode.from_circuit(
        circuit, qb.PauliZ(gate.num_qubits - 1), max_diff=2, diff_method=method
    )


def reference(point, power):
    phase = -power * cmath.phase(cmath.exp(-0.5j * (point * point + 0.4)))
    s, c, t, u = np.sin(point), np.cos(point), np.sin(phase), np.cos(phase)
    first_phase, second_phase = power * point, power
    value = 1 - 2 * s * s * t * t
    first = -4 * (s * c * t * t + s * s * t * u * first_phase)
    second = -4 * (
        (c * c - s * s) * t * t
        + 4 * s * c * t * u * first_phase
        + s * s * ((u * u - t * t) * first_phase**2 + t * u * second_phase)
    )
    x, z = np.array([[0, 1], [1, 0]], complex), np.diag([1.0, -1.0])
    matrix = np.cos(phase) * np.eye(2) - 1j * np.sin(phase) * (
        np.cos(point) * z + np.sin(point) * x
    )
    return value, first, second, matrix


@pytest.mark.parametrize("point", [0.37, 1.3, 2.8])
@pytest.mark.parametrize("power", [0.5, -0.5, 1.5])
@pytest.mark.parametrize("control", [None, 0, 1])
def test_noncommuting_family_has_actual_forward_adjoint_hessian_and_hvp(
    point, power, control
):
    source, node = build(power, control)
    before = source.to_ir().to_json()
    value, first, second, matrix = reference(point, power)
    assert node(point) == pytest.approx(value, abs=5e-12)
    assert node.compute_jacobian(point) == pytest.approx(first, abs=5e-11)
    assert node.compute_hessian(point) == pytest.approx(second, abs=8e-10)
    assert node.compute_hvp(0.7, point) == pytest.approx(0.7 * second, abs=8e-10)
    plan = node._construct((point,), {})
    bound = plan.circuit.bind(
        dict(zip(plan.recorder.parameters, plan.recorder.native_values()))
    )
    if control is not None:
        full = np.eye(4, dtype=complex)
        full[2 * control : 2 * control + 2, 2 * control : 2 * control + 2] = matrix
        if control == 1:
            full = full @ np.kron(np.array([[0, 1], [1, 0]]), np.eye(2))
        matrix = full
    np.testing.assert_allclose(Operator(bound).data, matrix, atol=5e-12, rtol=0)
    assert source.to_ir().to_json() == before


@pytest.mark.parametrize("format", ["ir", "qpy"])
def test_symbolic_source_roundtrip_preserves_identity_and_actual_derivatives(format):
    source, _ = build()
    if format == "qpy":
        from quantumbridge.serialization import qpy_dumps, qpy_loads

        restored = qpy_loads(qpy_dumps(source))[0]
    else:
        from quantumbridge.compat.qiskit_adapter import circuit_from_ir
        from quantumbridge.ir.qb_ir import IRProgram

        restored = circuit_from_ir(IRProgram.from_json(source.to_ir().to_json()))
    assert tuple(p.uuid for p in restored.parameters) == tuple(
        p.uuid for p in source.parameters
    )
    node = QNode.from_circuit(restored, qb.PauliZ(0), max_diff=2, diff_method="best")
    value, first, second, _ = reference(1.3, 0.5)
    np.testing.assert_allclose(
        [node(1.3), node.compute_jacobian(1.3), node.compute_hessian(1.3)],
        [value, first, second],
        atol=8e-10,
        rtol=0,
    )
    assert "native_matrix_power" not in source.to_ir().to_json()


@pytest.mark.parametrize(
    "order", ["inverse_power", "power_inverse", "power_twice", "open_control"]
)
def test_modifier_order_controls_and_nonconsecutive_invocation_wires(order):
    p = qb.Parameter("p")
    gate = qb.Circuit(1).ry(-p, 0).rz(p * p + 0.4, 0).ry(p, 0).to_gate()
    if order == "inverse_power":
        annotation = gate.inverse(annotated=True).power(0.5)
    elif order == "power_inverse":
        annotation = gate.power(0.5, annotated=True).inverse()
    elif order == "power_twice":
        annotation = gate.power(0.5, annotated=True).power(0.5)
    else:
        annotation = gate.power(0.5, annotated=True).control(2, ctrl_state=1)
    source = qb.QuantumCircuit(4)
    if order == "open_control":
        source.x(3)
    wires = (3, 0, 2) if order == "open_control" else (2,)
    source.append(annotation, wires)
    node = QNode.from_circuit(source, qb.PauliZ(2), max_diff=2, diff_method="adjoint")
    power = 0.25 if order == "power_twice" else 0.5 if order == "open_control" else -0.5
    value, first, second, _ = reference(1.3, power)
    np.testing.assert_allclose(
        [node(1.3), node.compute_jacobian(1.3), node.compute_hessian(1.3)],
        [value, first, second],
        atol=8e-10,
        rtol=0,
    )


def test_moving_family_exact_branch_cut_is_not_given_a_finite_derivative():
    source, node = build()
    before = source.to_ir().to_json()
    point = np.sqrt(2 * np.pi - 0.4)
    with pytest.raises((ValueError, np.linalg.LinAlgError), match="branch"):
        node.compute_jacobian(point)
    assert source.to_ir().to_json() == before


def test_resource_denial_happens_before_numeric_factorization(monkeypatch):
    from quantumbridge.execution import UnifiedExecutionLimits, UnifiedResourceLedger
    from quantumbridge.execution.resource_context import ResourceScope

    source, node = build()
    before = source.to_ir().to_json()
    ledger = UnifiedResourceLedger(UnifiedExecutionLimits(max_total_memory_bytes=0))
    monkeypatch.setattr(
        np.linalg,
        "eig",
        lambda *a, **k: pytest.fail("unadmitted numeric factorization"),
    )
    with ResourceScope(ledger), pytest.raises(MemoryError):
        node.compute_hessian(0.37)
    assert ledger.receipt()["live_memory_bytes"] == 0
    assert source.to_ir().to_json() == before


def test_general_power_cannot_hide_an_unsupported_variable_exponent():
    from quantumbridge.core.classical import UnsupportedFeature

    p, a = qb.Parameter("p"), qb.Parameter("a")
    body = qb.Circuit(1).rx(p, 0).ry(p * p, 0)
    source = qb.QuantumCircuit(1)
    source.append(body.to_gate().power(a, annotated=True), (0,))
    node = QNode.from_circuit(source, qb.PauliZ(0), diff_method="adjoint", max_diff=2)
    with pytest.raises(UnsupportedFeature, match="power|generator"):
        node.compute_hessian(0.5, 0.37)


@pytest.mark.parametrize("point", [0.37, 1.3])
def test_global_phase_inside_generic_power_is_visible_under_coherent_control(point):
    p = qb.Parameter("p")
    body = qb.Circuit(1).ry(-p, 0).rz(p * p + 0.4, 0).ry(p, 0)
    body.global_phase = 0.2 * p * p
    source = qb.QuantumCircuit(2)
    source.h(0)
    source.append(body.to_gate().power(0.5, annotated=True).control(), (0, 1))
    node = QNode.from_circuit(source, qb.PauliX(0), max_diff=2, diff_method="adjoint")
    # Independent analytic scalar: Re(exp(i*p*p/10) * V_00).
    phase, first_phase, second_phase = 0.1 * point * point, 0.2 * point, 0.2
    angle, first_angle, second_angle = 0.25 * (point * point + 0.4), 0.5 * point, 0.5
    c, s, u, t = np.cos(phase), np.sin(phase), np.cos(angle), np.sin(angle)
    cp, sp = np.cos(point), np.sin(point)
    value = c * u + s * t * cp
    first = (
        -s * first_phase * u
        - c * t * first_angle
        + c * first_phase * t * cp
        + s * u * first_angle * cp
        - s * t * sp
    )
    second = (
        -(c * first_phase**2 + s * second_phase) * u
        + 2 * s * first_phase * t * first_angle
        - c * (u * first_angle**2 + t * second_angle)
        + (-s * first_phase**2 + c * second_phase) * t * cp
        + 2 * c * first_phase * u * first_angle * cp
        - 2 * c * first_phase * t * sp
        + s * (-t * first_angle**2 + u * second_angle) * cp
        - 2 * s * u * first_angle * sp
        - s * t * cp
    )
    np.testing.assert_allclose(
        [node(point), node.compute_jacobian(point), node.compute_hessian(point)],
        [value, first, second],
        atol=8e-10,
        rtol=0,
    )


def test_repeated_identity_eigenvalues_have_finite_actual_second_derivatives():
    p = qb.Parameter("p")
    body = qb.Circuit(1).rx(p, 0).ry(p * p, 0)
    source = qb.QuantumCircuit(1)
    source.append(body.to_gate().power(0.5, annotated=True), (0,))
    node = QNode.from_circuit(source, qb.PauliZ(0), max_diff=2, diff_method="adjoint")
    assert node(0.0) == pytest.approx(1.0, abs=2e-12)
    assert node.compute_jacobian(0.0) == pytest.approx(0.0, abs=2e-12)
    assert node.compute_hessian(0.0) == pytest.approx(-0.25, abs=2e-12)


@pytest.mark.parametrize(
    "field,value",
    [("num_qubits", True), ("parameter_uuid", "wrong"), ("program", "{}")],
)
def test_transient_source_descriptor_is_validated_before_execution(field, value):
    from copy import deepcopy
    from quantumbridge.diff.matrix_power_jet import (
        matrix_power_derivative,
        recorded_matrix_power,
    )

    source, _ = build()
    annotation = source.operations[0].metadata["annotated_operation"]
    metadata = deepcopy(
        recorded_matrix_power(annotation).definition.operations[0].metadata
    )
    metadata["matrix_power_source"][field] = value
    with pytest.raises((ValueError, TypeError, KeyError)):
        matrix_power_derivative((0.37,), metadata, 1)


def test_general_jet_output_lease_is_retained_by_a_view_not_a_dead_source_graph():
    import gc
    from quantumbridge.diff.matrix_power_jet import (
        matrix_power_derivative,
        recorded_matrix_power,
    )
    from quantumbridge.execution import UnifiedResourceLedger
    from quantumbridge.execution.resource_context import ResourceScope

    source, _ = build()
    annotation = source.operations[0].metadata["annotated_operation"]
    metadata = recorded_matrix_power(annotation).definition.operations[0].metadata
    ledger = UnifiedResourceLedger()
    with ResourceScope(ledger):
        output = matrix_power_derivative((0.37,), metadata, 2)
    gc.collect()
    assert ledger.receipt()["live_memory_bytes"] == output.nbytes == 64
    view = output[0]
    del output
    gc.collect()
    assert ledger.receipt()["live_memory_bytes"] == 64
    del view
    gc.collect()
    assert ledger.receipt()["live_memory_bytes"] == 0


def test_transient_source_limit_counts_utf8_bytes_not_code_points():
    from copy import deepcopy
    from quantumbridge.diff.matrix_power_jet import (
        matrix_power_derivative,
        recorded_matrix_power,
    )
    from quantumbridge.serialization.errors import ResourceLimitError

    source, _ = build()
    metadata = deepcopy(
        recorded_matrix_power(source.operations[0].metadata["annotated_operation"])
        .definition.operations[0]
        .metadata
    )
    metadata["matrix_power_source"]["program"] = '"' + chr(0x4E2D) * 400000 + '"'
    with pytest.raises(ResourceLimitError, match="max_metadata_bytes"):
        matrix_power_derivative((0.37,), metadata, 1)


def test_transient_source_rejects_foreign_keys_before_hash_dispatch():
    from quantumbridge.diff.matrix_power_jet import matrix_power_derivative

    class Foreign(str):
        dispatch = False

        def __hash__(self):
            if self.dispatch:
                pytest.fail("foreign metadata key dispatched")
            return str.__hash__(self)

    key = Foreign("matrix_power_source")
    metadata = {key: {}}
    key.dispatch = True
    with pytest.raises(ValueError, match="metadata"):
        matrix_power_derivative((0.37,), metadata, 1)
