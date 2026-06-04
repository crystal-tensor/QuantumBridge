# Copyright 2026 QuantumBridge Contributors.
# Licensed under the Apache License, Version 2.0.
# This file is part of QuantumBridge SDK.
# This implementation is developed for the QuantumBridge native architecture.
# Design source: docs/mvp/behavior_test_plan_v0.1.md.

from math import cos, pi

from quantumbridge import Circuit, Hamiltonian, PauliString, PauliZ, StatevectorDevice


def test_ry_expectation_z_matches_cos_theta():
    theta = pi / 3
    circuit = Circuit(1).ry(theta, 0)
    value = StatevectorDevice().expectation(circuit, PauliZ(0))
    assert abs(value - cos(theta)) < 1e-10


def test_hamiltonian_expectation_is_weighted_sum():
    theta = pi / 4
    circuit = Circuit(1).ry(theta, 0)
    hamiltonian = Hamiltonian([(0.5, PauliZ(0)), (0.25, PauliString([]))])
    value = StatevectorDevice().expectation(circuit, hamiltonian)
    assert abs(value - (0.5 * cos(theta) + 0.25)) < 1e-10

