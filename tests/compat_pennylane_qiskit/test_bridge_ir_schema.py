# This file is independently implemented for QuantumBridge SDK.
# No source code from Qiskit, PennyLane, or PennyLane-Qiskit was copied.

from quantumbridge.compat.pennylane_qiskit import (
    bridge_ir_summary,
    pennylane_qnode_metadata_to_bridge_ir,
    pennylane_tape_to_bridge_ir,
)


def test_bridge_ir_validates_for_tape_dict():
    tape = {"operations": [{"operation": "RX", "wires": [0], "parameters": [0.25]}]}
    ir = pennylane_tape_to_bridge_ir(tape)
    summary = bridge_ir_summary(ir)
    assert ir.num_qubits == 1
    assert summary.validate() is True
    assert summary.converted_ir["instructions"][0]["op"] == "rx"


def test_qnode_metadata_converts_to_bridge_ir():
    metadata = {"num_qubits": 2, "operations": [{"operation": "CNOT", "wires": [0, 1]}]}
    ir = pennylane_qnode_metadata_to_bridge_ir(metadata)
    assert ir.num_qubits == 2
    assert ir.instructions[0].op == "cx"
