# This file is independently implemented for QuantumBridge SDK.
# No source code from Qiskit IBM Runtime was copied.

from quantumbridge.compat import qiskit_runtime
from quantumbridge.compat.qiskit_contract_helpers import assert_qiskit_contract


def test_qiskit_runtime_offline_contract_does_not_read_tokens(monkeypatch):
    monkeypatch.setenv("QISKIT_IBM_TOKEN", "sentinel-token")
    monkeypatch.setenv("IBM_QUANTUM_TOKEN", "sentinel-token")
    assert_qiskit_contract(qiskit_runtime, advisory=True, offline_only=True)
    report = qiskit_runtime.get_dependency_report()
    assert report["cloud_access"] is False
    assert report["token_read"] is False
    assert report["token_storage"] is False
    assert "sentinel-token" not in str(report)
