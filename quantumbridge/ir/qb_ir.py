# Copyright 2026 QuantumBridge Contributors.
# Licensed under the Apache License, Version 2.0.
# This file is part of QuantumBridge SDK.
# This implementation is developed for the QuantumBridge native architecture.
# Design source: docs/mvp/ir_design_v0.1.md.

from __future__ import annotations

from dataclasses import dataclass, field
from numbers import Real
from typing import Any, Optional

from quantumbridge.core.parameters import Parameter


def _param_to_ir(value: Any) -> Any:
    if isinstance(value, Parameter):
        return {"parameter": value.name}
    if isinstance(value, Real):
        return float(value)
    return value


@dataclass(frozen=True)
class IRInstruction:
    op: str
    targets: tuple[int, ...]
    controls: tuple[int, ...] = ()
    params: tuple[Any, ...] = ()
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "op": self.op,
            "targets": list(self.targets),
            "controls": list(self.controls),
            "params": [_param_to_ir(param) for param in self.params],
            "metadata": {key: value for key, value in self.metadata.items() if key != "matrix"},
        }


@dataclass(frozen=True)
class IRMeasurement:
    kind: str
    wire: int
    bit: int

    def to_dict(self) -> dict[str, Any]:
        return {"kind": self.kind, "wires": [self.wire], "bits": [self.bit]}


@dataclass(frozen=True)
class IRProgram:
    ir_version: str
    num_qubits: int
    num_bits: int
    instructions: tuple[IRInstruction, ...]
    measurements: tuple[IRMeasurement, ...] = ()
    name: Optional[str] = None
    metadata: dict[str, Any] = field(default_factory=dict)

    @classmethod
    def from_circuit(cls, circuit) -> "IRProgram":
        return cls(
            ir_version="qb-ir-v0.1",
            num_qubits=circuit.num_qubits,
            num_bits=circuit.num_bits,
            instructions=tuple(
                IRInstruction(op.name, op.targets, op.controls, op.params, op.metadata) for op in circuit.operations
            ),
            measurements=tuple(IRMeasurement(item.kind, item.wire, item.bit) for item in circuit.measurements),
            name=circuit.name,
            metadata=dict(circuit.metadata),
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "ir_version": self.ir_version,
            "name": self.name,
            "registers": {
                "quantum": {"size": self.num_qubits},
                "classical": {"size": self.num_bits},
            },
            "instructions": [instruction.to_dict() for instruction in self.instructions],
            "measurements": [measurement.to_dict() for measurement in self.measurements],
            "metadata": dict(self.metadata),
        }
