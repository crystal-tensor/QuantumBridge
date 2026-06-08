import pytest

from quantumbridge.algorithms.adapters import QiskitAlgorithmsAdapter


def test_optimizer_adapter_optional():
    pytest.importorskip("qiskit_algorithms", reason="optional dependency unavailable: qiskit-algorithms")
    assert QiskitAlgorithmsAdapter().optimizer("COBYLA")["algorithm"] == "COBYLA"
