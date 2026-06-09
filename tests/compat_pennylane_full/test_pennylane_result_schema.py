# This file is independently implemented for QuantumBridge SDK.
# No source code from Qiskit or PennyLane was copied.

import json

from quantumbridge.compat.pennylane_full.result_adapter import wrap_pennylane_result
from quantumbridge.schema import PennyLaneResult
from quantumbridge.schema.pennylane_results import QNodeResult


def test_pennylane_result_schema_roundtrip():
    result = wrap_pennylane_result({"probabilities": [1.0, 0.0]})
    assert isinstance(result, PennyLaneResult)
    assert result.capability_level == 2
    assert result.validate()
    restored = PennyLaneResult.from_dict(json.loads(result.to_json()))
    assert restored.to_dict() == result.to_dict()


def test_pennylane_qnode_result_schema_class():
    result = QNodeResult(raw_type="float", data=0.5)
    assert result.ecosystem == "pennylane"
    assert result.to_dict()["unsupported_reason"] is None
