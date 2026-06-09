# This file is independently implemented for QuantumBridge SDK.
# No source code from Qiskit or PennyLane was copied.

import pytest

from quantumbridge.compat.pennylane_full.operations_adapter import (
    operation_sequence_to_quantumbridge_ir,
    operation_to_metadata,
    operation_to_quantumbridge_ir_fragment,
    quantumbridge_ir_fragment_to_pennylane_operation,
)

qml = pytest.importorskip("pennylane", reason="optional dependency unavailable: pennylane")


def test_operation_metadata_contains_stage8c_fields():
    metadata = operation_to_metadata(qml.RX(0.125, wires=0))
    assert metadata["name"] == "RX"
    assert metadata["wires"] == [0]
    assert metadata["parameters"] == [0.125]
    assert metadata["num_wires"] == 1
    assert metadata["num_params"] == 1
    assert metadata["capability_level"] == 2
    assert metadata["unsupported_reason"] is None


def test_operation_sequence_to_quantumbridge_ir_basic_gates():
    ir = operation_sequence_to_quantumbridge_ir([qml.Hadamard(0), qml.CNOT(wires=[0, 1])])
    assert ir["ecosystem"] == "pennylane"
    assert ir["wires"] == [0, 1]
    assert [op["op"] for op in ir["operations"]] == ["h", "cx"]
    assert ir["unsupported_operations"] == []


def test_ir_fragment_to_pennylane_lightweight_operation_spec():
    spec = quantumbridge_ir_fragment_to_pennylane_operation({"op": "cx", "controls": [0], "targets": [1]})
    assert spec["supported"] is True
    assert spec["operation"] == "CNOT"
    assert spec["wires"] == [0, 1]


def test_unsupported_operation_returns_structured_warning():
    fragment = operation_to_quantumbridge_ir_fragment(qml.Toffoli(wires=[0, 1, 2]))
    assert fragment["supported"] is False
    assert "Toffoli" in fragment["reason"]
