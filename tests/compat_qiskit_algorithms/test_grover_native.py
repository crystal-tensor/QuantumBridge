# This file is independently implemented for QuantumBridge SDK.
# No source code from Qiskit Algorithms was copied.

from quantumbridge.compat.qiskit_algorithms import (
    build_grover_oracle_marked_bitstrings,
    grover_result_to_dict,
    run_grover_native,
    simulate_grover_statevector_native,
)


def test_native_grover_finds_marked_bitstring():
    result = run_grover_native(["11"], num_qubits=2)
    assert result.algorithm == "Grover"
    assert result.mode == "native_minimal"
    assert result.bitstring == "11"
    assert result.probabilities["11"] == 1.0
    assert result.validate()


def test_native_grover_oracle_and_statevector_metadata():
    oracle = build_grover_oracle_marked_bitstrings(["10"], num_qubits=2)
    state, metadata = simulate_grover_statevector_native(["10"], num_qubits=2, iterations=1)
    assert oracle["marked_bitstrings"] == ("10",)
    assert metadata["iterations"] == 1
    assert state.shape == (4,)
    assert grover_result_to_dict(run_grover_native(["10"], 2))["bitstring"] == "10"
