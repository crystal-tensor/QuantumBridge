# Copyright 2026 QuantumBridge Contributors.
# Licensed under the Apache License, Version 2.0.
# This file is part of QuantumBridge SDK.
# This implementation is developed for the QuantumBridge native architecture.

import pytest

from quantumbridge.compat import circuit_from_qiskit, circuit_to_qiskit, ir_from_qiskit, result_from_qiskit_counts

qiskit = pytest.importorskip("qiskit", reason="optional dependency unavailable: qiskit")


def test_qiskit_adapter_realistic_roundtrip_and_counts():
    qc = qiskit.QuantumCircuit(2, 2)
    qc.h(0)
    qc.ry(0.125, 1)
    qc.cx(0, 1)
    qc.measure(0, 0)
    qc.measure(1, 1)

    ir = ir_from_qiskit(qc)
    qb = circuit_from_qiskit(qc)
    exported = circuit_to_qiskit(qb)
    adapted_result = result_from_qiskit_counts({"00": 5, "11": 5})

    assert ir.num_qubits == 2
    assert exported.num_qubits == 2
    assert [item.operation.name for item in exported.data] == ["h", "ry", "cx", "measure", "measure"]
    assert len(qb.measurements) == 2
    assert adapted_result.counts() == {"00": 5, "11": 5}
    assert adapted_result.probabilities() == {"00": 0.5, "11": 0.5}

