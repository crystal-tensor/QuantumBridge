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


@dataclass(init=False)
class Instruction:
    """Qiskit-style instruction object with optional circuit definition."""

    name: str
    num_qubits: int
    num_bits: int = 0
    params: MutableSequence[Any] = ()
    definition: Any = None
    metadata: dict[str, Any] = field(default_factory=dict)

    def __init__(self, name, num_qubits, num_bits=0, params=(), definition=None, metadata=None):
        from .instruction_parameters import admit_owner
        admit_owner(self)
        object.__setattr__(self, "name", name)
        object.__setattr__(self, "num_qubits", num_qubits)
        object.__setattr__(self, "num_bits", num_bits)
        object.__setattr__(self, "_params", ())
        object.__setattr__(self, "_definition", None)
        object.__setattr__(self, "_parameter_plan", None)
        object.__setattr__(self, "metadata", dict(metadata or {}))
        self.__post_init__()
        from .instruction_parameters import validated_values
        object.__setattr__(self, "_params", validated_values(self, params))
        self.definition = definition

    def __post_init__(self) -> None:
        if not isinstance(self.name, str) or not self.name:
            raise ValueError("QuantumBridge instructions require a non-empty name.")
        if not isinstance(self.num_qubits, int) or self.num_qubits <= 0:
            raise ValueError("QuantumBridge instructions require a positive qubit count.")
        if not isinstance(self.num_bits, int) or self.num_bits < 0:
            raise ValueError("QuantumBridge instruction classical bit count cannot be negative.")
        object.__setattr__(self, "metadata", dict(self.metadata))

    def __setattr__(self, name, value):
        if name in {"params", "definition"}: return object.__setattr__(self, name, value)
        raise AttributeError("Use params/definition assignment or copy to update a native Instruction.")

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
        from .parameters import parameter_set
        if not set(value.parameters) <= set(parameter_set(params)):
            raise ValueError("Instruction definition parameter namespace differs from its owner.")

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

    def inverse(self, name: str | None = None) -> "Instruction":
        if self.definition is not None:
            return self.definition.inverse().to_instruction(name=name or f"{self.name}_dg")
        metadata = deepcopy(self.metadata)
        matrix = metadata.get("matrix")
        if matrix is not None:
            import numpy as np

            metadata["matrix"] = np.asarray(matrix, dtype=complex).conj().T
            metadata["inverse_of"] = self.name
            return Instruction(name=name or f"{self.name}_dg", num_qubits=self.num_qubits, params=self.params, metadata=metadata)
        from quantumbridge.core.circuit import Circuit

        circuit = Circuit(self.num_qubits, self.num_bits).append(self.name, range(self.num_qubits), params=self.params, metadata=metadata)
        return circuit.inverse().to_instruction(name=name or f"{self.name}_dg")

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

    def __post_init__(self) -> None:
        if not self.name:
            raise ValueError("QuantumBridge operations require a non-empty name.")
        object.__setattr__(self, "targets", tuple(self.targets))
        object.__setattr__(self, "controls", tuple(self.controls))
        object.__setattr__(self, "params", tuple(self.params))

    @property
    def wires(self) -> tuple[int, ...]:
        return self.controls + self.targets
