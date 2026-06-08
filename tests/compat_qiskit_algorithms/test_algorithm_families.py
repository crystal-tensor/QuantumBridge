# This file is independently implemented for QuantumBridge SDK.
# No source code from Qiskit or PennyLane was copied.

import pytest

from quantumbridge.compat.qiskit_algorithms.amplitude_adapter import ADAPTER as AMPLITUDE
from quantumbridge.compat.qiskit_algorithms.gradient_adapter import ADAPTER as GRADIENT
from quantumbridge.compat.qiskit_algorithms.grover_adapter import ADAPTER as GROVER
from quantumbridge.compat.qiskit_algorithms.optimizer_adapter import ADAPTER as OPTIMIZER


def test_grover_and_amplitude_availability():
    if not GROVER.dependency_available():
        pytest.skip("qiskit-algorithms unavailable")
    assert GROVER.passthrough_class("Grover") is not None
    assert AMPLITUDE.list_public_api_inventory()


def test_optimizer_and_gradient_inventory():
    if not OPTIMIZER.dependency_available():
        pytest.skip("qiskit-algorithms unavailable")
    assert OPTIMIZER.list_public_api_inventory()
    assert GRADIENT.list_public_api_inventory()