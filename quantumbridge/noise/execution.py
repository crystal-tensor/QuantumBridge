# Copyright 2026 QuantumBridge Contributors.
# Licensed under the Apache License, Version 2.0.
# This file is independently implemented for QuantumBridge SDK.
# No source code from Qiskit or PennyLane was copied.
# Design source: docs/roadmap/p2_execution_plan_v0.1.md.

from __future__ import annotations

from numbers import Integral

from quantumbridge.devices import DensityMatrixDevice, StatevectorDevice
from quantumbridge.results import Result


def _device_with_noise(base_device, noise_model):
    if base_device is None:
        return DensityMatrixDevice(noise_model=noise_model)
    if hasattr(base_device, "with_noise_model"):
        return base_device.with_noise_model(noise_model)
    if type(base_device) is StatevectorDevice:
        return DensityMatrixDevice(max_qubits=base_device.max_qubits, noise_model=noise_model)
    raise TypeError("QuantumBridge noisy execution needs a device with native noise configuration support.")


class NoisySampler:
    def __init__(self, shots: int, noise_model, seed: int | None = None, base_device=None):
        if isinstance(shots, bool) or not isinstance(shots, Integral) or shots <= 0:
            raise ValueError("QuantumBridge NoisySampler shots must be positive.")
        self.shots = int(shots)
        self.noise_model = noise_model
        self.seed = seed
        self.base_device = base_device or StatevectorDevice()
        self.device = _device_with_noise(base_device, noise_model)

    def probabilities(self, circuit) -> dict[str, float]:
        return self.device.run(circuit).probabilities()

    def run(self, circuit) -> Result:
        result = self.device.run_shots(circuit, shots=self.shots, seed=self.seed)
        result.metadata_data.update({"device": "NoisySampler", "provenance": {"mode": "Native Core", "component": "quantumbridge.noise"}})
        return result


class NoisyEstimator:
    def __init__(self, noise_model, seed: int | None = None, base_device=None):
        self.noise_model = noise_model
        self.seed = seed
        self.base_device = base_device or StatevectorDevice()
        self.device = _device_with_noise(base_device, noise_model)

    def expectation(self, circuit, observable) -> float:
        return self.device.expectation(circuit, observable)

    def run(self, circuit, observable) -> Result:
        value = self.expectation(circuit, observable)
        return Result(
            expectation_data=value,
            metadata_data={
                "device": "NoisyEstimator",
                "seed": self.seed,
                "noise_model_metadata": {} if self.noise_model is None else self.noise_model.summary(),
                "provenance": {"mode": "Native Core", "component": "quantumbridge.noise"},
            },
        )
