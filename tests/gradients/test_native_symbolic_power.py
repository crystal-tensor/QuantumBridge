# Copyright 2026 QuantumBridge Contributors. Apache-2.0.
"""Independent projector oracles for symbolic principal-power QNodes."""

import cmath

import numpy as np
import pytest

import quantumbridge as qb
from quantumbridge.circuit_library import CRXGate, CRYGate, CRZGate
from quantumbridge.core.classical import UnsupportedFeature
from quantumbridge.core.gate_limits import GateCircuitLimits, gate_circuit_scope
from quantumbridge.devices import DensityMatrixDevice, MatrixProductStateDevice
from quantumbridge.information import Operator
from quantumbridge.qml import QNode
from quantumbridge.serialization import qpy_dumps, qpy_loads


AXES = {
    "x": np.array([[0, 1], [1, 0]], complex),
    "y": np.array([[0, -1j], [1j, 0]], complex),
    "z": np.diag([1.0, -1.0]),
}
KINDS = {"x": CRXGate, "y": CRYGate, "z": CRZGate}
H = np.array([[1, 1], [1, -1]], complex) / np.sqrt(2)


def rotation(axis, value):
    return np.cos(value / 2) * np.eye(2) - 1j * np.sin(value / 2) * AXES[axis]


def projector_blocks(axis, value, power, control):
    blocks = [
        np.eye(4, dtype=complex),
        np.zeros((4, 4), complex),
        np.zeros((4, 4), complex),
    ]
    blocks[0][2 * control : 2 * control + 2, 2 * control : 2 * control + 2] = 0
    for sign in (-1, 1):
        phase = cmath.phase(cmath.exp(-0.5j * sign * value))
        scalar = cmath.exp(1j * power * phase)
        projector = (np.eye(2) + sign * AXES[axis]) / 2
        for order in range(3):
            blocks[order][
                2 * control : 2 * control + 2, 2 * control : 2 * control + 2
            ] += scalar * (-0.5j * sign * power) ** order * projector
    return blocks


def source_and_node(
    axis="y", power=0.5, control=1, method="parameter-shift", device=None
):
    p = qb.Parameter("p")
    source = qb.QuantumCircuit(2)
    source.h(0)
    source.ry(0.37, 1)
    source.rz(0.23, 1)
    source.append(
        KINDS[axis](p, ctrl_state=control).power(power, annotated=True), [0, 1]
    )
    return source, QNode.from_circuit(
        source, qb.PauliX(0), max_diff=2, diff_method=method, device=device
    )


def expected(axis, value, power, control):
    vector = np.kron(H, rotation("z", 0.23) @ rotation("y", 0.37))[:, 0]
    blocks = projector_blocks(axis, value, power, control)
    state, tangent, second = [matrix @ vector for matrix in blocks]
    observable = np.kron(AXES["x"], np.eye(2))
    return (
        np.vdot(state, observable @ state).real,
        2 * np.vdot(state, observable @ tangent).real,
        2
        * (
            np.vdot(tangent, observable @ tangent) + np.vdot(state, observable @ second)
        ).real,
    )


@pytest.mark.parametrize("axis", AXES)
@pytest.mark.parametrize("control", [0, 1])
@pytest.mark.parametrize("power", [0.5, -0.5, 1.5])
def test_unbound_symbolic_power_compiles_to_complete_branch_correct_matrix(
    axis, control, power
):
    source, node = source_and_node(axis, power, control)
    source_json = source.to_ir().to_json()
    for x in (7.3, 2 * np.pi - 0.03, 2 * np.pi + 0.03, -2 * np.pi - 0.03):
        plan = node._construct((x,), {})
        bound = plan.circuit.bind(
            dict(zip(plan.recorder.parameters, plan.recorder.native_values()))
        )
        preparation = np.kron(H, rotation("z", 0.23) @ rotation("y", 0.37))
        np.testing.assert_allclose(
            Operator(bound).data,
            projector_blocks(axis, x, power, control)[0] @ preparation,
            atol=3e-12,
            rtol=0,
        )
        assert node(x) == pytest.approx(expected(axis, x, power, control)[0], abs=3e-12)
    assert source.to_ir().to_json() == source_json


