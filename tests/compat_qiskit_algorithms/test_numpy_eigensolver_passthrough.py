# This file is independently implemented for QuantumBridge SDK.
# No source code from Qiskit or PennyLane was copied.

import pytest

from quantumbridge.compat.qiskit_algorithms.eigensolver_adapter import ADAPTER


def test_numpy_eigensolver_and_vqd_availability():
    if not ADAPTER.dependency_available():
        pytest.skip("qiskit-algorithms unavailable")
    assert ADAPTER.passthrough_class("NumPyEigensolver") is not None
    assert ADAPTER.passthrough_class("VQD") is not None