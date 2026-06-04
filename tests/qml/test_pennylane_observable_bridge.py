# Copyright 2026 QuantumBridge Contributors.
# Licensed under the Apache License, Version 2.0.
# This file is part of QuantumBridge SDK.
# This implementation is developed for the QuantumBridge native architecture.

import warnings

import pytest

from quantumbridge.compat.pennylane_adapter import (
    circuit_and_observable_from_pennylane_tape,
    ir_from_pennylane_tape,
    observable_from_pennylane,
)

qml = pytest.importorskip("pennylane", reason="optional dependency unavailable: pennylane")


def test_pennylane_observable_bridge_pauli_z():
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        obs = qml.PauliZ(0)
    qb = observable_from_pennylane(obs)
    assert qb.terms == ((0, "Z"),)


def test_pennylane_tape_to_circuit_and_ir():
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        tape = qml.tape.QuantumScript(
            [qml.Hadamard(0), qml.CNOT([0, 1])],
            [qml.expval(qml.PauliZ(0))],
        )
    circuit, observable = circuit_and_observable_from_pennylane_tape(tape)
    ir = ir_from_pennylane_tape(tape).to_dict()
    assert [op.name for op in circuit.operations] == ["h", "cx"]
    assert observable.terms == ((0, "Z"),)
    assert ir["instructions"][1]["op"] == "cx"
