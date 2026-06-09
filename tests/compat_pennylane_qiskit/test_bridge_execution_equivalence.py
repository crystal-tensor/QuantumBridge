# This file is independently implemented for QuantumBridge SDK.
# No source code from Qiskit, PennyLane, or PennyLane-Qiskit was copied.

from quantumbridge.compat.pennylane_qiskit import run_bidirectional_bridge_equivalence


def test_bidirectional_bell_equivalence_proof():
    result = run_bidirectional_bridge_equivalence(shots=64, seed=7)
    assert result.validate() is True
    assert result.equivalence_status == "equivalent"
    assert result.circuit_summary["max_probability_delta"] <= 1e-8
    assert set(result.statevector_probabilities) == {"00", "11"}
    assert result.metadata["counts_comparison"] == "statistical_support"
