from quantumbridge.compat.quafu.examples import quafu_bell_circuit
from quantumbridge.compat.quafu.mock_backend import run_quafu_mock_backend


def test_quafu_mock_backend_executes_bell_counts():
    result = run_quafu_mock_backend(quafu_bell_circuit(), shots=128, seed=23)
    assert set(result.counts) <= {"00", "11"}
    assert sum(result.counts.values()) == 128
    assert result.metadata["token_read"] is False
