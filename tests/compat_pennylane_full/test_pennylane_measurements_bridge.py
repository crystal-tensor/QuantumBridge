# This file is independently implemented for QuantumBridge SDK.
# No source code from Qiskit or PennyLane was copied.

import pytest

from quantumbridge.compat.pennylane_full.measurements_adapter import (
    describe_measurement,
    measurement_to_metadata,
    measurement_to_quantumbridge_result_fragment,
)

qml = pytest.importorskip("pennylane", reason="optional dependency unavailable: pennylane")


def test_measurement_metadata_for_expval():
    metadata = measurement_to_metadata(qml.expval(qml.PauliZ(0)))
    assert metadata["measurement_type"] == "expval"
    assert metadata["observable"] == "PauliZ"
    assert metadata["wires"] == [0]
    assert metadata["capability_level"] == 2
    assert metadata["unsupported_reason"] is None


def test_measurement_result_fragment_for_probs():
    fragment = measurement_to_quantumbridge_result_fragment(qml.probs(wires=[0, 1]))
    assert fragment["ecosystem"] == "pennylane"
    assert fragment["measurement"]["measurement_type"] == "probs"
    assert fragment["measurement"]["wires"] == [0, 1]


def test_measurement_describe_marks_unknown_as_inventory_only():
    metadata = describe_measurement("not_a_measurement")
    assert metadata["supported"] is False
    assert metadata["capability_level"] == 0
