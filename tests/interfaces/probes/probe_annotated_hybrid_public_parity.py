# Copyright 2026 QuantumBridge Contributors. Apache-2.0.
"""Open raw-controlled annotation parity with independent three-basis math."""

from itertools import product

import numpy as np
import pytest

import quantumbridge as qb
from quantumbridge.core.standard_gates import UnitaryGate


def hybrid_index(controls, targets):
    return sum(bit << (len(controls) - 1 - i) for i, bit in enumerate(controls)) * (1 << len(targets)) \
        + sum(bit << i for i, bit in enumerate(targets))


def public_index(controls, targets):
    return sum(bit << i for i, bit in enumerate((*controls, *targets)))


def native_index(controls, targets):
    bits = (*controls, *targets)
    return sum(bit << (len(bits) - 1 - i) for i, bit in enumerate(bits))


def convert(data, controls, targets, index):
    pairs = [(hybrid_index(c, t), index(c, t))
        for c in product((0, 1), repeat=controls) for t in product((0, 1), repeat=targets)]
    assert sorted(a for a, _ in pairs) == sorted(b for _, b in pairs) == list(range(len(data)))
    result = np.empty_like(data)
    for row, target_row in pairs:
        for column, target_column in pairs:result[target_row, target_column] = data[row, column]
    return result


def raw_matrix(width):
    rng = np.random.default_rng(12440 + width)
    size = 1 << width
    vectors, _ = np.linalg.qr(rng.normal(size=(size, size)) + 1j * rng.normal(size=(size, size)))
    return vectors @ np.diag(np.exp(1j * (.17 + np.linspace(.1, .6, size)))) @ vectors.conj().T


def independent_modifiers(matrix, modifiers):
    data = matrix.copy()
    for kind, value, state in modifiers:
        if kind == "inverse":data = data.conj().T
        elif kind == "power":
            if float(value).is_integer():data = np.linalg.matrix_power(data, int(value))
            else:
                values, vectors = np.linalg.eig(data)
                data = vectors @ np.diag(np.exp(value * 1j * np.angle(values))) @ np.linalg.inv(vectors)
        else:
            control = sum(((state >> i) & 1) << (value - 1 - i) for i in range(value))
            result = np.eye(len(data) * (1 << value), dtype=complex)
            start = control * len(data)
            result[start:start + len(data), start:start + len(data)] = data
            data = result
    return data


@pytest.mark.parametrize("targets", [1, 2])
@pytest.mark.parametrize("controls", [1, 2])
@pytest.mark.parametrize("opened", [False, True])
@pytest.mark.parametrize("order", ["control", "inverse_control", "control_inverse",
    "fractional_control", "control_fractional", "integer_control", "control_integer"])
def test_raw_controlled_annotation_has_public_and_native_physical_coordinates(targets, controls, opened, order):
    from qiskit.circuit.library import UnitaryGate as QU
    from qiskit.circuit import AnnotatedOperation as QA, InverseModifier as QI, PowerModifier as QP, ControlModifier as QC
    matrix = raw_matrix(targets)
    state = 0 if opened else (1 << controls) - 1
    control = ("control", controls, state)
    extra = ("inverse", None, None) if "inverse" in order else ("power", .37 if "fractional" in order else 2, None)
    modifiers = [control] if order == "control" else [control, extra] if order.startswith("control_") else [extra, control]
    native_mods = [qb.InverseModifier() if kind == "inverse" else qb.PowerModifier(value) if kind == "power"
        else qb.ControlModifier(value, selected) for kind, value, selected in modifiers]
    public_mods = [QI() if kind == "inverse" else QP(value) if kind == "power"
        else QC(value, selected) for kind, value, selected in modifiers]
    actual = qb.AnnotatedOperation(UnitaryGate(matrix), native_mods).to_matrix()
    hybrid = independent_modifiers(matrix, modifiers)
    np.testing.assert_allclose(actual.data, hybrid, atol=8e-13, rtol=0)
    expected = convert(hybrid, controls, targets, public_index)
    reference = QA(QU(matrix), public_mods).to_matrix().data
    np.testing.assert_allclose(reference, expected, atol=8e-13, rtol=0)
    # These are open end-state assertions, not expected-failure decorations.
    np.testing.assert_allclose(actual.as_qiskit_operator().data, expected, atol=8e-13, rtol=0)
    np.testing.assert_allclose(actual.as_native_operator().data,
        convert(hybrid, controls, targets, native_index), atol=8e-13, rtol=0)


