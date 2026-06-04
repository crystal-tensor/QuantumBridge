# Copyright 2026 QuantumBridge Contributors.
# Licensed under the Apache License, Version 2.0.
# This file is part of QuantumBridge SDK.
# This implementation is developed for the QuantumBridge native architecture.
# Design source: docs/mvp/api_contract_v0.1.md and docs/mvp/simulator_design_v0.1.md.

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Optional, Union

import numpy as np


def _complex_list(values: Optional[np.ndarray]) -> Optional[list[dict[str, float]]]:
    if values is None:
        return None
    return [{"real": float(np.real(value)), "imag": float(np.imag(value))} for value in values]


@dataclass
class Result:
    state: Optional[np.ndarray] = None
    probabilities_data: Optional[dict[str, float]] = None
    counts_data: Optional[dict[str, int]] = None
    expectation_data: Optional[Union[float, dict[str, float]]] = None
    metadata_data: dict[str, Any] = field(default_factory=dict)
    trace: Optional[list[dict[str, Any]]] = None

    def statevector(self) -> Optional[np.ndarray]:
        return None if self.state is None else self.state.copy()

    def probabilities(self) -> Optional[dict[str, float]]:
        return None if self.probabilities_data is None else dict(self.probabilities_data)

    def counts(self) -> Optional[dict[str, int]]:
        return None if self.counts_data is None else dict(self.counts_data)

    def expectation_value(self):
        return self.expectation_data

    def metadata(self) -> dict[str, Any]:
        return dict(self.metadata_data)

    def to_dict(self) -> dict[str, Any]:
        return {
            "statevector": _complex_list(self.state),
            "probabilities": self.probabilities(),
            "counts": self.counts(),
            "expectation": self.expectation_data,
            "metadata": self.metadata(),
            "trace": self.trace,
        }
