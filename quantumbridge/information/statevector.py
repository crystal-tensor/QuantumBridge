# Copyright 2026 QuantumBridge Contributors.
# Licensed under the Apache License, Version 2.0.
# This file is part of QuantumBridge SDK.
# This implementation is developed for the QuantumBridge native architecture.

from __future__ import annotations

import numpy as np

from quantumbridge.devices import StatevectorDevice
from quantumbridge.utils.math import probabilities_from_state


class Statevector:
    def __init__(self, data):
        self.data = np.asarray(data, dtype=complex)

    @classmethod
    def from_circuit(cls, circuit) -> "Statevector":
        return cls(StatevectorDevice().statevector(circuit))

    def probabilities(self) -> dict[str, float]:
        num_qubits = int(np.log2(len(self.data)))
        return probabilities_from_state(self.data, num_qubits)

