# This file is independently implemented for QuantumBridge SDK.
# No source code from Qiskit or PennyLane was copied.

import pytest

from quantumbridge.compat.qiskit_dynamics.backend_adapter import ADAPTER as BACKEND
from quantumbridge.compat.qiskit_dynamics.model_adapter import ADAPTER as MODEL
from quantumbridge.compat.qiskit_dynamics.signal_adapter import ADAPTER as SIGNAL
from quantumbridge.compat.qiskit_dynamics.solver_adapter import ADAPTER as SOLVER


def test_solver_model_signal_backend_availability():
    if not SOLVER.dependency_available():
        pytest.skip("qiskit-dynamics unavailable")
    assert SOLVER.passthrough_class("Solver") is not None
    assert MODEL.list_public_api_inventory()
    assert SIGNAL.list_public_api_inventory()
    assert BACKEND.list_public_api_inventory()


def test_signal_object_smoke():
    if not SIGNAL.dependency_available():
        pytest.skip("qiskit-dynamics unavailable")
    Signal = SIGNAL.passthrough_class("Signal")
    signal = Signal(1.0)
    assert signal(0.0) is not None