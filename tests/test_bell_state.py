# Copyright 2026 QuantumBridge Contributors.
# Licensed under the Apache License, Version 2.0.
# This file is part of QuantumBridge SDK.
# This implementation is developed for the QuantumBridge native architecture.
# Design source: docs/mvp/behavior_test_plan_v0.1.md.

from quantumbridge import Circuit, StatevectorDevice


def test_bell_state_probabilities_are_on_00_and_11():
    circuit = Circuit(2).h(0).cx(0, 1)
    probs = StatevectorDevice().probabilities(circuit)
    assert abs(probs["00"] - 0.5) < 1e-12
    assert abs(probs["11"] - 0.5) < 1e-12
    assert abs(probs["01"]) < 1e-12
    assert abs(probs["10"]) < 1e-12

