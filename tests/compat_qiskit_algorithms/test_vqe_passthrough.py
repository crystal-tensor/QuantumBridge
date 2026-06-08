# This file is independently implemented for QuantumBridge SDK.
# No source code from Qiskit or PennyLane was copied.

import pytest

from quantumbridge.compat.qiskit_algorithms.minimum_eigensolver_adapter import ADAPTER


@pytest.mark.parametrize("name", ["VQE", "QAOA", "SamplingVQE", "NumPyMinimumEigensolver"])
def test_minimum_eigensolver_passthrough(name):
    if not ADAPTER.dependency_available():
        pytest.skip("qiskit-algorithms unavailable")
    assert ADAPTER.passthrough_class(name) is not None