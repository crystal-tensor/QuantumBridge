# This file is independently implemented for QuantumBridge SDK.
# No source code from Qiskit, PennyLane, or QOS-UQCI was copied.

import pytest

from quantumbridge.compat.pennylane_full.qos_uqci_bridge import (
    pennylane_tape_to_qos_uqci_job_spec,
    qos_uqci_job_spec_to_dict,
    quantumbridge_ir_to_uqci_payload,
    uqci_payload_to_quantumbridge_ir,
    validate_qos_uqci_job_spec,
)

qml = pytest.importorskip("pennylane", reason="optional dependency unavailable: pennylane")


def test_qos_uqci_job_spec_generation_and_validation():
    tape = qml.tape.QuantumScript([qml.Hadamard(0), qml.CNOT(wires=[0, 1])], [qml.probs(wires=[0, 1])])
    spec = pennylane_tape_to_qos_uqci_job_spec(tape)
    assert spec["target"] == "qos_uqci"
    assert spec["source"] == "pennylane"
    assert spec["experimental"] is True
    assert spec["uqci_payload"]["cloud_access"] is False
    assert spec["uqci_payload"]["token_storage"] is False
    assert validate_qos_uqci_job_spec(spec) is True
    assert qos_uqci_job_spec_to_dict(spec)["target"] == "qos_uqci"


def test_uqci_payload_to_quantumbridge_ir_roundtrip_shape():
    payload = quantumbridge_ir_to_uqci_payload(
        {
            "wires": [0],
            "operations": [{"op": "h", "wires": [0], "targets": [0], "controls": [], "params": []}],
            "measurements": [],
            "shots": None,
        }
    )
    ir = uqci_payload_to_quantumbridge_ir(payload)
    assert ir["ecosystem"] == "pennylane"
    assert ir["operations"][0]["op"] == "h"
    assert payload["executes_hardware"] is False
