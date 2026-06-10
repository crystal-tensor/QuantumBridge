# Copyright 2026 QuantumBridge Contributors.
# Licensed under the Apache License, Version 2.0.
# This file is part of QuantumBridge SDK.
# This implementation is developed for the QuantumBridge native architecture.

"""Native circuit-library builders for reusable QuantumBridge circuits."""

from .arithmetic import integer_comparator, weighted_adder
from .data_preparation import amplitude_encoding, basis_state, initialize
from .standard_gates import standard_gate
from .templates import efficient_su2, qft, real_amplitudes, two_local, zz_feature_map

__all__ = [
    "amplitude_encoding",
    "basis_state",
    "efficient_su2",
    "initialize",
    "integer_comparator",
    "qft",
    "real_amplitudes",
    "standard_gate",
    "two_local",
    "weighted_adder",
    "zz_feature_map",
]