@pytest.mark.parametrize("targets", [1, 2])
def test_nested_raw_annotation_controls_preserve_ordered_basis_and_all_complex_entries(targets):
    from qiskit.circuit.library import UnitaryGate as QU
    from qiskit.circuit import AnnotatedOperation as QA, InverseModifier as QI, PowerModifier as QP, ControlModifier as QC
    matrix = raw_matrix(targets)
    inner = qb.AnnotatedOperation(UnitaryGate(matrix), [qb.ControlModifier(1, 0), qb.InverseModifier()])
    outer = qb.AnnotatedOperation(inner, [qb.PowerModifier(.37), qb.ControlModifier(1, 1)])
    public_inner = QA(QU(matrix), [QC(1, 0), QI()])
    reference = QA(public_inner, [QP(.37), QC(1, 1)]).to_matrix().data
    hybrid = independent_modifiers(matrix, [("control", 1, 0), ("inverse", None, None),
        ("power", .37, None), ("control", 1, 1)])
    operator = outer.to_matrix()
    np.testing.assert_allclose(operator.data, hybrid, atol=8e-13, rtol=0)
    expected = convert(hybrid, 2, targets, public_index)
    np.testing.assert_allclose(reference, expected, atol=8e-13, rtol=0)
    np.testing.assert_allclose(operator.as_qiskit_operator().data, expected, atol=8e-13, rtol=0)


@pytest.mark.parametrize("entry", ["unitary", "append"])
@pytest.mark.parametrize("path", ["source", "compiler", "json_ir", "qpy13", "detached_json_ir", "detached_qpy13"])
@pytest.mark.parametrize("order", ["inverse_control", "control_inverse", "control_fractional"])
def test_hybrid_constructor_public_execution_and_standard_matrix_transport(entry, path, order):
    from qiskit import QuantumCircuit
    from qiskit.quantum_info import Statevector as QS
    from qiskit.circuit.library import UnitaryGate as QU
    from qiskit.circuit import AnnotatedOperation as QA, InverseModifier as QI, PowerModifier as QP, ControlModifier as QC
    from quantumbridge.information import Operator
    from quantumbridge.compat.qiskit_adapter import circuit_from_ir
    from quantumbridge.ir.qb_ir import IRProgram
    from quantumbridge.serialization import qpy_dumps, qpy_loads
    matrix = raw_matrix(2)
    native_mods, public_mods = {
        "inverse_control": ([qb.InverseModifier(), qb.ControlModifier(1, 0)], [QI(), QC(1, 0)]),
        "control_inverse": ([qb.ControlModifier(1, 0), qb.InverseModifier()], [QC(1, 0), QI()]),
        "control_fractional": ([qb.ControlModifier(1, 0), qb.PowerModifier(.37)], [QC(1, 0), QP(.37)]),
    }[order]
    operator = Operator(qb.AnnotatedOperation(UnitaryGate(matrix), native_mods))
    expected_operator = QA(QU(matrix), public_mods).to_matrix()
    actual, reference = qb.QuantumCircuit(5, global_phase=.23), QuantumCircuit(5, global_phase=.23)
    for circuit in (actual, reference):
        circuit.h(0)
        circuit.h(4)
        circuit.ry(.31, 1)
        circuit.rx(-.43, 3)
    wires = [4, 1, 3]
    if entry == "unitary":
        actual.unitary(operator, wires, label="hybrid-source")
        reference.unitary(expected_operator, wires, label="hybrid-source")
    else:
        actual.append(UnitaryGate(operator.as_qiskit_operator().data), wires)
        reference.append(QU(expected_operator.data), wires)
    if path == "compiler":actual = qb.transpile(actual, basis_gates=["h", "rx", "ry", "rz", "sx", "cx", "unitary"], optimization_level=1)
    elif "json_ir" in path:
        payload = actual.to_ir().to_json()
        assert "_literal_target_width" not in payload
        actual = circuit_from_ir(IRProgram.from_json(payload))
    elif "qpy13" in path:
        payload = qpy_dumps(actual, version=13)
        assert b"_literal_target_width" not in payload
        actual = qpy_loads(payload)[0]
    if path.startswith("detached"):
        owner = actual.operations[-1].metadata["gate"]
        actual = qb.QuantumCircuit(5, global_phase=.23)
        actual.h(0)
        actual.h(4)
        actual.ry(.31, 1)
        actual.rx(-.43, 3)
        actual.append(owner, wires)
    order_indices = [int(format(i, "05b")[::-1], 2) for i in range(32)]
    expected = QS.from_instruction(reference).data[order_indices]
    np.testing.assert_allclose(qb.StatevectorDevice().statevector(actual), expected, atol=9e-13, rtol=0)
    np.testing.assert_allclose(qb.MatrixProductStateDevice(cutoff=0, max_bond_dim=32)
        .matrix_product_state(actual).statevector(), expected, atol=9e-13, rtol=0)
