# Copyright 2026 QuantumBridge Contributors.
# Licensed under the Apache License, Version 2.0.
# This file is part of QuantumBridge SDK.
# This implementation is developed for the QuantumBridge native architecture.
# Design source: docs/mvp/api_contract_v0.1.md and docs/mvp/simulator_design_v0.1.md.

from __future__ import annotations

from collections.abc import MutableSequence
from copy import deepcopy
from dataclasses import dataclass, field
from typing import Any

from .parameters import ParameterValue

_UNSET = object()


def instruction_definition_work(circuit, *, owner=None, params=None):
    """Bound a definition graph without requiring its operations to be unitary."""
    from .circuit import Circuit
    from .control_flow import ControlBlock
    from .gate_limits import current_gate_limits
    from .instruction_parameters import admit_owner, admit_payloads
    from .gates import is_native_instruction
    from .annotated_operation import _inspect
    limits = current_gate_limits()
    from quantumbridge.execution.resource_context import current_resources
    managed = current_resources() is not None
    stack = [(circuit, 0, frozenset(() if owner is None else (id(owner),)))]
    total = definitions = 0
    while stack:
        body, depth, ancestors = stack.pop()
        if type(body) is not Circuit: raise TypeError("An instruction definition needs a native Circuit.")
        if managed and (type(body.operations) is not list or type(body.measurements) is not list or type(body.metadata) is not dict):
            from .classical import UnsupportedFeature
            raise UnsupportedFeature("managed_instruction_definition_container")
        if id(body) in ancestors: raise ValueError("Cyclic instruction definition.")
        limits.check("max_definition_depth", depth)
        definitions += 1
        limits.check("max_custom_definitions", definitions)
        total += len(body.operations)+len(body.measurements)
        limits.check("max_total_operations", total)
        limits.check("max_decomposition_work", total+definitions)
        ancestors = ancestors | {id(body)}
        for operation in body.operations:
            if managed and (type(operation) is not Operation or type(operation.metadata) is not dict):
                from .classical import UnsupportedFeature
                raise UnsupportedFeature("managed_instruction_definition_operation")
            node = operation.metadata.get("control_node")
            if node is not None:
                if type(node) is not ControlBlock: raise TypeError("Unknown native control definition.")
                if managed and type(node.data) is not dict:
                    from .classical import UnsupportedFeature
                    raise UnsupportedFeature("managed_instruction_control_data")
                stack.extend((child, depth+1, ancestors) for child in node.bodies)
            child = operation.metadata.get("gate", operation.metadata.get("instruction_object"))
            annotation = operation.metadata.get("annotated_operation")
            if sum(operation.metadata.get(key) is not None for key in ("gate", "instruction_object", "annotated_operation")) > 1:
                raise ValueError("An invocation cannot have multiple operation owners.")
            if annotation is not None: child = _inspect(annotation)[0]
            if child is not None:
                if not is_native_instruction(child): raise TypeError("Unknown native instruction definition.")
                admit_owner(child)
                if id(child) in ancestors: raise ValueError("Cyclic instruction definition.")
                from .standard_gates import invocation_params
                actual_owner=annotation if annotation is not None else child
                if (operation.name != actual_owner.name or operation.controls
                        or len(operation.targets) != actual_owner.num_qubits
                        or tuple(operation.params) != invocation_params(actual_owner)):
                    raise ValueError("Instruction definition invocation differs from its operation owner.")
                if child.definition is not None:
                    stack.append((child.definition, depth+1, ancestors | {id(child)}))
    if owner is not None:
        from .parameters import parameter_set
        admit_payloads(tuple(owner.params if params is None else params))
        if not set(circuit.parameters) <= set(parameter_set(owner.params if params is None else params)):
            raise ValueError("Instruction definition parameter namespace differs from its owner.")
    return total


