# Copyright 2026 QuantumBridge Contributors.
# Licensed under the Apache License, Version 2.0.
# This file is part of QuantumBridge SDK.
# This implementation is developed for the QuantumBridge native architecture.

from dataclasses import dataclass


@dataclass(frozen=True)
class Target:
    num_qubits: int
    basis_gates: tuple[str, ...]

