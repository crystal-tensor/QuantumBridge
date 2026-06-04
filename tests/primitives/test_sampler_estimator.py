# Copyright 2026 QuantumBridge Contributors.
# Licensed under the Apache License, Version 2.0.
# This file is part of QuantumBridge SDK.
# This implementation is developed for the QuantumBridge native architecture.

from quantumbridge import Circuit
from quantumbridge.primitives import Estimator, Sampler
from quantumbridge.utils.math import PauliZ


def test_sampler_and_estimator_primitives():
    counts = Sampler(shots=100, seed=2).run(Circuit(1).x(0)).counts()
    assert counts == {"1": 100}
    estimate = Estimator().run(Circuit(1), PauliZ(0)).expectation_value()
    assert abs(estimate - 1.0) < 1e-12

