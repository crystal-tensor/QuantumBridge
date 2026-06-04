# Copyright 2026 QuantumBridge Contributors.
# Licensed under the Apache License, Version 2.0.
# This file is part of QuantumBridge SDK.
# This implementation is developed for the QuantumBridge native architecture.

import pytest

from quantumbridge import Circuit, circuit_from_openqasm


def test_qasm_p1_bell_comments_include_barrier_and_whole_measure():
    text = """
    OPENQASM 2.0;
    include "qelib1.inc";
    // bell circuit
    qreg q[2];
    creg c[2];
    h q[0];
    barrier q[0],q[1];
    cx q[0],q[1]; // entangle
    measure q -> c;
    """
    circuit = circuit_from_openqasm(text)
    assert circuit.num_qubits == 2
    assert circuit.num_bits == 2
    assert [op.name for op in circuit.operations] == ["h", "cx"]
    assert [(m.wire, m.bit) for m in circuit.measurements] == [(0, 0), (1, 1)]


def test_qasm_p1_parameterized_and_multi_registers():
    text = """
    OPENQASM 2.0;
    include "qelib1.inc";
    qreg qa[1];
    qreg qb[1];
    creg ca[1];
    creg cb[1];
    rx(0.1) qa[0];
    ry(0.2) qb[0];
    rz(0.3) qa[0];
    cz qa[0],qb[0];
    measure qa[0] -> ca[0];
    measure qb[0] -> cb[0];
    """
    circuit = circuit_from_openqasm(text)
    assert circuit.num_qubits == 2
    assert circuit.num_bits == 2
    assert [op.name for op in circuit.operations] == ["rx", "ry", "rz", "cz"]
    assert [(m.wire, m.bit) for m in circuit.measurements] == [(0, 0), (1, 1)]


def test_qasm_p1_unsupported_and_malformed():
    with pytest.raises(ValueError, match="does not support"):
        circuit_from_openqasm("OPENQASM 2.0;\nqreg q[1];\nu3(0,0,0) q[0];\n")
    with pytest.raises(ValueError, match="qreg"):
        circuit_from_openqasm("OPENQASM 2.0;\nh q[0];\n")


def test_qasm_p1_roundtrip():
    circuit = Circuit(2, 2).h(0).rx(0.2, 1).cx(0, 1).measure(0, 0).measure(1, 1)
    imported = circuit_from_openqasm(circuit.to_openqasm())
    assert imported.num_qubits == 2
    assert imported.num_bits == 2
    assert [op.name for op in imported.operations] == ["h", "rx", "cx"]

