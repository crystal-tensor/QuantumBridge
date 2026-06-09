# This file is independently implemented for QuantumBridge SDK.
# No source code from Qiskit, PennyLane, or QOS-UQCI was copied.

from quantumbridge.compat.pennylane_full.qos_uqci_bridge import quantumbridge_ir_to_uqci_payload


def test_pennylane_qos_uqci_bridge_generates_job_spec_only():
    payload = quantumbridge_ir_to_uqci_payload(
        {
            "ir_version": "qb-ir-v0.1",
            "registers": {"quantum": {"size": 1}, "classical": {"size": 0}},
            "instructions": [],
            "measurements": [],
            "metadata": {},
        }
    )
    assert payload["experimental"] is True
    assert payload["executes_hardware"] is False
    assert payload["cloud_access"] is False
    assert payload["token_storage"] is False
