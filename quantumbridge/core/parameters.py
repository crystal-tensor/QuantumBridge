# Copyright 2026 QuantumBridge Contributors.
# Licensed under the Apache License, Version 2.0.
# This file is part of QuantumBridge SDK.
# This implementation is developed for the QuantumBridge native architecture.
# Design source: docs/mvp/api_contract_v0.1.md and docs/mvp/mvp_scope_v0.1.md.

from __future__ import annotations

from dataclasses import dataclass
from numbers import Real
from typing import Mapping, Union


@dataclass(frozen=True)
class Parameter:
    """Named scalar parameter used by QuantumBridge circuits."""

    name: str

    def __post_init__(self) -> None:
        if not isinstance(self.name, str) or not self.name:
            raise ValueError("QuantumBridge parameter names must be non-empty strings.")

    def __repr__(self) -> str:
        return f"Parameter({self.name!r})"


ParameterValue = Union[Real, Parameter]


def resolve_parameter(value: ParameterValue, mapping: Mapping[Union[Parameter, str], Real]) -> Real:
    if isinstance(value, Parameter):
        if value in mapping:
            return mapping[value]
        if value.name in mapping:
            return mapping[value.name]
        raise ValueError(f"QuantumBridge parameter {value.name!r} is not bound.")
    if isinstance(value, Real):
        return value
    raise TypeError("QuantumBridge parameters must be real numbers or Parameter objects.")
