# Copyright 2026 QuantumBridge Contributors.
# Licensed under the Apache License, Version 2.0.
# This file is part of QuantumBridge SDK.
# This implementation is developed for the QuantumBridge native architecture.
# Design source: docs/mvp/ir_design_v0.1.md.

from __future__ import annotations

from dataclasses import dataclass, field
from numbers import Real
from typing import Any, Optional

from quantumbridge.core.parameters import Parameter, ParameterExpression


def matrix_from_ir(value):
    import numpy as np
    from quantumbridge.execution.resource_context import current_resources
    scope = current_resources()
    if scope is not None:
        from quantumbridge.execution.array_reservations import numeric_array, numeric_shape, numeric_into
        from quantumbridge.execution.array_ownership import retained_array
        if type(value) is dict and set(value) == {"real", "imag"}:
            shape = numeric_shape(value["real"], real_only=True)
            if shape != numeric_shape(value["imag"], real_only=True):
                raise ValueError("QuantumBridge matrix real/imag shapes must match.")
            result = retained_array(scope.ledger, "ir_complex_conversion", shape, complex)
            scope.ledger.unavailable("ir_python_conversion_workspace",
                "IR conversion owns its complex output; Python containers and internal iterator workspace are not measured RSS.")
            numeric_into(result.real, value["real"])
            numeric_into(result.imag, value["imag"])
            return result
        return numeric_array(value, category="ir_numeric_conversion")

    if isinstance(value, dict) and set(value) == {"real", "imag"}:
        real, imag = np.asarray(value["real"]), np.asarray(value["imag"])
        if real.shape != imag.shape:
            raise ValueError("QuantumBridge matrix real/imag shapes must match.")
        return real.astype(float) + 1j * imag.astype(float)
    return np.asarray(value, dtype=complex)


def decode_instruction_metadata(metadata):
    result = dict(metadata)
    if "matrix" in result:
        result["matrix"] = matrix_from_ir(result["matrix"])
    if "kraus" in result:
        result["kraus"] = tuple(matrix_from_ir(value) for value in result["kraus"])
    if "control_node" in result and isinstance(result["control_node"], dict):
        from quantumbridge.core.control_flow import ControlBlock
        result["control_node"] = ControlBlock.from_dict(result["control_node"])
    return result


def _matrix_to_ir(value):
    matrix = matrix_from_ir(value)
    return {"real": matrix.real.tolist(), "imag": matrix.imag.tolist()}


def _param_to_ir(value: Any) -> Any:
    if isinstance(value, Parameter):
        return {"parameter": value.name, **({"parameter_uuid": value.uuid} if value.uuid is not None else {})}
    if isinstance(value, ParameterExpression):
        return {
            "expression": str(value),
            "parameters": sorted(parameter.name for parameter in value.parameters),
            "parameter_ast": {"op": value.op, "args": [_param_to_ir(arg) for arg in value.args]},
        }
    if isinstance(value, Real):
        return float(value)
    return value


def param_from_ir(value):
    if not isinstance(value, dict): return value
    if set(value) in ({"parameter"}, {"parameter","parameter_uuid"}): return Parameter(value["parameter"],value.get("parameter_uuid"))
    if "parameter_ast" in value:
        tree = value["parameter_ast"]
        if tree["op"] not in {"const", "parameter", "neg", "+", "-", "*", "/", "**"}:
            raise ValueError("Unknown executable QuantumBridge parameter AST.")
        args = tuple(param_from_ir(arg) for arg in tree["args"])
        return ParameterExpression(tree["op"], args)
    raise ValueError("QuantumBridge parameter expressions require an executable AST, not text.")


@dataclass(frozen=True)
class IRInstruction:
    op: str
    targets: tuple[int, ...]
    controls: tuple[int, ...] = ()
    params: tuple[Any, ...] = ()
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        metadata = {key: value for key, value in self.metadata.items() if key not in {"matrix", "kraus"}}
        if "matrix" in self.metadata:
            metadata["matrix"] = _matrix_to_ir(self.metadata["matrix"])
        if "kraus" in self.metadata:
            metadata["kraus"] = [_matrix_to_ir(value) for value in self.metadata["kraus"]]
        if "control_node" in self.metadata:
            metadata["control_node"] = self.metadata["control_node"].to_dict()
        return {
            "op": self.op,
            "targets": list(self.targets),
            "controls": list(self.controls),
            "params": [_param_to_ir(param) for param in self.params],
            "metadata": metadata,
        }


@dataclass(frozen=True)
class IRMeasurement:
    kind: str
    wire: int
    bit: int
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        result = {"kind": self.kind, "wires": [self.wire], "bits": [self.bit]}
        if self.metadata:
            result["metadata"] = dict(self.metadata)
        return result


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
    def from_dict(cls, data, validate=True):
        if data.get("ir_version") != "qb-ir-v0.1": raise ValueError("Unknown QuantumBridge IR version.")
        registers = data["registers"]
        result = cls(data["ir_version"], registers["quantum"]["size"], registers["classical"]["size"],
            tuple(IRInstruction(item["op"], tuple(item["targets"]), tuple(item.get("controls", ())),
                tuple(param_from_ir(value) for value in item.get("params", ())), decode_instruction_metadata(item.get("metadata", {}))) for item in data["instructions"]),
            tuple(IRMeasurement(item["kind"], item["wires"][0], item["bits"][0], dict(item.get("metadata", {}))) for item in data.get("measurements", ())), data.get("name"), dict(data.get("metadata", {})))
        if "global_phase" in result.metadata:
            result.metadata["global_phase"] = param_from_ir(result.metadata["global_phase"])
        if validate: result.validate()
        return result

    @classmethod
    def from_json(cls, text, *, serialization_limits=None):
        from quantumbridge.schema.serialization import from_json
        return cls.from_dict(from_json(text, limits=serialization_limits))

    def to_json(self, *, serialization_limits=None):
        from quantumbridge.schema.serialization import to_json
        return to_json(self.to_dict(), limits=serialization_limits)

    def validate(self):
        from quantumbridge.compat.qiskit_adapter import circuit_from_ir
        from quantumbridge.core.control_flow import validate_control_flow
        if self.ir_version != "qb-ir-v0.1": raise ValueError("Unknown QuantumBridge IR version.")
        validate_control_flow(circuit_from_ir(self))
        return True

    @classmethod
    def from_circuit(cls, circuit) -> "IRProgram":
        return cls(
            ir_version="qb-ir-v0.1",
            num_qubits=circuit.num_qubits,
            num_bits=circuit.num_bits,
            instructions=tuple(
                IRInstruction(op.name, op.targets, op.controls, op.params, op.metadata) for op in circuit.operations
            ),
            measurements=tuple(IRMeasurement(item.kind, item.wire, item.bit, dict(item.metadata)) for item in circuit.measurements),
            name=circuit.name,
            metadata=dict(circuit.metadata),
        )

    def to_dict(self) -> dict[str, Any]:
        metadata = dict(self.metadata)
        if "global_phase" in metadata: metadata["global_phase"] = _param_to_ir(metadata["global_phase"])
        return {
            "ir_version": self.ir_version,
            "name": self.name,
            "registers": {
                "quantum": {"size": self.num_qubits},
                "classical": {"size": self.num_bits},
            },
            "instructions": [instruction.to_dict() for instruction in self.instructions],
            "measurements": [measurement.to_dict() for measurement in self.measurements],
            "metadata": metadata,
        }
