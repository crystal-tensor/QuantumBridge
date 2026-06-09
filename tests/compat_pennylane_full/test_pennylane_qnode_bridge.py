# This file is independently implemented for QuantumBridge SDK.
# No source code from Qiskit or PennyLane was copied.

import pytest

from quantumbridge.compat.pennylane_full.qnode_adapter import (
    qnode_to_quantumbridge_ir,
    qnode_to_workflow_metadata,
    run_qnode_passthrough,
)

qml = pytest.importorskip("pennylane", reason="optional dependency unavailable: pennylane")


def _simple_qnode():
    dev = qml.device("default.qubit", wires=2)

    @qml.qnode(dev)
    def circuit(theta):
        qml.RX(theta, wires=0)
        qml.CNOT(wires=[0, 1])
        return qml.probs(wires=[0, 1])

    return circuit


def test_qnode_workflow_metadata_and_passthrough_result():
    qnode = _simple_qnode()
    metadata = qnode_to_workflow_metadata(qnode)
    assert metadata["callable"] is True
    result = run_qnode_passthrough(qnode, 0.25)
    assert result.ecosystem == "pennylane"
    assert result.validate() is True


def test_qnode_to_quantumbridge_ir_with_sample_args():
    ir = qnode_to_quantumbridge_ir(_simple_qnode(), sample_args=(0.25,))
    assert ir.get("ecosystem") == "pennylane", ir
    assert [op["op"] for op in ir["operations"]] == ["rx", "cx"]
    assert ir["qnode"]["callable"] is True
