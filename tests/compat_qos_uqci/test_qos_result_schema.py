from quantumbridge.compat.qos_uqci.examples import qos_uqci_bell_circuit
from quantumbridge.compat.qos_uqci.mock_runtime import run_qos_uqci_mock_runtime
from quantumbridge.schema.backend_results import QOSUQCIBackendResult


def test_qos_result_schema_roundtrip():
    result = run_qos_uqci_mock_runtime(qos_uqci_bell_circuit(), shots=64, seed=5)
    payload = result.to_dict()
    restored = QOSUQCIBackendResult.from_dict(payload)
    assert restored.validate()
    assert restored.to_json()
    assert restored.counts == result.counts
