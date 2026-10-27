# Copyright 2026 QuantumBridge Contributors. Apache-2.0.
"""The exact pre-migration inputs/behavior remain at explicit Legacy entry."""
from math import pi
import numpy as np
from quantumbridge import Circuit, Parameter
from quantumbridge.primitives import LegacySampler


def test_legacy_numpy_parameter_values_keep_original_counts_and_nesting():
    theta = Parameter("theta")
    circuit = Circuit(1).ry(theta, 0)
    result = LegacySampler(shots=24, seed=11).run_pubs((circuit, np.asarray([[0.0], [pi]]), 24))
    assert len(result) == 1
    assert result[0].data.counts == [{"0": 24}, {"1": 24}]
    assert result[0].data.meas[0].get_counts() == {"0": 24}
    assert result[0].data.meas[1].get_counts() == {"1": 24}
    assert result[0].metadata["num_parameter_sets"] == 2


def test_legacy_job_like_result_keeps_original_identity_and_fixed_id():
    result = LegacySampler(shots=12, seed=5).run([(Circuit(1).x(0),)])
    assert result.result() is result
    assert result.done()
    assert result.status() == "DONE"
    assert not result.running()
    assert not result.cancelled()
    assert result.job_id() == "quantumbridge-primitive-result"
    assert result.result()[0].data.meas.get_counts() == {"1": 12}
