# Copyright 2026 QuantumBridge Contributors.
# Licensed under the Apache License, Version 2.0.
# This file is part of QuantumBridge SDK.
# This implementation is developed for the QuantumBridge native architecture.

from quantumbridge.devices import StatevectorDevice
from quantumbridge.results import Result
from typing import Optional


class Estimator:
    def __init__(self, device: Optional[StatevectorDevice] = None):
        self.device = device or StatevectorDevice()

    def run(self, circuit, observable) -> Result:
        value = self.device.expectation(circuit, observable)
        return Result(expectation_data=value, metadata_data={"primitive": "Estimator"})
