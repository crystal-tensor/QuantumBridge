# This file is independently implemented for QuantumBridge SDK.
# No source code from Qiskit, PennyLane, or PennyLane-Qiskit was copied.

from quantumbridge.compat.pennylane_qiskit import run_pennylane_to_qiskit_bridge


def test_bridge_metadata_never_claims_cloud_token_or_hardware():
    result = run_pennylane_to_qiskit_bridge([{"operation": "Hadamard", "wires": [0]}])
    assert result.metadata["cloud_access"] is False
    assert result.metadata["token_read"] is False
    assert result.metadata["hardware_access"] is False
    assert result.provenance["cloud_access"] is False
    assert result.provenance["token_read"] is False
    assert result.provenance["hardware_access"] is False
