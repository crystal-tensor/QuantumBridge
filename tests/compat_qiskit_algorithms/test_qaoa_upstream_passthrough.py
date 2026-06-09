# This file is independently implemented for QuantumBridge SDK.
# No source code from Qiskit Algorithms was copied.

import math

from quantumbridge.compat.qiskit_algorithms import run_qaoa_upstream, validate_algorithms_dependencies


def test_upstream_qaoa_runs_or_reports_clear_reason():
    result = run_qaoa_upstream()
    report = validate_algorithms_dependencies()
    assert result.algorithm == "QAOA"
    if report["available"]:
        assert result.unsupported_reason is None
        assert result.eigenvalue is not None
        assert math.isfinite(result.eigenvalue)
    else:
        assert result.unsupported_reason
