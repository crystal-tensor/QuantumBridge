# Copyright 2026 QuantumBridge Contributors.
# Licensed under the Apache License, Version 2.0.
# This file is part of QuantumBridge SDK.
# This implementation is developed for the QuantumBridge native architecture.

import pytest

from quantumbridge import Circuit
from quantumbridge.compat import circuit_to_qiskit

pytest.importorskip("qiskit", reason="optional dependency unavailable: qiskit")


def test_qiskit_export_basic_circuit():
    qb = Circuit(2, 2).h(0).cx(0, 1).measure(0, 0).measure(1, 1)
    qc = circuit_to_qiskit(qb)
    assert qc.num_qubits == 2
    assert qc.num_clbits == 2
    assert [item.operation.name for item in qc.data] == ["h", "cx", "measure", "measure"]
