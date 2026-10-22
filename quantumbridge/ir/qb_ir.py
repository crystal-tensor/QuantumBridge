# Copyright 2026 QuantumBridge Contributors.
# Licensed under the Apache License, Version 2.0.
# This file is part of QuantumBridge SDK.
# This implementation is developed for the QuantumBridge native architecture.
# Design source: docs/mvp/ir_design_v0.1.md.

from __future__ import annotations

from dataclasses import dataclass, field
from numbers import Real
from typing import Any, Optional

from quantumbridge.core.parameters import Parameter, ParameterExpression, ParameterVector, ParameterVectorElement, legacy_parameter, EXPRESSION_OPS


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


def decode_instruction_metadata(metadata, *, _vectors=None, _limits=None):
    result = dict(metadata)
    if "matrix" in result:
        result["matrix"] = matrix_from_ir(result["matrix"])
    if "kraus" in result:
        result["kraus"] = tuple(matrix_from_ir(value) for value in result["kraus"])
    if "control_node" in result and isinstance(result["control_node"], dict):
        from quantumbridge.core.control_flow import ControlBlock
        result["control_node"] = ControlBlock.from_dict(result["control_node"],
            serialization_limits=_limits, _parameter_vectors=_vectors)
    if isinstance(result.get("instruction"),dict) and "params" in result["instruction"]:
        result["instruction"]=dict(result["instruction"])
        result["instruction"]["params"]=[param_from_ir(value,_vectors=_vectors,_limits=_limits) if isinstance(value,dict)
            and ("parameter" in value or "parameter_ast" in value) else value for value in result["instruction"]["params"]]
    return result


def _matrix_to_ir(value):
    matrix = matrix_from_ir(value)
    return {"real": matrix.real.tolist(), "imag": matrix.imag.tolist()}


def _param_to_ir(value: Any) -> Any:
    if isinstance(value, Parameter):
        result={"parameter":value.name,"parameter_uuid":value.uuid}
        if not value._uuid_explicit:result["parameter_uuid_explicit"]=False
        if isinstance(value,ParameterVectorElement):
            result["parameter_vector"]={"name":value._vector_name,"root_uuid":value.vector._root_uuid,
                "length":len(value.vector),"index":value.index}
        return result
    if isinstance(value, ParameterExpression):
        return {
            "expression": str(value),
            "parameters": sorted(parameter.name for parameter in value.parameters),
            "parameter_ast": {"op": value.op, "args": [_param_to_ir(arg) for arg in value.args]},
        }
    if isinstance(value, Real):
        return float(value)
    if isinstance(value, complex):
        return {"parameter_complex": [value.real, value.imag]}
    return value


