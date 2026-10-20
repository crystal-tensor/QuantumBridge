# Copyright 2026 QuantumBridge Contributors.
# Licensed under the Apache License, Version 2.0.
"""Immutable requests for native numerical plans, not upstream SDK dispatch."""

from dataclasses import dataclass

from .resource_limits import UnifiedExecutionLimits


@dataclass(frozen=True)
class DerivativeExecutionRequest:
    circuit_or_tape: object
    parameters: object = ()
    derivative_order: int = 1
    method: str = "best"
    derivative_kind: str = "jacobian"
    cotangent: object = None
    tangent: object = None
    shots: object = None
    seed: object = None
    limits: UnifiedExecutionLimits | None = None
    observable: object = None
