# This file is independently implemented for QuantumBridge SDK.
# No source code from Qiskit or PennyLane was copied.

import pytest

from quantumbridge.compat.pennylane_full.qnode_adapter import describe_qnode, run_qnode_passthrough, wrap_qnode_result

qml = pytest.importorskip("pennylane", reason="optional dependency unavailable: pennylane")


def test_pennylane_qnode_adapter_runs_passthrough_and_wraps():
    dev = qml.device("default.qubit", wires=1)

    @qml.qnode(dev)
    def circuit():
        qml.PauliX(wires=0)
        return qml.probs(wires=0)

    description = describe_qnode(circuit)
    result = run_qnode_passthrough(circuit)
    assert description["callable"] is True
    assert result.ecosystem == "pennylane"


def test_pennylane_qnode_wrap_raw_result():
    assert wrap_qnode_result(0.5).raw_type == "float"
