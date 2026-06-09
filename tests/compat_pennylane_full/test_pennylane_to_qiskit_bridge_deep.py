# This file is independently implemented for QuantumBridge SDK.
# No source code from Qiskit or PennyLane was copied.

import pytest

from quantumbridge.compat.contracts import UnsupportedCapability
from quantumbridge.compat.pennylane_full.qiskit_bridge import (
    pennylane_tape_to_qiskit_circuit,
    pennylane_tape_to_quantumbridge_ir,
    qiskit_circuit_to_basic_pennylane_spec,
)

qml = pytest.importorskip("pennylane", reason="optional dependency unavailable: pennylane")


def test_pennylane_tape_to_qiskit_circuit_basic_gates():
    tape = qml.tape.QuantumScript([qml.Hadamard(0), qml.CNOT(wires=[0, 1]), qml.RZ(0.2, wires=1)], [])
    ir = pennylane_tape_to_quantumbridge_ir(tape)
    assert [op["op"] for op in ir["operations"]] == ["h", "cx", "rz"]
    circuit = pennylane_tape_to_qiskit_circuit(tape)
    if isinstance(circuit, UnsupportedCapability):
        assert "Qiskit is not installed" in circuit.reason
    else:
        assert circuit.num_qubits == 2
        assert [item.operation.name for item in circuit.data] == ["h", "cx", "rz"]


def test_qiskit_circuit_to_basic_pennylane_spec_when_qiskit_installed():
    qiskit = pytest.importorskip("qiskit", reason="optional dependency unavailable: qiskit")
    circuit = qiskit.QuantumCircuit(2)
    circuit.h(0)
    circuit.cx(0, 1)
    spec = qiskit_circuit_to_basic_pennylane_spec(circuit)
    assert spec["ecosystem"] == "pennylane"
    assert [op["operation"] for op in spec["operations"]] == ["Hadamard", "CNOT"]
