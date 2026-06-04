# Copyright 2026 QuantumBridge Contributors.
# Licensed under the Apache License, Version 2.0.
# This file is part of QuantumBridge SDK.
# This implementation is developed for the QuantumBridge native architecture.
# Design source: docs/mvp/behavior_test_plan_v0.1.md.

from math import pi, sin

import numpy as np

from quantumbridge import Circuit, PauliZ, StatevectorDevice, parameter_shift


def test_parameter_shift_ry_z_expectation_matches_minus_sin():
    device = StatevectorDevice()

    def objective(values):
        return device.expectation(Circuit(1).ry(values[0], 0), PauliZ(0))

    theta = pi / 4
    gradient = parameter_shift(objective, np.array([theta]))
    assert abs(gradient[0] - (-sin(theta))) < 1e-7

