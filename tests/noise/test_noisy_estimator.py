from quantumbridge.core import Circuit
from quantumbridge.noise import BitFlipChannel, NoiseModel, NoisyEstimator
from quantumbridge.utils.math import PauliZ


def test_noisy_estimator_expectation_changes_direction():
    clean = NoisyEstimator(NoiseModel().add_channel(BitFlipChannel(0.0), wires=[0])).expectation(Circuit(1), PauliZ(0))
    noisy = NoisyEstimator(NoiseModel().add_channel(BitFlipChannel(1.0), wires=[0])).expectation(Circuit(1), PauliZ(0))
    assert clean == 1.0
    assert noisy == -1.0
