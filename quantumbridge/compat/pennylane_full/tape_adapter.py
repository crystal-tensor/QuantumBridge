# This file is independently implemented for QuantumBridge SDK.
# No source code from Qiskit or PennyLane was copied.
"""PennyLane tape metadata and minimal IR bridge."""

from __future__ import annotations

from quantumbridge.compat.contracts import CapabilityLevel
from quantumbridge.compat.pennylane_adapter import ir_from_pennylane_tape

from .operations_adapter import operation_to_metadata, operation_to_quantumbridge_ir_fragment
from .warnings import adapter_metadata, unsupported


def describe_tape(tape) -> dict:
    operations = list(getattr(tape, "operations", []))
    measurements = list(getattr(tape, "measurements", []))
    return {
        "operation_count": len(operations),
        "measurement_count": len(measurements),
        "operations": [getattr(op, "name", type(op).__name__) for op in operations],
        "measurements": [type(measurement).__name__ for measurement in measurements],
        **adapter_metadata(CapabilityLevel.SCHEMA_ADAPTER),
    }


def tape_to_operation_metadata(tape) -> list[dict]:
    return [operation_to_metadata(op) for op in getattr(tape, "operations", [])]


def tape_to_quantumbridge_ir(tape):
    try:
        return ir_from_pennylane_tape(tape)
    except Exception as exc:
        fragments = [operation_to_quantumbridge_ir_fragment(op) for op in getattr(tape, "operations", [])]
        if any(isinstance(fragment, dict) and fragment.get("supported") is False for fragment in fragments):
            return unsupported(f"Tape contains unsupported operations: {exc}").to_dict()
        return unsupported(f"Tape could not be converted to QuantumBridge IR: {type(exc).__name__}: {exc}").to_dict()
