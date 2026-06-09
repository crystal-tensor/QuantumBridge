from quantumbridge.compat.qos_uqci.examples import qos_uqci_bell_circuit
from quantumbridge.compat.qos_uqci.mock_runtime import run_qos_uqci_mock_runtime


def test_qos_uqci_mock_runtime_executes_bell_counts():
    result = run_qos_uqci_mock_runtime(qos_uqci_bell_circuit(), shots=128, seed=21)
    assert result.counts
    assert set(result.counts) <= {"00", "11"}
    assert sum(result.counts.values()) == 128
    assert result.native_implementation is True
    assert result.metadata["hardware_access"] is False
