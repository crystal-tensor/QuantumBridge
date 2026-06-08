from quantumbridge.core import Circuit
from quantumbridge.noise import NoiseModel, NoisySampler, ReadoutError


def test_readout_error_flips_counts():
    model = NoiseModel().add_readout_error(0, ReadoutError(1.0, 0.0))
    result = NoisySampler(50, model, seed=2).run(Circuit(1))
    assert result.counts() == {"1": 50}
