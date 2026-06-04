# Copyright 2026 QuantumBridge Contributors.
# Licensed under the Apache License, Version 2.0.
# This file is part of QuantumBridge SDK.
# This implementation is developed for the QuantumBridge native architecture.

import pytest

from quantumbridge.compat import circuit_from_qiskit, circuit_to_qiskit, ir_from_qiskit, ir_to_qiskit, result_from_qiskit_counts

qiskit = pytest.importorskip("qiskit", reason="optional dependency unavailable: qiskit")
QuantumCircuit = qiskit.QuantumCircuit


def test_qiskit_roundtrip_ir_for_basic_circuit():
    qc = QuantumCircuit(1, 1)
    qc.ry(0.25, 0)
    qc.measure(0, 0)
    qb = circuit_from_qiskit(qc)
    ir = qb.to_ir().to_dict()
    direct_ir = ir_from_qiskit(qc).to_dict()
    exported = circuit_to_qiskit(qb)
    exported_from_ir = ir_to_qiskit(qb.to_ir())
    assert ir["instructions"][0]["op"] == "ry"
    assert direct_ir["instructions"][0]["op"] == "ry"
    assert exported.data[0].operation.name == "ry"
    assert exported_from_ir.data[0].operation.name == "ry"
    assert exported.num_qubits == qc.num_qubits


def test_qiskit_counts_result_adapter():
    result = result_from_qiskit_counts({"0": 3, "1": 1})
    assert result.counts() == {"0": 3, "1": 1}
    assert result.probabilities() == {"0": 0.75, "1": 0.25}
