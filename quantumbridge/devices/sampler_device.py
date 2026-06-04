# Copyright 2026 QuantumBridge Contributors.
# Licensed under the Apache License, Version 2.0.
# This file is part of QuantumBridge SDK.
# This implementation is developed for the QuantumBridge native architecture.
# Design source: docs/mvp/simulator_design_v0.1.md and docs/mvp/api_contract_v0.1.md.

from __future__ import annotations

from numbers import Real
from typing import Mapping, Optional, Union

import numpy as np

from quantumbridge.core.parameters import Parameter
from quantumbridge.results import Result
from .statevector_device import StatevectorDevice


class ShotSampler:
    """Seeded sampler over exact MVP statevector probabilities."""

    def __init__(self, shots: int, seed: Optional[int] = None, base_device: Optional[StatevectorDevice] = None, noise_model=None) -> None:
        if not isinstance(shots, int) or shots <= 0:
            raise ValueError("QuantumBridge sampler shots must be a positive integer.")
        self.shots = shots
        self.seed = seed
        self.base_device = base_device or StatevectorDevice()
        self.noise_model = noise_model

    def run(self, circuit, parameters: Optional[Mapping[Union[Parameter, str], Real]] = None) -> Result:
        probabilities = self.base_device.probabilities(circuit, parameters=parameters)
        labels = sorted(probabilities)
        weights = np.array([probabilities[label] for label in labels], dtype=float)
        weights = weights / weights.sum()
        rng = np.random.default_rng(self.seed)
        draws = rng.choice(labels, size=self.shots, p=weights)
        counts = {label: int(np.count_nonzero(draws == label)) for label in labels}
        counts = {label: count for label, count in counts.items() if count}
        empirical = {label: count / self.shots for label, count in counts.items()}
        return Result(
            probabilities_data=empirical,
            counts_data=counts,
            metadata_data={
                "device": "ShotSampler",
                "shots": self.shots,
                "seed": self.seed,
                "source": "StatevectorDevice probabilities",
                "qubit_order": "q0-first bitstrings",
                "noise_model": None if self.noise_model is None else self.noise_model.summary(),
            },
        )
