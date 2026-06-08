import pytest

from quantumbridge.algorithms.adapters import QiskitAlgorithmsAdapter


def test_vqe_adapter_optional():
    pytest.importorskip("qiskit_algorithms", reason="optional dependency unavailable: qiskit-algorithms")
    assert QiskitAlgorithmsAdapter().vqe()["algorithm"] == "VQE"