@dataclass(init=False)
class Instruction:
    """Qiskit-style instruction object with optional circuit definition."""

    name: str
    num_qubits: int
    num_bits: int = 0
    params: MutableSequence[Any] = ()
    definition: Any = None
    metadata: dict[str, Any] = field(default_factory=dict)
    label: str | None = None

    def __init__(self, name, num_qubits, num_clbits=_UNSET, params=(), label=None, *, definition=None, metadata=None, num_bits=_UNSET):
        from .instruction_parameters import admit_owner, admit_payloads
        admit_owner(self)
        if num_clbits is not _UNSET and num_bits is not _UNSET:
            raise TypeError("Classical width was provided by both num_clbits and num_bits.")
        num_bits = num_clbits if num_clbits is not _UNSET else 0 if num_bits is _UNSET else num_bits
        admit_payloads((name, num_qubits, num_bits, label))
        if label is not None and not isinstance(label, str): raise TypeError("Instruction label must be a string or None.")
        object.__setattr__(self, "name", name)
        object.__setattr__(self, "num_qubits", num_qubits)
        object.__setattr__(self, "num_bits", num_bits)
        object.__setattr__(self, "_params", ())
        object.__setattr__(self, "_definition", None)
        object.__setattr__(self, "_parameter_plan", None)
        object.__setattr__(self, "metadata", dict(metadata or {}))
        object.__setattr__(self, "label", label)
        self.__post_init__()
        from .instruction_parameters import validated_values
        object.__setattr__(self, "_params", validated_values(self, params))
        self.definition = definition

    def __post_init__(self) -> None:
        if not isinstance(self.name, str) or not self.name:
            raise ValueError("QuantumBridge instructions require a non-empty name.")
        from .errors import CircuitError
        if not isinstance(self.num_qubits, int) or not isinstance(self.num_bits, int):
            raise CircuitError("Instruction quantum and classical widths must be integers.")
        if self.num_qubits < 0 or self.num_bits < 0:
            raise CircuitError("Instruction quantum and classical widths cannot be negative.")
        object.__setattr__(self, "metadata", dict(self.metadata))

    def __setattr__(self, name, value):
        if name in {"params", "definition"}: return object.__setattr__(self, name, value)
        if name in {"name", "label"}:
            if value is None and name == "label": return object.__setattr__(self, name, value)
            if not isinstance(value, str) or name == "name" and not value: raise ValueError("Instruction name/label must be valid strings.")
            return object.__setattr__(self, name, value)
        raise AttributeError("Use params/definition assignment or copy to update a native Instruction.")

    @property
    def base_class(self): return type(self)

    @property
    def mutable(self): return getattr(self, "_mutable", True)

    def to_mutable(self):
        result = self.copy()
        object.__setattr__(result, "_mutable", True)
        return result

    @property
    def num_clbits(self): return self.num_bits

    @property
    def params(self):
        from .instruction_parameters import ParameterList
        return ParameterList(self)

    @params.setter
    def params(self, values):
        from .instruction_parameters import validated_values, prepare_definition_update
        values = validated_values(self, values)
        self._validate_parameter_arity(values)
        definition, plan = prepare_definition_update(self, values)
        metadata = self.metadata
        from .instruction_parameters import same_values
        if definition is not None and "global_phase" in metadata and same_values((metadata["global_phase"],), (self.definition.global_phase,)):
            metadata = {**metadata, "global_phase": definition.global_phase}
        object.__setattr__(self, "_params", values)
        object.__setattr__(self, "_definition", definition)
        object.__setattr__(self, "_parameter_plan", plan)
        object.__setattr__(self, "metadata", metadata)

    def validate_parameter(self, parameter): return parameter

    def _validate_parameter_arity(self, values): pass

    def is_parameterized(self):
        from .parameters import parameter_set
        return bool(parameter_set(self.params))

    def _validate_definition(self, value, params):
        from .circuit import Circuit
        from .instruction_parameters import _managed
        if _managed() and type(value) is not Circuit:
            from .classical import UnsupportedFeature
            raise UnsupportedFeature("managed_instruction_definition")
        if not isinstance(value, Circuit): raise TypeError("An Instruction definition requires a native Circuit.")
        if (value.num_qubits, value.num_bits) != (self.num_qubits, self.num_bits):
            raise ValueError("Instruction definition width differs from its owner.")
        instruction_definition_work(value, owner=self, params=params)

    @property
    def definition(self): return self._definition

    @definition.setter
    def definition(self, value):
        if value is not None: self._validate_definition(value, self._params)
        from .instruction_parameters import owned_copy
        value = owned_copy(value)
        object.__setattr__(self, "_definition", value)
        object.__setattr__(self, "_parameter_plan", None)

    def copy(self, name: str | None = None) -> "Instruction":
        from quantumbridge.execution.array_ownership import native_configuration_copy
        from quantumbridge.execution.resource_context import current_resources
        copied = native_configuration_copy(self, category="native_instruction_copy",
            strict=current_resources() is not None)
        if name is not None:
            if not isinstance(name, str) or not name: raise ValueError("An Instruction copy needs a nonempty name.")
            object.__setattr__(copied, "name", name)
        return copied

    def assign_parameters(self, mapping, *, strict=True):
        from .circuit import _parameter_mapping_from_values
        from .parameters import parameter_set, parameter_sort_key, resolve_parameter
        from .instruction_parameters import admit_owner, inherit_binding_plan, owned_copy
        admit_owner(self)
        values = _parameter_mapping_from_values(tuple(sorted(parameter_set(self.params), key=parameter_sort_key)), mapping, strict)
        if self.definition is not None: instruction_definition_work(self.definition, owner=self)
        metadata = owned_copy(self.metadata)
        if "global_phase" in metadata:
            metadata["global_phase"] = resolve_parameter(metadata["global_phase"], values, allow_partial=True)
        result = Instruction(self.name, self.num_qubits, self.num_bits,
            tuple(resolve_parameter(value, values, allow_partial=True) for value in self.params), self.label,
            definition=None if self.definition is None else self.definition.assign_parameters(values, strict=False), metadata=metadata)
        inherit_binding_plan(self, result)
        return result

    def inverse(self, annotated=False, *, name=None):
        from .instruction_parameters import admit_owner, admit_payloads
        from .errors import CircuitError
        admit_owner(self)
        admit_payloads((annotated, name))
        if annotated:
            from .annotated_operation import AnnotatedOperation, InverseModifier
            return AnnotatedOperation(self, InverseModifier())
        output_name = name or f"{self.name}_dg"
        if self.definition is not None:
            instruction_definition_work(self.definition, owner=self)
            try:
                body = self.definition.inverse()
                return body.to_instruction(name=output_name) if self.num_bits else body.to_gate(_name=output_name)
            except (TypeError, ValueError) as exc:
                raise CircuitError("Instruction inverse is not implemented for this definition.") from exc
        if "matrix" in self.metadata and not self.num_bits:
            from .annotated_operation import _base_gate
            return _base_gate(self).inverse().copy(name=output_name)
        raise CircuitError(f"inverse() is not implemented for {self.name}.")

    def repeat(self, n):
        from .instruction_parameters import admit_owner, admit_payloads
        from .gate_limits import current_gate_limits
        from .errors import CircuitError
        from .circuit import Circuit
        admit_owner(self)
        admit_payloads((n,))
        count = int(n)
        if count < 1 or count != n: raise CircuitError("Repeat requires a strictly positive integral count.")
        limits = current_gate_limits()
        limits.check("max_repeat_count", count)
        work = 1 if self.definition is None else instruction_definition_work(self.definition, owner=self)
        predicted = count*(1+work if self.definition is not None else 1)
        limits.check("max_total_operations", predicted)
        limits.check("max_decomposition_work", predicted)
        if not self.num_qubits:
            from .classical import UnsupportedFeature
            raise UnsupportedFeature("zero_width_instruction_repeat", "A zero-qubit Instruction can be staged, but zero-width Circuit definitions are not implemented yet.")
        body = Circuit(self.num_qubits, self.num_bits)
        for _ in range(count): body._append_instruction_reference(self, range(self.num_qubits), range(self.num_bits))
        return Instruction(f"{self.name}*{count}", self.num_qubits, self.num_bits,
            tuple(self.params), definition=body)

    def power(self, exponent: int, name: str | None = None) -> "Instruction":
        if not isinstance(exponent, int):
            raise ValueError("QuantumBridge Instruction.power requires an integer exponent.")
        if self.definition is not None:
            return self.definition.power(exponent).to_instruction(name=name or f"{self.name}^{exponent}")
        from quantumbridge.core.circuit import Circuit

        circuit = Circuit(self.num_qubits, self.num_bits)
        unit = self.inverse() if exponent < 0 else self
        for _ in range(abs(exponent)):
            circuit.append(unit, range(self.num_qubits), clbits=range(self.num_bits))
        return circuit.to_instruction(name=name or f"{self.name}^{exponent}")

    def control(
        self,
        num_ctrl_qubits: int = 1,
        label: str | None = None,
        ctrl_state: int | None = None,
    ) -> "Instruction":
        if self.definition is not None:
            return self.definition.control(num_ctrl_qubits, label=label or f"c{num_ctrl_qubits}_{self.name}", ctrl_state=ctrl_state).to_instruction(
                name=label or f"c{num_ctrl_qubits}_{self.name}"
            )
        from quantumbridge.core.circuit import Circuit

        circuit = Circuit(self.num_qubits, self.num_bits).append(self, range(self.num_qubits), clbits=range(self.num_bits))
        return circuit.control(num_ctrl_qubits, label=label or f"c{num_ctrl_qubits}_{self.name}", ctrl_state=ctrl_state).to_instruction(
            name=label or f"c{num_ctrl_qubits}_{self.name}"
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "num_qubits": self.num_qubits,
            "num_bits": self.num_bits,
            "params": list(self.params),
            "has_definition": self.definition is not None,
            "metadata": deepcopy(self.metadata),
        }


