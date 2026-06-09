# This file is independently implemented for QuantumBridge SDK.
# No source code from Qiskit Aer was copied.

import pytest

from quantumbridge.compat.qiskit_aer import (
    apply_measurement_bitflip_noise,
    create_bitflip_noise_model,
    create_depolarizing_metadata,
    run_noisy_qasm_simulator_native,
    validate_noise_model,
)
from quantumbridge.core import Circuit
from quantumbridge.schema.aer_results import NoisySimulationResult


def test_bitflip_noise_model_validation_and_p_zero():
    model = create_bitflip_noise_model(0.0)
    assert validate_noise_model(model)["p"] == 0.0
    assert apply_measurement_bitflip_noise({"0": 5}, 0.0, 5, seed=1) == {"0": 5}
    with pytest.raises(ValueError):
        create_bitflip_noise_model(1.1)


def test_depolarizing_metadata_is_metadata_only():
    model = create_depolarizing_metadata(0.25)
    assert model["type"] == "depolarizing_metadata"
    assert model["applied_as"] == "metadata_only"
    assert model["qiskit_aer_noise_model_parity"] is False


def test_noisy_qasm_native_is_seeded_and_warned():
    circuit = Circuit(1, 1)
    circuit.h(0).measure(0, 0)
    model = create_bitflip_noise_model(0.2)

    first = run_noisy_qasm_simulator_native(circuit, shots=32, noise_model=model, seed=3)
    second = run_noisy_qasm_simulator_native(circuit, shots=32, noise_model=model, seed=3)

    assert isinstance(first, NoisySimulationResult)
    assert first.counts == second.counts
    assert sum(first.counts.values()) == 32
    assert first.noise_model["educational_only"] is True
    assert any("noise" in item.lower() for item in first.warnings)
