# Copyright 2026 QuantumBridge Contributors.
# Licensed under the Apache License, Version 2.0.
# This file is independently implemented for QuantumBridge SDK.
# No source code from Qiskit or PennyLane was copied.
# Design source: docs/roadmap/p2_upstream_integration_strategy_v0.1.md.

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable


@dataclass(frozen=True)
class FermionicOp:
    terms: tuple[tuple[str, complex], ...]
    register_length: int | None = None

    def __init__(self, terms: dict[str, complex] | Iterable[tuple[str, complex]], register_length: int | None = None):
        items = terms.items() if isinstance(terms, dict) else terms
        normalized = tuple((str(label).strip(), complex(coeff)) for label, coeff in items)
        object.__setattr__(self, "terms", normalized)
        if register_length is None:
            max_index = -1
            for label, _ in normalized:
                for token in label.split():
                    if "_" in token:
                        max_index = max(max_index, int(token.split("_", 1)[1]))
            register_length = max_index + 1 if max_index >= 0 else 0
        object.__setattr__(self, "register_length", int(register_length))

    def normal_ordered(self) -> "FermionicOp":
        ordered = []
        for label, coeff in self.terms:
            tokens = label.split()
            creations = [tok for tok in tokens if tok.startswith("+")]
            annihilations = [tok for tok in tokens if tok.startswith("-")]
            ordered.append((" ".join(creations + annihilations), coeff))
        return FermionicOp(ordered, self.register_length)

    def to_dict(self) -> dict[str, complex]:
        return dict(self.terms)