@dataclass(frozen=True)
class Operation:
    """Value object describing a QuantumBridge MVP operation."""

    name: str
    targets: tuple[int, ...]
    controls: tuple[int, ...] = ()
    params: tuple[ParameterValue, ...] = ()
    metadata: dict[str, Any] = field(default_factory=dict)

    def __getattribute__(self, name):
        if name in {"params", "name"}:
            owner = object.__getattribute__(self,"__dict__").get("_shared_owner")
            if owner is not None:
                if name == "name": return owner.name
                from .standard_gates import invocation_params
                return invocation_params(owner)
        return object.__getattribute__(self,name)

    def __post_init__(self) -> None:
        if not self.name:
            raise ValueError("QuantumBridge operations require a non-empty name.")
        object.__setattr__(self, "targets", tuple(self.targets))
        object.__setattr__(self, "controls", tuple(self.controls))
        object.__setattr__(self, "params", tuple(self.params))
        owners = [self.metadata[key] for key in ("gate","instruction_object","annotated_operation") if key in self.metadata]
        if len(owners) == 1:
            from .gates import is_native_instruction
            from .annotated_operation import AnnotatedOperation
            owner = owners[0]
            if is_native_instruction(owner) or type(owner) is AnnotatedOperation:
                from .standard_gates import invocation_params
                from .instruction_parameters import admit_payloads
                values = invocation_params(owner)
                admit_payloads(values)
                if self.name == owner.name and self.params == values:
                    object.__setattr__(self,"_shared_owner",owner)

    @property
    def wires(self) -> tuple[int, ...]:
        return self.controls + self.targets
