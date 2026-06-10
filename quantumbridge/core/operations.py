# Copyright 2026 QuantumBridge Contributors.
# Licensed under the Apache License, Version 2.0.
# This file is part of QuantumBridge SDK.
# This implementation is developed for the QuantumBridge native architecture.
# Design source: docs/mvp/api_contract_v0.1.md and docs/mvp/simulator_design_v0.1.md.

from __future__ import annotations

from copy import deepcopy
from dataclasses import dataclass, field
from typing import Any

from .parameters import ParameterValue


@dataclass(frozen=True)
class Instruction:
    """Qiskit-style instruction object with optional circuit definition."""

    name: str
    num_qubits: int
    num_bits: int = 0
    params: tuple[ParameterValue, ...] = ()
    definition: Any = None
    metadata: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not isinstance(self.name, str) or not self.name:
            raise ValueError("QuantumBridge instructions require a non-empty name.")
        if not isinstance(self.num_qubits, int) or self.num_qubits <= 0:
            raise ValueError("QuantumBridge instructions require a positive qubit count.")
        if not isinstance(self.num_bits, int) or self.num_bits < 0:
            raise ValueError("QuantumBridge instruction classical bit count cannot be negative.")
        object.__setattr__(self, "params", tuple(self.params))
        object.__setattr__(self, "metadata", dict(self.metadata))

    def copy(self, name: str | None = None) -> "Instruction":
        return Instruction(
            name=name or self.name,
            num_qubits=self.num_qubits,
            num_bits=self.num_bits,
            params=self.params,
            definition=None if self.definition is None else self.definition.copy(),
            metadata=deepcopy(self.metadata),
        )

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
