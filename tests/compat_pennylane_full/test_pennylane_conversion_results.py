# This file is independently implemented for QuantumBridge SDK.
# No source code from Qiskit or PennyLane was copied.

from quantumbridge.schema.pennylane_results import (
    ConversionResult,
    MeasurementBridgeResult,
    OperationBridgeResult,
    QOSUQCIJobSpecResult,
    QiskitBridgeResult,
    TapeBridgeResult,
)


def test_stage8c_bridge_results_roundtrip_validate():
    result_types = (
        OperationBridgeResult,
        MeasurementBridgeResult,
        TapeBridgeResult,
        QiskitBridgeResult,
        QOSUQCIJobSpecResult,
        ConversionResult,
    )
    for result_type in result_types:
        result = result_type(data={"ok": True}, warnings=["metadata only"], provenance={"source_code_copied": False})
        assert result.validate() is True
        restored = result_type.from_dict(result.to_dict())
        assert restored.ecosystem == "pennylane"
        assert restored.to_json()
