# Copyright 2026 QuantumBridge Contributors.
# Licensed under the Apache License, Version 2.0.
# This file is part of QuantumBridge SDK.
# This implementation is developed for the QuantumBridge native architecture.

from quantumbridge.devices import ShotSampler


from typing import Optional


class Sampler:
    def __init__(self, shots: int = 1024, seed: Optional[int] = None, noise_model=None):
        self.shots = shots
        self.seed = seed
        self.noise_model = noise_model

    def run(self, circuit):
        return ShotSampler(self.shots, self.seed, noise_model=self.noise_model).run(circuit)
