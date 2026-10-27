# Copyright 2026 QuantumBridge Contributors. Apache-2.0.
"""Physical matrix ordering must survive existing owner derivation paths."""

import numpy as np
import pytest

import quantumbridge as qb
from quantumbridge.compat.qiskit_adapter import circuit_from_ir
from quantumbridge.serialization import qpy_dumps, qpy_loads


def matrix_source():
    rng = np.random.default_rng(5041)
    basis, _ = np.linalg.qr(rng.normal(size=(4, 4)) + 1j * rng.normal(size=(4, 4)))
    phases = np.array([.17, -.43, 1.21, -1.62])
    return basis @ np.diag(np.exp(1j * phases)) @ basis.conj().T, basis, phases


def apply_local(vector, matrix, wires, width):
    axes = list(wires) + [wire for wire in range(width) if wire not in wires]
    value = matrix @ vector.reshape((2,) * width).transpose(axes).reshape(len(matrix), -1)
    return value.reshape((2,) * width).transpose(np.argsort(axes)).reshape(-1)


DERIVATIONS = ("source", "copy", "inverse", "repeat", "integer_power", "fractional_power",
    "annotated_inverse", "annotated_power", "open_control", "closed_control", "annotated_control")


def derived_owner(owner, kind):
    if kind == "source": return owner
    if kind == "copy": return owner.copy()
    if kind == "inverse": return owner.inverse()
    if kind == "repeat": return owner.repeat(2)
    if kind == "integer_power": return owner.power(2)
    if kind == "fractional_power": return owner.power(.37)
    if kind == "annotated_inverse": return qb.AnnotatedOperation(owner, qb.InverseModifier())
    if kind == "annotated_power": return qb.AnnotatedOperation(owner, qb.PowerModifier(.37))
    return owner.control(1, ctrl_state=0 if kind == "open_control" else 1,
        annotated=kind == "annotated_control")


@pytest.mark.parametrize("kind", DERIVATIONS)
@pytest.mark.parametrize("path", ["source", "decompose", "ir", "qpy13"])
def test_public_matrix_owner_derivations_keep_physical_math_and_source(kind, path):
    matrix, basis, phases = matrix_source()
    factory = qb.QuantumCircuit(2)
    factory.unitary(matrix, [0, 1], label="public-matrix")
    owner = factory.data[0].operation
    derived = derived_owner(owner, kind)
    expected_matrix = matrix
    if kind in ("inverse", "annotated_inverse"): expected_matrix = matrix.conj().T
    if kind in ("repeat", "integer_power"): expected_matrix = matrix @ matrix
    if kind in ("fractional_power", "annotated_power"):
        expected_matrix = basis @ np.diag(np.exp(.37j * phases)) @ basis.conj().T
    controlled = "control" in kind
    if controlled:
        block = np.eye(8, dtype=complex)
        state = 0 if kind == "open_control" else 1
        block[4 * state:4 * state + 4, 4 * state:4 * state + 4] = expected_matrix
        expected_matrix = block
    source = qb.QuantumCircuit(5, global_phase=.23)
    source.h(0)
    source.ry(.51, 1)
    source.ry(-.74, 4)
    source.append(derived, [4, 3, 1] if controlled else [3, 1])
    source.cx(0, 2)
    initial = np.zeros(32, complex)
    initial[0] = 1
    initial = apply_local(initial, np.array([[1, 1], [1, -1]]) / np.sqrt(2), [0], 5)
    for wire, angle in ((1, .51), (4, -.74)):
        initial = apply_local(initial, np.array([[np.cos(angle / 2), -np.sin(angle / 2)],
            [np.sin(angle / 2), np.cos(angle / 2)]]), [wire], 5)
    expected = apply_local(initial, expected_matrix, [4, 1, 3] if controlled else [1, 3], 5)
    expected = apply_local(expected, np.array([[1, 0, 0, 0], [0, 1, 0, 0],
        [0, 0, 0, 1], [0, 0, 1, 0]]), [0, 2], 5) * np.exp(.23j)
    if path == "source": restored = source
    elif path == "decompose": restored = source.decompose(reps=2)
    elif path == "ir": restored = circuit_from_ir(source.to_ir())
    else: restored = qpy_loads(qpy_dumps(source, version=13))[0]
    np.testing.assert_allclose(qb.StatevectorDevice().statevector(restored), expected, atol=3e-12, rtol=0)
    np.testing.assert_allclose(qb.MatrixProductStateDevice(cutoff=0, max_bond_dim=32)
        .matrix_product_state(restored).statevector(), expected, atol=3e-12, rtol=0)
    np.testing.assert_array_equal(owner.to_matrix(), matrix)
    np.testing.assert_array_equal(factory.data[0].operation.to_matrix(), matrix)
    assert factory.data[0].operation is owner and owner.label == "public-matrix"
    assert tuple(source.find_bit(bit).index for bit in source.data[3].qubits) == (
        (4, 3, 1) if controlled else (3, 1))


