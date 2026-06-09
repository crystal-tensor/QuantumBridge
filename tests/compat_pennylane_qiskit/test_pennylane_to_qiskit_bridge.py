# This file is independently implemented for QuantumBridge SDK.
# No source code from Qiskit, PennyLane, or PennyLane-Qiskit was copied.

from quantumbridge.compat.pennylane_qiskit import (
    bridge_ir_to_qiskit_circuit,
    pennylane_operations_to_bridge_ir,
    run_pennylane_to_qiskit_bridge,
)


def test_pennylane_operations_convert_to_qiskit_circuit():
    operations = [
        {"operation": "Hadamard", "wires": [0]},
        {"operation": "CNOT", "wires": [0, 1]},
    ]
    ir = pennylane_operations_to_bridge_ir(operations)
    circuit = bridge_ir_to_qiskit_circuit(ir)
    assert circuit.num_qubits == 2
    assert [item.operation.name for item in circuit.data] == ["h", "cx"]


def test_pennylane_operations_bridge_runs_native():
    result = run_pennylane_to_qiskit_bridge(
        [{"operation": "Hadamard", "wires": [0]}, {"operation": "CNOT", "wires": [0, 1]}],
        shots=64,
        seed=7,
    )
    assert result.validate() is True
    assert result.production_ready is False
    assert result.converted_target["operations"] == ["h", "cx"]
    assert set(result.statevector_probabilities) == {"00", "11"}
