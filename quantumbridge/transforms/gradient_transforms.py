# Copyright 2026 QuantumBridge Contributors.
# Licensed under the Apache License, Version 2.0.
# This file is part of QuantumBridge SDK.
# This implementation is developed for the QuantumBridge native architecture.

from __future__ import annotations

from numbers import Real
from typing import Callable, Sequence, Union

import numpy as np


def finite_difference(objective: Callable[[np.ndarray], Real], parameters: Union[Sequence[Real], Real], step: float = 1e-6):
    scalar_input = isinstance(parameters, Real)
    values = np.array([parameters] if scalar_input else list(parameters), dtype=float)
    gradient = np.zeros_like(values)
    for index in range(len(values)):
        plus = values.copy()
        minus = values.copy()
        plus[index] += step
        minus[index] -= step
        gradient[index] = (float(objective(plus)) - float(objective(minus))) / (2 * step)
    return float(gradient[0]) if scalar_input else gradient
