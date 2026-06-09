# This file is independently implemented for QuantumBridge SDK.
# No source code from Qiskit or PennyLane was copied.

import pytest

from quantumbridge.compat.pennylane_full.tape_adapter import describe_tape, tape_to_operation_metadata, tape_to_quantumbridge_ir

qml = pytest.importorskip("pennylane", reason="optional dependency unavailable: pennylane")


def test_pennylane_tape_adapter_extracts_metadata_and_ir():
    tape = qml.tape.QuantumScript([qml.Hadamard(0), qml.CNOT([0, 1])], [qml.probs(wires=[0, 1])])
    assert describe_tape(tape)["operation_count"] == 2
    assert len(tape_to_operation_metadata(tape)) == 2
    ir = tape_to_quantumbridge_ir(tape)
    assert ir["ecosystem"] == "pennylane"
    assert [op["op"] for op in ir["operations"]] == ["h", "cx"]