def param_from_ir(value, *, _vectors=None, _limits=None, _depth=0):
    if not isinstance(value, dict): return value
    vectors={} if _vectors is None else _vectors
    from quantumbridge.serialization.limits import SerializationLimits
    limits = _limits or SerializationLimits()
    limits.check("max_symbolic_expression_depth", _depth, format="ir-json")
    count = vectors.get("expression_nodes", 0) + 1
    limits.check("max_parameter_nodes", count, format="ir-json")
    vectors["expression_nodes"] = count
    if "parameter_complex" in value:
        parts = value["parameter_complex"]
        if set(value) != {"parameter_complex"} or type(parts) not in (tuple, list) or len(parts) != 2 or not all(isinstance(part, Real) for part in parts):
            raise ValueError("Malformed complex scalar parameter literal.")
        from quantumbridge.core.parameters import _checked_numeric
        return _checked_numeric(complex(*parts))
    if "parameter" in value:
        if not set(value)<={"parameter","parameter_uuid","parameter_uuid_explicit","parameter_vector"}:
            raise ValueError("Unknown QuantumBridge parameter identity fields.")
        if "parameter_uuid_explicit" in value and type(value["parameter_uuid_explicit"]) is not bool:
            raise ValueError("Parameter identity provenance must be a boolean.")
        name,identity=value["parameter"],value.get("parameter_uuid")
        spec=value.get("parameter_vector")
        if spec is None:
            parameter=legacy_parameter(name) if identity is None else Parameter(name,identity)
        else:
            from uuid import UUID
            from quantumbridge.serialization.limits import SerializationLimits
            if type(spec) is not dict or set(spec)!={"name","root_uuid","length","index"}:
                raise ValueError("Malformed parameter vector identity.")
            if type(spec["length"]) is not int or type(spec["index"]) is not int or min(spec["length"],spec["index"])<0:
                raise ValueError("Parameter vector lengths/indices must be nonnegative integers.")
            if type(spec["name"]) is not str or type(spec["root_uuid"]) is not str or type(identity) is not str:
                raise ValueError("Parameter vector identity fields must be strings.")
            limits=_limits or SerializationLimits()
            limits.check("max_parameter_nodes",spec["length"],format="ir-json")
            root_uuid=str(UUID(spec["root_uuid"]))
            identity=str(UUID(identity))
            index=spec["index"]
            if name!=f"{spec['name']}[{index}]":raise ValueError("Vector parameter name does not match its index.")
            key=(spec["name"],root_uuid,spec["length"])
            if key not in vectors:
                count=vectors.get(None,0)+spec["length"]
                limits.check("max_parameter_nodes",count,format="ir-json")
                vector=ParameterVector(spec["name"])
                vector._root_uuid=root_uuid
                vector.resize(spec["length"])
                vectors[key]=vector
                vectors[None]=count
            vector=vectors[key]
            parameter=vector[index] if index<len(vector) and vector[index].uuid==identity else ParameterVectorElement(vector,index,identity)
        if "parameter_uuid_explicit" in value:
            object.__setattr__(parameter,"_uuid_explicit",value["parameter_uuid_explicit"])
        return parameter
    if "parameter_ast" in value:
        tree = value["parameter_ast"]
        if type(tree) is not dict or set(tree) != {"op", "args"} or tree["op"] not in EXPRESSION_OPS or type(tree["args"]) not in (tuple, list):
            raise ValueError("Unknown executable QuantumBridge parameter AST.")
        args = tuple(param_from_ir(arg,_vectors=vectors,_limits=limits,_depth=_depth+1) for arg in tree["args"])
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
        if isinstance(metadata.get("instruction"),dict) and "params" in metadata["instruction"]:
            metadata["instruction"]=dict(metadata["instruction"])
            metadata["instruction"]["params"]=[_param_to_ir(value) for value in metadata["instruction"]["params"]]
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
    def from_dict(cls, data, validate=True, *, serialization_limits=None, _parameter_vectors=None):
        if data.get("ir_version") != "qb-ir-v0.1": raise ValueError("Unknown QuantumBridge IR version.")
        registers = data["registers"]
        vectors={} if _parameter_vectors is None else _parameter_vectors
        result = cls(data["ir_version"], registers["quantum"]["size"], registers["classical"]["size"],
            tuple(IRInstruction(item["op"], tuple(item["targets"]), tuple(item.get("controls", ())),
                tuple(param_from_ir(value,_vectors=vectors,_limits=serialization_limits) for value in item.get("params", ())),
                decode_instruction_metadata(item.get("metadata", {}),_vectors=vectors,_limits=serialization_limits)) for item in data["instructions"]),
            tuple(IRMeasurement(item["kind"], item["wires"][0], item["bits"][0], dict(item.get("metadata", {}))) for item in data.get("measurements", ())), data.get("name"), dict(data.get("metadata", {})))
        if "global_phase" in result.metadata:
            result.metadata["global_phase"] = param_from_ir(result.metadata["global_phase"],_vectors=vectors,_limits=serialization_limits)
        if validate: result.validate()
        return result

    @classmethod
    def from_json(cls, text, *, serialization_limits=None):
        from quantumbridge.schema.serialization import from_json
        from quantumbridge.core.symbolic_limits import symbolic_serialization_limits
        serialization_limits = symbolic_serialization_limits(serialization_limits)
        return cls.from_dict(from_json(text, limits=serialization_limits),serialization_limits=serialization_limits)

    def to_json(self, *, serialization_limits=None):
        from quantumbridge.schema.serialization import to_json
        from quantumbridge.core.symbolic_limits import symbolic_serialization_limits
        serialization_limits = symbolic_serialization_limits(serialization_limits)
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
