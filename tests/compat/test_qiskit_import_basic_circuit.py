# Copyright 2026 QuantumBridge Contributors.
# Licensed under the Apache License, Version 2.0.
# This file is part of QuantumBridge SDK.
# This implementation is developed for the QuantumBridge native architecture.

import pytest

from quantumbridge.compat import circuit_from_qiskit
from quantumbridge.devices import StatevectorDevice

qiskit = pytest.importorskip("qiskit", reason="optional dependency unavailable: qiskit")
QuantumCircuit = qiskit.QuantumCircuit


def test_qiskit_import_basic_circuit():
    qc = QuantumCircuit(2, 2)
    qc.h(0)
    qc.cx(0, 1)
    qc.measure(0, 0)
    qc.measure(1, 1)
    qb = circuit_from_qiskit(qc)
    probs = StatevectorDevice().probabilities(qb)
    assert abs(probs["00"] - 0.5) < 1e-12
    assert abs(probs["11"] - 0.5) < 1e-12
    assert len(qb.measurements) == 2
