# This file is independently implemented for QuantumBridge SDK.
# No source code from Qiskit Aer was copied.

import pytest

from quantumbridge.compat.qiskit_aer import run_statevector_simulator_native
from quantumbridge.core import Circuit
from quantumbridge.schema.aer_results import StatevectorSimulationResult


def test_statevector_native_bell_probabilities():
    circuit = Circuit(2)
    circuit.h(0).cx(0, 1)

    result = run_statevector_simulator_native(circuit)

    assert isinstance(result, StatevectorSimulationResult)
    assert result.mode == "native_minimal"
    assert result.capability_level == 3
    assert result.production_ready is False
    assert result.native_implementation is True
    assert result.probabilities["00"] == pytest.approx(0.5)
    assert result.probabilities["11"] == pytest.approx(0.5)
    assert result.metadata["cloud_access"] is False
    assert result.metadata["token_read"] is False
    assert result.metadata["hardware_access"] is False
