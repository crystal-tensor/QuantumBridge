# This file is independently implemented for QuantumBridge SDK.
# No source code from Qiskit or PennyLane was copied.

import pytest

from quantumbridge.compat.contracts import UnsupportedCapability
from quantumbridge.compat.pennylane_full.qiskit_bridge import (
    pennylane_operations_to_quantumbridge_ir,
    quantumbridge_ir_to_qiskit_circuit,
)

qml = pytest.importorskip("pennylane", reason="optional dependency unavailable: pennylane")


def test_pennylane_qiskit_bridge_basic_gates_or_clear_unsupported():
    ir = pennylane_operations_to_quantumbridge_ir([qml.Hadamard(0), qml.CNOT([0, 1])])
    circuit = quantumbridge_ir_to_qiskit_circuit(ir)
    if isinstance(circuit, UnsupportedCapability):
        assert "Qiskit is not installed" in circuit.reason
    else:
        assert circuit.num_qubits == 2
