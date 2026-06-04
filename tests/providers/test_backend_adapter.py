# Copyright 2026 QuantumBridge Contributors.
# Licensed under the Apache License, Version 2.0.
# This file is part of QuantumBridge SDK.
# This implementation is developed for the QuantumBridge native architecture.

from quantumbridge import Circuit
from quantumbridge.providers import Provider


def test_backend_job_result_adapter():
    backend = Provider().get_backend("statevector")
    job = backend.run(Circuit(1).h(0))
    assert job.status == "DONE"
    assert job.result().probabilities()["0"] == job.result().probabilities()["1"]