@pytest.mark.parametrize("axis", AXES)
@pytest.mark.parametrize("control", [0, 1])
@pytest.mark.parametrize("method", ["parameter-shift", "adjoint"])
def test_symbolic_power_jacobian_hessian_and_streamed_hvp(axis, control, method):
    _, node = source_and_node(axis, 1.5, control, method)
    for x in (7.3, 2 * np.pi - 0.02, 2 * np.pi + 0.02):
        value, first, second = expected(axis, x, 1.5, control)
        assert node(x) == pytest.approx(value, abs=3e-12)
        assert node.compute_jacobian(x) == pytest.approx(first, abs=4e-11)
        assert node.compute_hessian(x) == pytest.approx(second, abs=5e-11)
        assert node.compute_hvp(0.7, x) == pytest.approx(0.7 * second, abs=5e-11)
        assert node.last_metadata["hvp_streamed"] is True


@pytest.mark.parametrize(
    "device", [None, DensityMatrixDevice(), MatrixProductStateDevice()]
)
def test_roundtrip_preserves_delayed_power_and_executes_with_native_devices(device):
    source, _ = source_and_node("y", -0.5, 0)
    restored = qpy_loads(qpy_dumps(source))[0]
    assert tuple(p.uuid for p in restored.parameters) == tuple(
        p.uuid for p in source.parameters
    )
    node = QNode.from_circuit(restored, qb.PauliX(0), device=device, max_diff=2)
    value, first, second = expected("y", 7.3, -0.5, 0)
    assert node(7.3) == pytest.approx(value, abs=3e-12)
    assert node.compute_jacobian(7.3) == pytest.approx(first, abs=4e-11)
    assert node.compute_hessian(7.3) == pytest.approx(second, abs=5e-11)


def test_nested_control_inverse_and_power_modifiers_keep_their_order():
    p = qb.Parameter("p")
    operation = (
        CRYGate(p, ctrl_state=0)
        .power(0.5, annotated=True)
        .control(1, ctrl_state=0)
        .power(1.5)
        .inverse()
    )
    circuit = qb.QuantumCircuit(3)
    circuit.append(operation, [0, 1, 2])
    node = QNode.from_circuit(circuit, qb.PauliZ(2), max_diff=2)
    plan = node._construct((7.3,), {})
    bound = plan.circuit.bind(
        dict(zip(plan.recorder.parameters, plan.recorder.native_values()))
    )
    direct = circuit.assign_parameters({p: 7.3})
    np.testing.assert_allclose(
        Operator(bound).data, Operator(direct).data, atol=4e-12, rtol=0
    )
    assert node.compute_hessian(7.3) == pytest.approx(
        -(0.75**2) * np.cos(0.75 * (7.3 - 4 * np.pi)), abs=5e-11
    )


def test_zero_width_scalar_power_becomes_a_coherent_control_phase():
    p = qb.Parameter("p")
    body = qb.Circuit(0)
    body.global_phase = p
    operation = qb.AnnotatedOperation(
        body.to_gate(), [qb.PowerModifier(0.5), qb.ControlModifier(1, 0)]
    )
    source = qb.QuantumCircuit(1)
    source.h(0)
    source.append(operation, [0])
    node = QNode.from_circuit(source, qb.PauliX(0), max_diff=2)
    phase = cmath.phase(cmath.exp(7.3j)) / 2
    assert node(7.3) == pytest.approx(np.cos(phase), abs=3e-12)
    assert node.compute_jacobian(7.3) == pytest.approx(-0.5 * np.sin(phase), abs=4e-11)
    assert node.compute_hessian(7.3) == pytest.approx(-0.25 * np.cos(phase), abs=5e-11)


def test_exact_branch_switch_is_explicitly_rejected_without_mutating_the_source():
    source, node = source_and_node()
    before = source.to_ir().to_json()
    with pytest.raises((ValueError, UnsupportedFeature), match="branch"):
        node.compute_jacobian(2 * np.pi)
    assert source.to_ir().to_json() == before


def test_noncommuting_symbolic_generator_is_not_given_an_invalid_shift_rule():
    p = qb.Parameter("p")
    body = qb.Circuit(1).rx(p, 0).ry(p * p, 0)
    source = qb.QuantumCircuit(1)
    source.append(body.to_gate().power(0.5, annotated=True), [0])
    node = QNode.from_circuit(source, qb.PauliZ(0), max_diff=2, diff_method="parameter-shift")
    with pytest.raises(UnsupportedFeature, match="no fixed native parameter-shift recipe"):
        node.compute_hessian(0.37)


