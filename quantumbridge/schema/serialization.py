# Copyright 2026 QuantumBridge Contributors.
# Licensed under the Apache License, Version 2.0.
# This file is independently implemented for QuantumBridge SDK.
# No source code from Qiskit or PennyLane was copied.
# Design source: docs/roadmap/p2_execution_plan_v0.1.md.

from __future__ import annotations

import json
from typing import Any


def to_json(payload: dict[str, Any], *, indent: int | None = None) -> str:
    return json.dumps(payload, sort_keys=True, indent=indent)


def from_json(text: str) -> dict[str, Any]:
    return json.loads(text)
