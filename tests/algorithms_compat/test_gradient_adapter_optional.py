import pytest

from quantumbridge.algorithms.adapters import QiskitAlgorithmsAdapter


def test_gradient_adapter_optional():
    pytest.importorskip("qiskit_algorithms", reason="optional dependency unavailable: qiskit-algorithms")
    assert QiskitAlgorithmsAdapter().gradient("ParamShift")["algorithm"] == "ParamShift"
