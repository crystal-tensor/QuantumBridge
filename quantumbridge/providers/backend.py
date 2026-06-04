# Copyright 2026 QuantumBridge Contributors.
# Licensed under the Apache License, Version 2.0.
# This file is part of QuantumBridge SDK.
# This implementation is developed for the QuantumBridge native architecture.

from quantumbridge.devices import StatevectorDevice
from .job import Job


class Backend:
    def __init__(self, name: str = "quantumbridge_statevector", device=None):
        self.name = name
        self.device = device or StatevectorDevice()

    def run(self, circuit) -> Job:
        return Job(job_id=f"{self.name}-local-1", _result=self.device.run(circuit))

