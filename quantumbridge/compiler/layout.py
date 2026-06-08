# Copyright 2026 QuantumBridge Contributors.
# Licensed under the Apache License, Version 2.0.
# This file is part of QuantumBridge SDK.
# This implementation is developed for the QuantumBridge native architecture.


def identity_layout(num_qubits: int) -> dict[int, int]:
    return {wire: wire for wire in range(num_qubits)}


class Layout:
    def __init__(self, mapping):
        self.mapping = {int(logical): int(physical) for logical, physical in dict(mapping).items()}

    @classmethod
    def trivial(cls, num_qubits: int) -> "Layout":
        return cls(identity_layout(num_qubits))

    def physical(self, logical: int) -> int:
        return self.mapping[int(logical)]

    def to_dict(self) -> dict[int, int]:
        return dict(self.mapping)
