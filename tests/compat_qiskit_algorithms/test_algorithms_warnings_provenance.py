# This file is independently implemented for QuantumBridge SDK.
# No source code from Qiskit Algorithms was copied.

from quantumbridge.compat.qiskit_algorithms import run_grover_native, run_qaoa_native_maxcut, run_vqe_native


def test_algorithms_warnings_and_provenance_avoid_parity_claims():
    results = [
        run_vqe_native(parameter_grid=(0.0, 3.141592653589793)),
        run_qaoa_native_maxcut(((0, 1),), 2),
        run_grover_native(["11"], 2),
    ]
    for result in results:
        joined = " ".join(result.warnings).lower()
        assert "not a full qiskit algorithms replacement" in joined
        assert "production" in joined
        assert result.provenance["official_endorsement"] is False
        assert result.provenance["copied_upstream_source"] is False