def test_local_power_on_hundred_wire_mps_never_requests_a_full_state(monkeypatch):
    p = qb.Parameter("p")
    source = qb.QuantumCircuit(100)
    source.x(98)
    source.append(CRYGate(p).power(0.5, annotated=True), [98, 99])
    device = MatrixProductStateDevice(max_bond_dim=4)
    node = QNode.from_circuit(source, qb.PauliZ(99), device=device, max_diff=2)
    monkeypatch.setattr(
        device, "statevector", lambda *a, **k: pytest.fail("full MPS state requested")
    )
    assert node(7.3) == pytest.approx(np.cos(0.5 * (7.3 - 4 * np.pi)), abs=4e-12)
    assert node.compute_hvp(0.7, 7.3) == pytest.approx(
        -0.175 * np.cos(0.5 * (7.3 - 4 * np.pi)), abs=5e-11
    )


def test_power_local_dimension_limit_is_checked_before_spectral_work(monkeypatch):
    source, node = source_and_node()
    monkeypatch.setattr(
        np.linalg, "eig", lambda *a, **k: pytest.fail("unexpected spectral allocation")
    )
    with (
        gate_circuit_scope(GateCircuitLimits(max_matrix_dimension=2)),
        pytest.raises(MemoryError),
    ):
        node(7.3)


@pytest.mark.parametrize("method", ["parameter-shift", "adjoint"])
def test_variable_exponent_retains_mixed_classical_second_derivatives(method):
    a, p = qb.Parameter("a"), qb.Parameter("p")
    source = qb.QuantumCircuit(2)
    source.h(0)
    source.append(qb.AnnotatedOperation(CRYGate(p), qb.PowerModifier(a)), [0, 1])
    node = QNode.from_circuit(source, qb.PauliX(0), max_diff=2, diff_method=method)
    x, exponent = 7.3, 0.5
    w, phase = x - 4 * np.pi, exponent * (x - 4 * np.pi) / 2
    gradient = -np.sin(phase) * np.array([w / 2, exponent / 2])
    hessian = -np.cos(phase) * np.outer([w / 2, exponent / 2], [w / 2, exponent / 2])
    hessian[0, 1] -= 0.5 * np.sin(phase)
    hessian[1, 0] -= 0.5 * np.sin(phase)
    point, vector = np.array([exponent, x]), np.array([0.2, -0.7])
    assert node(point) == pytest.approx(np.cos(phase), abs=3e-12)
    np.testing.assert_allclose(
        node.compute_jacobian(point), gradient, atol=5e-11, rtol=0
    )
    np.testing.assert_allclose(node.compute_hessian(point), hessian, atol=6e-11, rtol=0)
    np.testing.assert_allclose(
        node.compute_hvp(vector, point), hessian @ vector, atol=6e-11, rtol=0
    )


@pytest.mark.parametrize("method", ["parameter-shift", "adjoint"])
@pytest.mark.parametrize("level", [0, 1, 2])
def test_basis_compiler_keeps_the_branch_correct_classical_graph(method, level):
    _, node = source_and_node("y", 0.5, 0, method)
    node = node.compile(basis_gates=["rz", "sx", "cx"], optimization_level=level)
    value, first, second = expected("y", 7.3, 0.5, 0)
    assert node(7.3) == pytest.approx(value, abs=4e-12)
    assert node.compute_jacobian(7.3) == pytest.approx(first, abs=6e-11)
    assert node.compute_hessian(7.3) == pytest.approx(second, abs=7e-11)


@pytest.mark.parametrize("format", ["ir", "qpy"])
@pytest.mark.parametrize("power", [0.5, -0.5, 1.5])
def test_symbolic_modifier_roundtrip_uses_parameter_uuids_not_cached_numeric_matrices(
    format, power
):
    source, _ = source_and_node("x", power, 0)
    if format == "qpy":
        restored = qpy_loads(qpy_dumps(source))[0]
    else:
        from quantumbridge.compat.qiskit_adapter import circuit_from_ir
        from quantumbridge.ir.qb_ir import IRProgram

        restored = circuit_from_ir(IRProgram.from_json(source.to_ir().to_json()))
    assert tuple(p.uuid for p in restored.parameters) == tuple(
        p.uuid for p in source.parameters
    )
    node = QNode.from_circuit(restored, qb.PauliX(0), max_diff=2)
    assert node(7.3) == pytest.approx(expected("x", 7.3, power, 0)[0], abs=4e-12)


