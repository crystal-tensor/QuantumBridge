# Copyright 2026 QuantumBridge Contributors. Apache-2.0.
"""Explicit installed-public-API observations, not copied SDK implementation."""

import inspect
import json

import numpy as np
import pytest


@pytest.mark.parametrize("local_width", [1, 2])
def test_installed_public_unitary_signature_storage_and_return(local_width, record_property):
    import qiskit
    from qiskit import QuantumCircuit

    rng = np.random.default_rng(2037 + local_width)
    dimension = 1 << local_width
    raw = rng.normal(size=(dimension, dimension)) + 1j * rng.normal(size=(dimension, dimension))
    matrix, _ = np.linalg.qr(raw)
    circuit = QuantumCircuit(4, global_phase=.23)
    wires = [3] if local_width == 1 else [3, 1]
    returned = circuit.unitary(matrix, wires, label="complex-local")
    context = circuit.data[0]
    record = dict(version=qiskit.__version__, origin=qiskit.__file__,
        signature=str(inspect.signature(QuantumCircuit.unitary)),
        return_type=type(returned).__name__, operation_type=type(context.operation).__name__,
        label=context.operation.label, wires=[circuit.find_bit(bit).index for bit in context.qubits],
        instruction_reference=returned.instructions[0] is context.operation,
        global_phase=float(circuit.global_phase), operations=len(circuit.data))
    assert record["return_type"] == "InstructionSet"
    assert record["wires"] == wires
    assert record["label"] == "complex-local"
    assert record["instruction_reference"] and record["operations"] == 1
    np.testing.assert_allclose(context.operation.to_matrix(), matrix, atol=0, rtol=0)
    matrix[0, 0] += .125
    record["caller_mutation_changes_gate"] = np.array_equal(context.operation.to_matrix(), matrix)
    record_property("public_observation", json.dumps(record, sort_keys=True))


@pytest.mark.parametrize("kind", ["shape", "nonunitary", "duplicate", "range", "dtype"])
def test_installed_public_unitary_invalid_input_atomicity(kind, record_property):
    from qiskit import QuantumCircuit

    circuit = QuantumCircuit(2)
    matrix = {"shape": np.eye(3), "nonunitary": np.zeros((4, 4)),
        "dtype": [["not-a-number", 0], [0, 1]]}.get(kind, np.eye(4))
    wires = [0, 0] if kind == "duplicate" else [0, 2] if kind == "range" else [0, 1]
    try:
        circuit.unitary(matrix, wires)
    except Exception as error:
        record_property("exception_type", type(error).__name__)
        record_property("exception_message", str(error))
    else:
        pytest.fail("Public SDK accepted this invalid unitary invocation")
    assert len(circuit.data) == 0


@pytest.mark.parametrize("form", ["gate", "operator"])
def test_installed_public_unitary_accepts_native_owner_counterparts(form, record_property):
    from qiskit import QuantumCircuit
    from qiskit.circuit.library import UnitaryGate
    from qiskit.quantum_info import Operator

    matrix = np.diag([1., 1j, -1., -1j])
    obj = UnitaryGate(matrix) if form == "gate" else Operator(matrix)
    circuit = QuantumCircuit(2)
    result = circuit.unitary(obj, [1, 0], label="owner")
    assert type(result).__name__ == "InstructionSet"
    np.testing.assert_array_equal(circuit.data[0].operation.to_matrix(), matrix)
    record_property("accepted_input_type", type(obj).__name__)


@pytest.mark.parametrize("name,wires", [("ch", (0, 2)), ("cswap", (2, 0, 3))])
def test_installed_public_adjacent_controlled_fixed_signature(name, wires, record_property):
    from qiskit import QuantumCircuit

    circuit = QuantumCircuit(4)
    result = getattr(circuit, name)(*wires, label="adjacent", ctrl_state=0)
    assert type(result).__name__ == "InstructionSet"
    assert circuit.data[0].operation.ctrl_state == 0
    assert circuit.data[0].operation.label == "adjacent"
    record_property("signature", str(inspect.signature(getattr(QuantumCircuit, name))))
    record_property("operation_type", type(circuit.data[0].operation).__name__)


@pytest.mark.parametrize("frame", ["loose-bits", "register"])
def test_installed_public_unitary_bit_logical_identity(frame, record_property):
    from qiskit import QuantumCircuit, QuantumRegister
    from qiskit.circuit import Qubit

    register, loose = QuantumRegister(2, "shared"), Qubit()
    circuit = QuantumCircuit(register, [loose])
    operands = [loose, register[0]] if frame == "loose-bits" else register
    supplied = list(operands)
    circuit.unitary(np.diag([1., 1j, -1., -1j]), operands)
    actual = circuit.data[0].qubits
    assert actual == tuple(supplied)
    record_property("python_identity", str([a is b for a, b in zip(actual, supplied)]))
    record_property("logical_identity", str([a == b for a, b in zip(actual, supplied)]))
