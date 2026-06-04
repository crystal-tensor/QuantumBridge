# Copyright 2026 QuantumBridge Contributors.
# Licensed under the Apache License, Version 2.0.
# This file is part of QuantumBridge SDK.
# This implementation is developed for the QuantumBridge native architecture.
# Design source: docs/mvp/behavior_test_plan_v0.1.md.

from quantumbridge import Circuit, StatevectorDevice, circuit_from_openqasm


def test_openqasm_export_contains_declarations_and_gates():
    text = Circuit(2, 2).h(0).cx(0, 1).measure(0, 0).measure(1, 1).to_openqasm()
    assert "OPENQASM 2.0;" in text
    assert "qreg q[2];" in text
    assert "creg c[2];" in text
    assert "h q[0];" in text
    assert "cx q[0],q[1];" in text
    assert "measure q[0] -> c[0];" in text
    assert "measure q[1] -> c[1];" in text


def test_result_serializes_to_dictionary():
    result = StatevectorDevice().run(Circuit(1).h(0))
    data = result.to_dict()
    assert data["statevector"][0]["real"] == data["statevector"][1]["real"]
    assert data["probabilities"]["0"] == data["probabilities"]["1"]
    assert data["metadata"]["device"] == "StatevectorDevice"


def test_openqasm_import_supported_subset():
    text = "OPENQASM 2.0;\nqreg q[1];\ncreg c[1];\nh q[0];\nmeasure q[0] -> c[0];\n"
    circuit = circuit_from_openqasm(text)
    assert circuit.num_qubits == 1
    assert circuit.num_bits == 1
    assert circuit.operations[0].name == "h"
    assert circuit.measurements[0].bit == 0