@pytest.mark.parametrize("value", [float("nan"), float("inf"), -float("inf")])
def test_nonfinite_symbolic_power_input_rejects_without_source_mutation(value):
    source, node = source_and_node()
    before = source.to_ir().to_json()
    with pytest.raises(ValueError):
        node(value)
    assert source.to_ir().to_json() == before


@pytest.mark.parametrize("offset", [-1e-6, 1e-6])
def test_resolvable_near_cut_points_are_not_mistaken_for_a_branch_switch(offset):
    _, node = source_and_node("y", 0.5)
    x = 2 * np.pi + offset
    assert node.compute_hessian(x) == pytest.approx(
        expected("y", x, 0.5, 1)[2], abs=5e-11
    )


def test_edited_standard_definition_is_not_replaced_by_its_original_class_formula():
    p = qb.Parameter("p")
    gate = CRYGate(p)
    gate.definition.x(1)
    source = qb.QuantumCircuit(2)
    source.append(gate.power(0.5, annotated=True), [0, 1])
    node = QNode.from_circuit(source, qb.PauliZ(1), max_diff=2)
    before = source.to_ir().to_json()
    with pytest.raises(UnsupportedFeature, match="edited controlled definition"):
        node(0.37)
    assert source.to_ir().to_json() == before


def test_resource_denial_precedes_numeric_work_and_releases_retained_storage(
    monkeypatch,
):
    from quantumbridge.execution import UnifiedExecutionLimits, UnifiedResourceLedger
    from quantumbridge.execution.resource_context import ResourceScope

    source, node = source_and_node()
    before = source.to_ir().to_json()
    ledger = UnifiedResourceLedger(UnifiedExecutionLimits(max_total_memory_bytes=0))
    monkeypatch.setattr(
        np.linalg, "eig", lambda *a, **k: pytest.fail("spectral work before admission")
    )
    with ResourceScope(ledger), pytest.raises(MemoryError):
        node(7.3)
    assert ledger.receipt()["live_memory_bytes"] == 0
    assert source.to_ir().to_json() == before


def test_array_subclass_cannot_dispatch_during_symbolic_spectral_preprocessing():
    class Foreign(np.ndarray):
        def __array_ufunc__(self, *args, **kwargs):
            pytest.fail("foreign scalar dispatched")

    _, node = source_and_node()
    with pytest.raises(UnsupportedFeature, match="native real scalars"):
        node(np.array(7.3).view(Foreign))


@pytest.mark.parametrize("point", [1e6 + 0.37, 1e12 + 0.37])
def test_large_angles_use_complex_phase_reduction_without_cancellation(point):
    _, node = source_and_node("y", 0.5, 0)
    value, first, second = expected("y", point, 0.5, 0)
    assert node(point) == pytest.approx(value, abs=3e-12)
    assert node.compute_jacobian(point) == pytest.approx(first, abs=5e-11)
    assert node.compute_hessian(point) == pytest.approx(second, abs=6e-11)


@pytest.mark.parametrize("reverse", [False, True])
@pytest.mark.parametrize("power", [0.5, -0.5, 1.5])
def test_generic_commuting_tensor_definition_uses_its_common_projector_frame(
    reverse, power
):
    p = qb.Parameter("p")
    body = qb.Circuit(2).rx(p, int(reverse)).rz(2 * p, int(not reverse))
    body.global_phase = p / 3
    source = qb.QuantumCircuit(2)
    source.append(body.to_gate().power(power, annotated=True), [0, 1])
    node = QNode.from_circuit(source, qb.PauliZ(int(reverse)), max_diff=2)
    x = 7.3
    blocks = [np.zeros((4, 4), complex) for _ in range(3)]
    for sx in (-1, 1):
        for sz in (-1, 1):
            local = [(np.eye(2) + sx * AXES["x"]) / 2, (np.eye(2) + sz * AXES["z"]) / 2]
            if reverse:
                local.reverse()
            phase = x / 3 - sx * x / 2 - sz * x
            scalar = cmath.exp(1j * power * cmath.phase(cmath.exp(1j * phase)))
            for order in range(3):
                blocks[order] += (
                    scalar
                    * (1j * power * (1 / 3 - sx / 2 - sz)) ** order
                    * np.kron(*local)
                )
    plan = node._construct((x,), {})
    bound = plan.circuit.bind(
        dict(zip(plan.recorder.parameters, plan.recorder.native_values()))
    )
    np.testing.assert_allclose(Operator(bound).data, blocks[0], atol=4e-12, rtol=0)
    state, tangent, second = [matrix[:, 0] for matrix in blocks]
    observable = (
        np.kron(AXES["z"], np.eye(2)) if not reverse else np.kron(np.eye(2), AXES["z"])
    )
    first = 2 * np.vdot(state, observable @ tangent).real
    hessian = (
        2
        * (
            np.vdot(tangent, observable @ tangent) + np.vdot(state, observable @ second)
        ).real
    )
    assert node(x) == pytest.approx(np.vdot(state, observable @ state).real, abs=4e-12)
    assert node.compute_jacobian(x) == pytest.approx(first, abs=6e-11)
    assert node.compute_hessian(x) == pytest.approx(hessian, abs=7e-11)


