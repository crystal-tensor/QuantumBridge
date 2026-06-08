from quantumbridge.core import Circuit
from quantumbridge.noise import BitFlipChannel, NoiseModel, NoisySampler


def test_noisy_sampler_seed_reproducible():
    model = NoiseModel().add_channel(BitFlipChannel(0.5), wires=[0])
    a = NoisySampler(100, model, seed=123).run(Circuit(1)).counts()
    b = NoisySampler(100, model, seed=123).run(Circuit(1)).counts()
    assert a == b
