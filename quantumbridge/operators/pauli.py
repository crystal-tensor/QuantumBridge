# Copyright 2026 QuantumBridge Contributors.
# Licensed under the Apache License, Version 2.0.
# This file is part of QuantumBridge SDK.
# This implementation is developed for the QuantumBridge native architecture.

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Pauli:
    label: str

    def __post_init__(self) -> None:
        normalized = self.label.upper()
        if normalized not in {"I", "X", "Y", "Z"}:
            raise ValueError("QuantumBridge Pauli labels must be I, X, Y, or Z.")
        object.__setattr__(self, "label", normalized)

    def __matmul__(self, other: "Pauli") -> tuple[complex, "Pauli"]:
        table = {
            ("I", "I"): (1, "I"),
            ("I", "X"): (1, "X"),
            ("I", "Y"): (1, "Y"),
            ("I", "Z"): (1, "Z"),
            ("X", "I"): (1, "X"),
            ("Y", "I"): (1, "Y"),
            ("Z", "I"): (1, "Z"),
            ("X", "X"): (1, "I"),
            ("Y", "Y"): (1, "I"),
            ("Z", "Z"): (1, "I"),
            ("X", "Y"): (1j, "Z"),
            ("Y", "Z"): (1j, "X"),
            ("Z", "X"): (1j, "Y"),
            ("Y", "X"): (-1j, "Z"),
            ("Z", "Y"): (-1j, "X"),
            ("X", "Z"): (-1j, "Y"),
        }
        phase, label = table[(self.label, other.label)]
        return phase, Pauli(label)
