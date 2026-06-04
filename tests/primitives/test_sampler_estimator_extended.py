# Copyright 2026 QuantumBridge Contributors.
# Licensed under the Apache License, Version 2.0.
# This file is part of QuantumBridge SDK.
# This implementation is developed for the QuantumBridge native architecture.

from math import cos, pi

import pytest

from quantumbridge import Circuit, Hamiltonian
from quantumbridge.primitives import Estimator, Sampler
from quantumbridge.utils.math import PauliString, PauliZ


def test_sampler_distribution_seed_reproducibility_shots_and_metadata():
    circuit = Circuit(1).h(0)
    a = Sampler(shots=200, seed=123).run(circuit)
    b = Sampler(shots=200, seed=123).run(circuit)
    assert a.counts() == b.counts()
    assert sum(a.counts().values()) == 200
    assert a.metadata()["shots"] == 200


def test_estimator_z_hamiltonian_invalid_observable_and_metadata():
    estimator = Estimator()
    assert abs(estimator.run(Circuit(1), PauliZ(0)).expectation_value() - 1.0) < 1e-12
    hamiltonian = Hamiltonian([(1.5, PauliString([(0, "Z")]))])
    value = estimator.run(Circuit(1).ry(pi / 3, 0), hamiltonian).expectation_value()
    assert abs(value - 1.5 * cos(pi / 3)) < 1e-10
    assert estimator.run(Circuit(1), PauliZ(0)).metadata()["primitive"] == "Estimator"
    with pytest.raises(Exception):
        estimator.run(Circuit(1), object())

