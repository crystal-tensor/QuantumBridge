# This file is independently implemented for QuantumBridge SDK.
# No source code from Qiskit Aer was copied.

from quantumbridge.compat.qiskit_aer.aer_upstream_adapter import (
    dependency_available,
    run_qasm_upstream_aer,
    validate_aer_dependencies,
    wrap_upstream_aer_result,
)
from quantumbridge.schema.aer_results import UpstreamAerResult


def test_validate_aer_dependencies_is_offline_safe():
    report = validate_aer_dependencies()
    assert isinstance(report["available"], bool)
    assert report["cloud_access"] is False
    assert report["token_read"] is False
    assert report["hardware_access"] is False


def test_upstream_wrapper_records_passthrough_provenance():
    result = wrap_upstream_aer_result({"raw": "demo"}, data={"counts": {"0": 2, "1": 2}}, shots=4)
    assert isinstance(result, UpstreamAerResult)
    assert result.mode == "upstream_passthrough"
    assert result.counts == {"0": 2, "1": 2}
    assert result.probabilities == {"0": 0.5, "1": 0.5}
    assert result.provenance["cloud_access"] is False


def test_upstream_qasm_returns_clear_result_when_unavailable_or_installed():
    if dependency_available():
        from qiskit import QuantumCircuit

        circuit = QuantumCircuit(1, 1)
        circuit.x(0)
        circuit.measure(0, 0)
        result = run_qasm_upstream_aer(circuit, shots=8)
        assert isinstance(result, UpstreamAerResult)
    else:
        result = run_qasm_upstream_aer(object(), shots=8)
        assert isinstance(result, UpstreamAerResult)
        assert result.unsupported_reason