@pytest.mark.parametrize("local_width", [1, 2])
def test_native_primitive_matrix_retains_q0_first_math_through_standard_qpy(local_width):
    matrix = matrix_source()[0] if local_width == 2 else np.array([[1, 1j], [1j, 1]]) / np.sqrt(2)
    source = qb.Circuit(4)
    source.h(0)
    source.ry(.3, 1)
    wires = [3] if local_width == 1 else [3, 1]
    assert source.unitary(matrix, wires) is source
    expected = qb.StatevectorDevice().statevector(source)
    payload = qpy_dumps(source, version=13)
    assert b"_public_matrix_basis" not in payload
    restored = qpy_loads(payload)[0]
    np.testing.assert_allclose(qb.StatevectorDevice().statevector(restored), expected, atol=3e-12, rtol=0)


def test_public_matrix_resolution_is_idempotent_and_live_owned_parameter_changes_are_not_stale():
    from quantumbridge.core.operations import execution_operation

    source = qb.QuantumCircuit(2)
    matrix, _, _ = matrix_source()
    source.unitary(matrix, [0, 1])
    first = execution_operation(source.operations[0])
    assert execution_operation(first) is first
    expected = apply_local(np.eye(4)[:, 0], matrix, [1, 0], 2)
    np.testing.assert_allclose(qb.StatevectorDevice().statevector(source), expected, atol=3e-12, rtol=0)
    source.data[0].operation.params = [matrix.conj().T]
    expected = apply_local(np.eye(4)[:, 0], matrix.conj().T, [1, 0], 2)
    np.testing.assert_allclose(qb.StatevectorDevice().statevector(source), expected, atol=3e-12, rtol=0)
    assert source.data[0].operation.label is None and len(source.data) == 1


def test_bad_raw_public_definition_width_rejects_before_matrix_allocation(monkeypatch):
    from quantumbridge.core.operations import Operation, execution_operation
    import quantumbridge.execution.array_reservations as reservations

    operation = Operation("unitary", (0,), metadata={"matrix": np.eye(4)})
    object.__setattr__(operation, "_public_matrix_basis", "little")
    def forbidden(*args, **kwargs): pytest.fail("Invalid matrix frame allocated a numeric snapshot")
    monkeypatch.setattr(reservations, "numeric_array", forbidden)
    with pytest.raises(ValueError, match="width"):
        execution_operation(operation)


def test_native_matrix_qpy_numeric_admission_precedes_owned_copy(monkeypatch):
    from quantumbridge.serialization import SerializationLimits, ResourceLimitError
    import quantumbridge.execution.array_reservations as reservations

    source = qb.Circuit(2).unitary(matrix_source()[0], [0, 1])
    def forbidden(*args, **kwargs): pytest.fail("QPY numeric limit preceded by an owned copy")
    monkeypatch.setattr(reservations, "numeric_array", forbidden)
    with pytest.raises(ResourceLimitError, match="max_numeric_elements"):
        qpy_dumps(source, version=13, limits=SerializationLimits(max_numeric_elements=15))
