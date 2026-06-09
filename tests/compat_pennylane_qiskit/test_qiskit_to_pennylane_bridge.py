# This file is independently implemented for QuantumBridge SDK.
# No source code from Qiskit, PennyLane, or PennyLane-Qiskit was copied.

import pytest

from quantumbridge.compat.pennylane_qiskit import (
    qiskit_circuit_to_bridge_ir,
    qiskit_circuit_to_pennylane_spec,
    run_qiskit_to_pennylane_bridge,
)

qiskit = pytest.importorskip("qiskit", reason="optional dependency unavailable: qiskit")


def test_qiskit_h_circuit_converts_to_pennylane_spec():
    circuit = qiskit.QuantumCircuit(1, 1)
    circuit.h(0)
    circuit.measure(0, 0)
    spec = qiskit_circuit_to_pennylane_spec(circuit)
    assert spec["ecosystem"] == "pennylane"
    assert [op["operation"] for op in spec["operations"]] == ["Hadamard"]
    assert spec["cloud_access"] is False


def test_qiskit_bell_bridge_runs_native():
    circuit = qiskit.QuantumCircuit(2, 2)
    circuit.h(0)
    circuit.cx(0, 1)
    circuit.measure(0, 0)
    circuit.measure(1, 1)
    ir = qiskit_circuit_to_bridge_ir(circuit)
    result = run_qiskit_to_pennylane_bridge(circuit, shots=64, seed=7)
    assert ir.num_qubits == 2
    assert result.validate() is True
    assert result.production_ready is False
    assert result.converted_target["operations"][1]["operation"] == "CNOT"
    assert set(result.statevector_probabilities) == {"00", "11"}
