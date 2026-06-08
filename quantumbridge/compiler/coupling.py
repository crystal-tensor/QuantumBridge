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

    def is_connected(self, a: int, b: int) -> bool:
        edge = (int(a), int(b))
        return edge in self.edges or (edge[1], edge[0]) in self.edges

    def neighbors(self, wire: int) -> tuple[int, ...]:
        out = []
        for a, b in self.edges:
            if a == wire:
                out.append(b)
            elif b == wire:
                out.append(a)
        return tuple(sorted(set(out)))
