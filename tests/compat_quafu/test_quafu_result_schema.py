from quantumbridge.compat.quafu.examples import quafu_bell_circuit
from quantumbridge.compat.quafu.mock_backend import run_quafu_mock_backend
from quantumbridge.schema.backend_results import QuafuBackendResult


def test_quafu_result_schema_roundtrip():
    result = run_quafu_mock_backend(quafu_bell_circuit(), shots=64, seed=7)
    restored = QuafuBackendResult.from_dict(result.to_dict())
    assert restored.validate()
    assert restored.counts == result.counts
    assert restored.to_json()
