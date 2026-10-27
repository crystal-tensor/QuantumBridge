# Copyright 2026 QuantumBridge Contributors. Apache-2.0.
"""Adjacent existing controlled gates must use the public append contract."""

import numpy as np
import pytest

import quantumbridge as qb
from quantumbridge.core.standard_gates import CHGate, CSwapGate
from test_quantumcircuit_unitary_public_abi import asymmetric_unitary, apply_local


@pytest.mark.parametrize("name,kind,wires", [("ch", CHGate, (0, 2)),
    ("cswap", CSwapGate, (2, 0, 3))])
def test_inherited_controlled_fixed_gate_public_invocation(name, kind, wires, record_property):
    circuit = qb.QuantumCircuit(4)
    # The default invocation was already exposed by inheritance before the fix.
    before = circuit.to_ir().to_json()
    try:
        result = getattr(circuit, name)(*wires)
    finally:
        record_property("store_changed_before_success_or_error", str(before != circuit.to_ir().to_json()))
    assert len(result.instructions) == len(circuit.data) == 1
    assert type(result.instructions[0]) is kind
    assert result.instructions[0] is circuit.data[0].operation
    np.testing.assert_allclose(qb.StatevectorDevice().statevector(circuit), np.eye(16)[:, 0], atol=2e-12, rtol=0)


@pytest.mark.parametrize("name,kind,wires", [("ch", CHGate, (0, 2)),
    ("cswap", CSwapGate, (2, 0, 3))])
@pytest.mark.parametrize("state", [0, 1])
def test_adjacent_controlled_labels_open_control_and_broadcast(name, kind, wires, state):
    circuit = qb.QuantumCircuit(4)
    circuit.x(0)
    circuit.h(2)
    initial = qb.StatevectorDevice().statevector(circuit)
    returned = getattr(circuit, name)(*wires, label="controlled", ctrl_state=state)
    expected = apply_local(initial, kind(ctrl_state=state).to_matrix(), wires, 4)
    assert returned.instructions[0].label == "controlled"
    assert returned.instructions[0].ctrl_state == state
    np.testing.assert_allclose(qb.StatevectorDevice().statevector(circuit), expected, atol=2e-12, rtol=0)
    other = qb.QuantumCircuit(5)
    args = ([0, 1], 4) if name == "ch" else ([0, 1], [2, 3], [4, 4])
    result = getattr(other, name)(*args)
    assert len(result) == len(other.operations) == len(other.data) == 2


@pytest.mark.parametrize("frame", ["loose-bits", "register"])
def test_public_unitary_existing_bit_register_identity_and_metadata(frame):
    register = qb.QuantumRegister(2, "shared")
    loose = qb.Qubit()
    circuit = qb.QuantumCircuit(register, [loose], metadata={"owner": "unchanged"})
    operands = [loose, register[0]] if frame == "loose-bits" else register
    indices = [2, 0] if frame == "loose-bits" else [0, 1]
    matrix = asymmetric_unitary(2)
    handle = circuit.unitary(matrix, operands, label="framed")
    assert circuit.data[0].qubits == tuple(operands)
    assert [circuit.find_bit(bit).index for bit in circuit.data[0].qubits] == indices
    assert handle.instructions[0] is circuit.data[0].operation
    assert circuit.metadata == {"owner": "unchanged"}
    initial = np.eye(8)[:, 0].astype(complex)
    np.testing.assert_allclose(qb.StatevectorDevice().statevector(circuit),
        apply_local(initial, matrix, tuple(reversed(indices)), 3), atol=2e-12, rtol=0)
