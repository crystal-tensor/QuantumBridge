# Copyright 2026 QuantumBridge Contributors.
# Licensed under the Apache License, Version 2.0.
# This file is part of QuantumBridge SDK.
# This implementation is developed for the QuantumBridge native architecture.

from dataclasses import dataclass


@dataclass(frozen=True)
class CouplingMap:
    edges: tuple[tuple[int, int], ...]

    def __init__(self, edges):
        object.__setattr__(self, "edges", tuple((int(a), int(b)) for a, b in edges))

