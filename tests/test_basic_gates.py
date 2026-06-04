# Copyright 2026 QuantumBridge Contributors.
# Licensed under the Apache License, Version 2.0.
# This file is part of QuantumBridge SDK.
# This implementation is developed for the QuantumBridge native architecture.
# Design source: docs/mvp/behavior_test_plan_v0.1.md.

import numpy as np

from quantumbridge import Circuit, StatevectorDevice


def test_h_on_zero_state():
    circuit = Circuit(1).h(0)
    state = StatevectorDevice().statevector(circuit)
    expected = np.array([1 / np.sqrt(2), 1 / np.sqrt(2)], dtype=complex)
    np.testing.assert_allclose(state, expected, atol=1e-10)


def test_x_on_zero_state():
    circuit = Circuit(1).x(0)
    state = StatevectorDevice().statevector(circuit)
    expected = np.array([0, 1], dtype=complex)
    np.testing.assert_allclose(state, expected, atol=1e-10)

