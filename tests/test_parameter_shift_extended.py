# Copyright 2026 QuantumBridge Contributors.
# Licensed under the Apache License, Version 2.0.
# This file is part of QuantumBridge SDK.
# This implementation is developed for the QuantumBridge native architecture.

from math import cos, pi

import numpy as np

from quantumbridge.transforms import finite_difference


def test_finite_difference_matches_cos_derivative():
    gradient = finite_difference(lambda x: cos(x[0]), np.array([pi / 3]))
    assert abs(gradient[0] + np.sin(pi / 3)) < 1e-6

