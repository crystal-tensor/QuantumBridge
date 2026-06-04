# Copyright 2026 QuantumBridge Contributors.
# Licensed under the Apache License, Version 2.0.
# This file is part of QuantumBridge SDK.
# This implementation is developed for the QuantumBridge native architecture.

from dataclasses import dataclass


@dataclass
class Job:
    job_id: str
    _result: object
    status: str = "DONE"

    def result(self):
        return self._result

