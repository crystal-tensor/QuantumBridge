# Copyright 2026 QuantumBridge Contributors. Apache-2.0.
"""Public unitary calls must reach the same native authoritative store."""

import inspect

import numpy as np
import pytest

import quantumbridge as qb


def asymmetric_unitary(width):
    rng = np.random.default_rng(2037 + width)
    dimension = 1 << width
    raw = rng.normal(size=(dimension, dimension)) + 1j * rng.normal(size=(dimension, dimension))
    matrix, triangular = np.linalg.qr(raw)
    phases = np.diag(triangular)
    return matrix * (phases / np.abs(phases)).conj()


@pytest.mark.parametrize("local_width", [1, 2])
def test_public_unitary_reaches_native_store_without_append_signature_failure(local_width, record_property):
    matrix = asymmetric_unitary(local_width)
    assert not np.allclose(matrix, matrix.T)
    native = qb.Circuit(local_width)
    assert native.unitary(matrix, list(range(local_width))) is native
    np.testing.assert_allclose(qb.StatevectorDevice().statevector(native),
        matrix[:, 0], atol=2e-12, rtol=0)
    circuit = qb.QuantumCircuit(local_width)
    before = circuit.to_ir().to_json()
    record_property("native_append_signature", str(inspect.signature(qb.Circuit.append)))
    record_property("public_append_signature", str(inspect.signature(qb.QuantumCircuit.append)))
    try:
        result = circuit.unitary(matrix, list(range(local_width)))
    finally:
        record_property("store_changed_before_success_or_error", str(circuit.to_ir().to_json() != before))
        record_property("actual_operation_count", len(circuit.operations))
    record_property("actual_return_type", type(result).__name__)
    assert len(circuit.operations) == len(circuit.data) == 1
    assert len(result.instructions) == 1


def apply_local(state, matrix, wires, width):
    axes = list(wires) + [wire for wire in range(width) if wire not in wires]
    tensor = np.transpose(state.reshape((2,) * width), axes)
    acted = matrix @ tensor.reshape(len(matrix), -1)
    return np.transpose(acted.reshape((2,) * width), np.argsort(axes)).reshape(-1)


@pytest.mark.parametrize("wires", [(2,), (3, 1), (0, 3)])
def test_public_unitary_complex_wire_math_phase_composition_inverse_and_owned_input(wires):
    from quantumbridge.core.standard_gates import UnitaryGate

    matrix = asymmetric_unitary(len(wires))
    stored = matrix.copy()
    circuit = qb.QuantumCircuit(4, global_phase=.23)
    circuit.h(1)
    initial = np.zeros(16, dtype=complex)
    initial[0] = initial[4] = 1 / np.sqrt(2)
    expected = apply_local(initial, stored, tuple(reversed(wires)), 4) * np.exp(.23j)
    returned = circuit.unitary(matrix, list(wires), label="asymmetric-local")
    context = circuit.data[-1]
    assert type(context.operation) is UnitaryGate
    assert returned.instructions[0] is context.operation
    assert context.operation.label == "asymmetric-local"
    assert tuple(circuit.find_bit(bit).index for bit in context.qubits) == wires
    np.testing.assert_array_equal(context.operation.to_matrix(), stored)
    matrix[:] = 0
    # Preserve the established native owned-matrix contract, not SDK aliasing.
    for body in (circuit, circuit.copy(), circuit.decompose()):
        np.testing.assert_allclose(qb.StatevectorDevice().statevector(body), expected, atol=2e-12, rtol=0)
        np.testing.assert_allclose(qb.MatrixProductStateDevice(cutoff=0, max_bond_dim=16)
            .matrix_product_state(body).statevector(), expected, atol=2e-12, rtol=0)
    restored = circuit.compose(circuit.inverse())
    np.testing.assert_allclose(qb.StatevectorDevice().statevector(restored), np.eye(16)[:, 0], atol=2e-12, rtol=0)
    assert len(circuit.operations) == len(circuit.data) == 2


@pytest.mark.parametrize("kind", ["shape", "nonunitary", "duplicate", "range", "dtype"])
def test_public_unitary_rejection_is_atomic_and_circuit_recovers(kind):
    circuit = qb.QuantumCircuit(2)
    circuit.h(0)
    before = circuit.to_ir().to_json()
    matrix = {"shape": np.eye(3), "nonunitary": np.zeros((4, 4)),
        "dtype": [["not-a-number", 0], [0, 1]]}.get(kind, np.eye(4))
    wires = [0, 0] if kind == "duplicate" else [0, 2] if kind == "range" else [0, 1]
    with pytest.raises((ValueError, TypeError, IndexError)):
        circuit.unitary(matrix, wires)
    assert circuit.to_ir().to_json() == before
    circuit.unitary(asymmetric_unitary(1), [1])
    assert len(circuit.data) == 2


def test_public_unitary_resource_refusal_precedes_append():
    from quantumbridge.execution.resource_context import ResourceScope
    from quantumbridge.execution.resource_ledger import UnifiedResourceLedger
    from quantumbridge.execution.resource_limits import UnifiedExecutionLimits

    circuit = qb.QuantumCircuit(1)
    before = circuit.to_ir().to_json()
    ledger = UnifiedResourceLedger(UnifiedExecutionLimits(max_total_memory_bytes=63))
    with ResourceScope(ledger), pytest.raises(MemoryError):
        circuit.unitary(asymmetric_unitary(1), [0])
    assert circuit.to_ir().to_json() == before
    assert ledger.receipt()["live_memory_bytes"] == 0


@pytest.mark.parametrize("form", ["gate", "operator"])
def test_public_unitary_accepts_existing_native_matrix_owner_forms(form):
    from quantumbridge.core.standard_gates import UnitaryGate
    from quantumbridge.information import Operator

    matrix = asymmetric_unitary(2)
    owner = UnitaryGate(matrix) if form == "gate" else Operator(matrix)
    circuit = qb.QuantumCircuit(2)
    returned = circuit.unitary(owner, [0, 1], label="from-owner")
    assert len(returned) == len(circuit.data) == 1
    np.testing.assert_allclose(qb.StatevectorDevice().statevector(circuit),
        apply_local(np.eye(4)[:, 0], matrix, (1, 0), 2), atol=2e-12, rtol=0)
    np.testing.assert_array_equal(circuit.data[0].operation.to_matrix(), matrix)
