# Copyright 2026 QuantumBridge Contributors.
# Licensed under the Apache License, Version 2.0.
# This file is part of QuantumBridge SDK.
# This implementation is developed for the QuantumBridge native architecture.

import pytest

from quantumbridge import Circuit, circuit_from_openqasm


def test_qasm_roundtrip_strict_structure():
    circuit = Circuit(2, 2).h(0).ry(0.25, 1).cx(0, 1).measure(0, 0).measure(1, 1)
    imported = circuit_from_openqasm(circuit.to_openqasm())
    assert imported.num_qubits == 2
    assert imported.num_bits == 2
    assert [op.name for op in imported.operations] == ["h", "ry", "cx"]
    assert imported.operations[1].params == (0.25,)
    assert [(m.wire, m.bit) for m in imported.measurements] == [(0, 0), (1, 1)]


def test_qasm_import_rejects_unsupported_syntax_with_clear_error():
    text = "OPENQASM 2.0;\nqreg q[1];\nu3(0,0,0) q[0];\n"
    with pytest.raises(ValueError, match="does not support line"):
        circuit_from_openqasm(text)
