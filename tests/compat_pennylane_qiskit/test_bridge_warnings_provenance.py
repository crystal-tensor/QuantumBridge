# This file is independently implemented for QuantumBridge SDK.
# No source code from Qiskit, PennyLane, or PennyLane-Qiskit was copied.

from quantumbridge.compat.pennylane_qiskit import run_pennylane_to_qiskit_bridge


def test_bridge_warnings_and_provenance_state_boundaries():
    result = run_pennylane_to_qiskit_bridge([{"operation": "Hadamard", "wires": [0]}])
    text = " ".join(result.warnings)
    assert "not a full PennyLane-Qiskit plugin replacement" in text
    assert "small operation and measurement subset" in text
    assert result.provenance["source_code_copied"] is False
    assert result.provenance["official_endorsement"] is False
    assert result.metadata["full_plugin_parity_claim"] is False
