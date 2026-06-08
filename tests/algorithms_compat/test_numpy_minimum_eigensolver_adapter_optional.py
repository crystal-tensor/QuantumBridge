import pytest

from quantumbridge.algorithms.adapters import QiskitAlgorithmsAdapter


def test_numpy_minimum_eigensolver_adapter_optional():
    pytest.importorskip("qiskit_algorithms", reason="optional dependency unavailable: qiskit-algorithms")
    assert QiskitAlgorithmsAdapter().numpy_minimum_eigensolver()["algorithm"] == "NumPyMinimumEigensolver"
