# This file is independently implemented for QuantumBridge SDK.
# No source code from Qiskit or PennyLane was copied.

import pytest

from quantumbridge.compat.pennylane_full.operations_adapter import describe_operation, list_operations, operation_to_quantumbridge_ir_fragment

qml = pytest.importorskip("pennylane", reason="optional dependency unavailable: pennylane")


def test_pennylane_operations_adapter_describes_basic_gates():
    assert "Hadamard" in list_operations()
    assert describe_operation("Hadamard")["supported"] is True


def test_pennylane_operation_to_ir_fragment_basic_gate():
    fragment = operation_to_quantumbridge_ir_fragment(qml.CNOT(wires=[0, 1]))
    assert fragment["op"] == "cx"
    assert fragment["controls"] == [0]
    assert fragment["targets"] == [1]
