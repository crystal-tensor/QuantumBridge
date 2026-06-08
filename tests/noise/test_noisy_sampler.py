from quantumbridge.core import Circuit
from quantumbridge.noise import BitFlipChannel, NoiseModel, NoisySampler


def test_noisy_sampler_p1_behavior_extremes():
    circuit = Circuit(1)
    clean = NoisySampler(100, NoiseModel().add_channel(BitFlipChannel(0.0), wires=[0]), seed=1).run(circuit)
    flipped = NoisySampler(100, NoiseModel().add_channel(BitFlipChannel(1.0), wires=[0]), seed=1).run(circuit)
    assert clean.counts() == {"0": 100}
    assert flipped.counts() == {"1": 100}
