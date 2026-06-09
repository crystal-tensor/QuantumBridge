# This file is independently implemented for QuantumBridge SDK.
# No source code from Qiskit or PennyLane was copied.

import pytest

from quantumbridge.compat.pennylane_full.tape_adapter import (
    quantumbridge_ir_to_tape_spec,
    tape_summary,
    tape_to_measurement_metadata,
    tape_to_quantumbridge_ir,
)

qml = pytest.importorskip("pennylane", reason="optional dependency unavailable: pennylane")


def test_tape_to_quantumbridge_ir_contains_stage8c_contract_fields():
    tape = qml.tape.QuantumScript([qml.Hadamard(0), qml.CNOT(wires=[0, 1])], [qml.probs(wires=[0, 1])])
    ir = tape_to_quantumbridge_ir(tape)
    assert ir["schema_version"] == "0.1"
    assert ir["ecosystem"] == "pennylane"
    assert ir["wires"] == [0, 1]
    assert [op["op"] for op in ir["operations"]] == ["h", "cx"]
    assert ir["measurements"][0]["measurement_type"] == "probs"
    assert ir["unsupported_operations"] == []


def test_tape_measurement_metadata_summary_and_reverse_spec():
    tape = qml.tape.QuantumScript([qml.PauliX(0)], [qml.expval(qml.PauliZ(0))])
    measurements = tape_to_measurement_metadata(tape)
    assert measurements[0]["measurement_type"] == "expval"
    summary = tape_summary(tape)
    assert summary["operation_count"] == 1
    spec = quantumbridge_ir_to_tape_spec(tape_to_quantumbridge_ir(tape))
    assert spec["metadata_only"] is True
    assert spec["operations"][0]["op"] == "x"