def test_tensor_spectrum_work_is_admitted_before_expanding_any_primitive(monkeypatch):
    import quantumbridge.diff.symbolic_power as implementation

    p = qb.Parameter("p")
    body = qb.Circuit(2)
    for _ in range(40):
        body.rx(p, 0).rz(p, 1)
    source = qb.QuantumCircuit(2)
    source.append(body.to_gate().power(0.5, annotated=True), [0, 1])
    node = QNode.from_circuit(source, qb.PauliZ(0))
    before = source.to_ir().to_json()
    monkeypatch.setattr(
        implementation,
        "_primitive",
        lambda *a, **k: pytest.fail("unadmitted tensor spectral expansion"),
    )
    with (
        gate_circuit_scope(GateCircuitLimits(max_decomposition_work=256)),
        pytest.raises(MemoryError, match="max_decomposition_work"),
    ):
        node(0.37)
    assert source.to_ir().to_json() == before


@pytest.mark.parametrize("format", ["ir", "qpy"])
def test_power_and_control_modifier_order_survives_real_roundtrip(format):
    a, p = qb.Parameter("a"), qb.Parameter("p")
    operation = qb.AnnotatedOperation(
        CRYGate(p, ctrl_state=0),
        [
            qb.PowerModifier(0.5 if format == "qpy" else a),
            qb.ControlModifier(1, 0),
            qb.InverseModifier(),
        ],
    )
    source = qb.QuantumCircuit(3)
    source.append(operation, [0, 1, 2])
    if format == "qpy":
        restored = qpy_loads(qpy_dumps(source))[0]
    else:
        from quantumbridge.compat.qiskit_adapter import circuit_from_ir
        from quantumbridge.ir.qb_ir import IRProgram

        restored = circuit_from_ir(IRProgram.from_json(source.to_ir().to_json()))
    assert tuple(p.uuid for p in restored.parameters) == tuple(
        p.uuid for p in source.parameters
    )
    owned = restored.operations[0].metadata["annotated_operation"]
    assert [type(m) for m in owned.modifiers] == [
        qb.PowerModifier,
        qb.ControlModifier,
        qb.InverseModifier,
    ]
    node = QNode.from_circuit(restored, qb.PauliZ(2), max_diff=2)
    point = np.array([7.3]) if format == "qpy" else np.array([0.5, 7.3])
    w = 7.3 - 4 * np.pi
    assert node(point) == pytest.approx(np.cos(0.5 * w), abs=4e-12)
    np.testing.assert_allclose(
        node.compute_jacobian(point),
        -np.sin(0.5 * w) * (np.array([0.5]) if format == "qpy" else np.array([w, 0.5])),
        atol=6e-11,
        rtol=0,
    )


def test_qpy13_rejects_symbolic_modifier_exponent_without_lossy_coercion():
    from quantumbridge.serialization.errors import (
        UnsupportedFeature as UnsupportedFormat,
    )

    a, p = qb.Parameter("a"), qb.Parameter("p")
    source = qb.QuantumCircuit(2)
    source.append(qb.AnnotatedOperation(CRYGate(p), qb.PowerModifier(a)), [0, 1])
    before = source.to_ir().to_json()
    with pytest.raises(UnsupportedFormat, match="float64 field"):
        qpy_dumps(source)
    assert source.to_ir().to_json() == before
