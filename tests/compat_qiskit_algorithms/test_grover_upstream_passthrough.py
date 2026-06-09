# This file is independently implemented for QuantumBridge SDK.
# No source code from Qiskit Algorithms was copied.

from quantumbridge.compat.qiskit_algorithms import run_grover_upstream, validate_algorithms_dependencies


def test_upstream_grover_runs_or_reports_clear_reason():
    result = run_grover_upstream()
    report = validate_algorithms_dependencies()
    assert result.algorithm == "Grover"
    if report["available"]:
        assert result.unsupported_reason is None
        assert result.bitstring == "11"
        assert result.probabilities
    else:
        assert result.unsupported_reason
