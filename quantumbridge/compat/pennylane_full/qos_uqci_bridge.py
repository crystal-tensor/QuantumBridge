# This file is independently implemented for QuantumBridge SDK.
# No source code from Qiskit, PennyLane, or QOS-UQCI was copied.
"""Experimental PennyLane to QOS-UQCI job-spec scaffold."""

from __future__ import annotations

from .qiskit_bridge import pennylane_operations_to_quantumbridge_ir
from .warnings import PENNYLANE_ADAPTER_WARNING, get_provenance


def pennylane_tape_to_qos_uqci_job_spec(tape) -> dict:
    payload = pennylane_operations_to_quantumbridge_ir(getattr(tape, "operations", []))
    return quantumbridge_ir_to_uqci_payload(payload)


def quantumbridge_ir_to_uqci_payload(ir) -> dict:
    payload = ir.to_dict() if hasattr(ir, "to_dict") else dict(ir)
    return {
        "schema": "quantumbridge.qos_uqci.job_spec.v0.1",
        "experimental": True,
        "executes_hardware": False,
        "cloud_access": False,
        "token_storage": False,
        "source_ir": payload,
        "warnings": [
            PENNYLANE_ADAPTER_WARNING,
            "QOS-UQCI support is an experimental job-spec scaffold and does not access real hardware.",
        ],
        "provenance": get_provenance(mode="qos-uqci-job-spec").to_dict(),
    }
