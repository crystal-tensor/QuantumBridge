# This file is independently implemented for QuantumBridge SDK.
# No source code from Qiskit, PennyLane, or PennyLane-Qiskit was copied.

import pytest

from quantumbridge.schema.pennylane_qiskit_bridge_results import (
    PennyLaneQiskitBridgeResult,
    QiskitToPennyLaneResult,
)


def test_bridge_result_round_trips():
    result = QiskitToPennyLaneResult(
        workflow="unit",
        mode="native_bridge",
        source_ecosystem="qiskit",
        target_ecosystem="pennylane",
        capability_level=3,
        statevector_probabilities={"0": 1.0},
        converted_ir={"instructions": []},
        converted_target={"operations": []},
    )
    payload = result.to_dict()
    restored = PennyLaneQiskitBridgeResult.from_dict(payload)
    assert restored.validate() is True
    assert restored.production_ready is False


def test_bridge_result_rejects_production_ready_claim():
    with pytest.raises(ValueError, match="production readiness"):
        QiskitToPennyLaneResult(
            workflow="bad",
            mode="native_bridge",
            source_ecosystem="qiskit",
            target_ecosystem="pennylane",
            capability_level=3,
            production_ready=True,
        )
