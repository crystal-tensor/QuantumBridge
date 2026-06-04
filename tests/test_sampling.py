# Copyright 2026 QuantumBridge Contributors.
# Licensed under the Apache License, Version 2.0.
# This file is part of QuantumBridge SDK.
# This implementation is developed for the QuantumBridge native architecture.
# Design source: docs/mvp/behavior_test_plan_v0.1.md.

from quantumbridge import Circuit, ShotSampler


def test_sampler_counts_sum_to_shots_and_match_balanced_state():
    circuit = Circuit(1).h(0)
    result = ShotSampler(shots=1000, seed=11).run(circuit)
    counts = result.counts()
    assert sum(counts.values()) == 1000
    assert 400 <= counts.get("0", 0) <= 600
    assert 400 <= counts.get("1", 0) <= 600


def test_sampler_deterministic_basis_state():
    circuit = Circuit(1).x(0)
    counts = ShotSampler(shots=100, seed=5).run(circuit).counts()
    assert counts == {"1": 100}

