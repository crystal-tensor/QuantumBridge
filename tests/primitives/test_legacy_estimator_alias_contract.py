# Copyright 2026 QuantumBridge Contributors. Apache-2.0.
"""Exact original alias-test body, with only its explicit Legacy entry changed."""

from math import pi
import numpy as np

from quantumbridge import Circuit, Parameter
from quantumbridge.primitives import LegacyEstimator
from quantumbridge.utils.math import PauliX, PauliZ


def test_explicit_legacy_estimator_retains_original_alias_math_nesting_and_metadata():
    theta = Parameter("theta")
    circuit = Circuit(1).ry(theta, 0)

    result = LegacyEstimator(default_precision=0.02).run_pubs(
        (circuit, [[PauliZ(0)], [PauliX(0)]], np.asarray([[0.0], [pi / 2]]))
    )

    assert len(result) == 1
    assert result[0].data.observable_shape == (((),), ((),))
    assert result[0].data.evs[0][0][0] == 1.0
    assert abs(result[0].data.evs[1][1][0] - 1.0) < 1e-12
    assert result[0].metadata["precision"] == 0.02
    assert result[0].metadata["num_parameter_sets"] == 2
