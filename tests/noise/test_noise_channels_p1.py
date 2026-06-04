# Copyright 2026 QuantumBridge Contributors.
# Licensed under the Apache License, Version 2.0.
# This file is part of QuantumBridge SDK.
# This implementation is developed for the QuantumBridge native architecture.

import numpy as np
import pytest

from quantumbridge import Circuit
from quantumbridge.noise import BitFlipChannel, DepolarizingChannel, NoiseModel, PhaseFlipChannel, ReadoutError
from quantumbridge.primitives import Sampler


def test_noise_channels_and_model_metadata():
    assert BitFlipChannel(0).apply_probabilities({"0": 1.0, "1": 0.0}) == {"0": 1.0, "1": 0.0}
    assert BitFlipChannel(1).apply_probabilities({"0": 1.0, "1": 0.0}) == {"0": 0.0, "1": 1.0}
    assert PhaseFlipChannel(0).probability == 0.0
    kraus = DepolarizingChannel(0.3).kraus()
    total = sum(k.conj().T @ k for k in kraus)
    np.testing.assert_allclose(total, np.eye(2), atol=1e-12)
    readout = ReadoutError(0.1, 0.2)
    model = NoiseModel().add_channel(BitFlipChannel(0.1), wires=[0]).add_readout_error(0, readout)
    metadata = Sampler(shots=10, seed=1, noise_model=model).run(Circuit(1)).metadata()
    assert metadata["noise_model"] == {"channels": ["bit_flip"], "readout_errors": [0]}


def test_invalid_noise_probability():
    with pytest.raises(ValueError, match="between 0 and 1"):
        BitFlipChannel(-0.1)
    with pytest.raises(ValueError, match="between 0 and 1"):
        ReadoutError(0.1, 1.2)
