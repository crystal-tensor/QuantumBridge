# Copyright 2026 QuantumBridge Contributors.
# Licensed under the Apache License, Version 2.0.
# This file is part of QuantumBridge SDK.
# This implementation is developed for the QuantumBridge native architecture.
# Design source: docs/mvp/api_contract_v0.1.md, docs/mvp/ir_design_v0.1.md,
# and docs/mvp/simulator_design_v0.1.md.

from __future__ import annotations

from copy import deepcopy
from numbers import Real
from typing import Any, Mapping, Optional, Sequence, Union

import numpy as np

from .measurements import Measurement
from .operations import Operation
from .parameters import Parameter, ParameterValue, resolve_parameter


class Circuit:
    """Ordered QuantumBridge MVP circuit."""

    def __init__(
        self,
        num_qubits: int,
        num_bits: int = 0,
        name: Optional[str] = None,
        metadata: Optional[Mapping[str, Any]] = None,
    ) -> None:
        if not isinstance(num_qubits, int) or num_qubits <= 0:
            raise ValueError("QuantumBridge circuits require a positive qubit count.")
        if not isinstance(num_bits, int) or num_bits < 0:
            raise ValueError("QuantumBridge classical bit count cannot be negative.")
        self.num_qubits = num_qubits
        self.num_bits = num_bits
        self.name = name
        self.metadata = dict(metadata or {})
        self.operations: list[Operation] = []
        self.measurements: list[Measurement] = []

    def _check_wire(self, wire: int) -> None:
        if not isinstance(wire, int) or not 0 <= wire < self.num_qubits:
            raise ValueError(f"QuantumBridge wire {wire!r} is outside this circuit.")

    def _check_bit(self, bit: int) -> None:
        if not isinstance(bit, int) or not 0 <= bit < self.num_bits:
            raise ValueError(f"QuantumBridge classical bit {bit!r} is outside this circuit.")

    def append(
        self,
        name: str,
        targets: Sequence[int],
        controls: Sequence[int] = (),
        params: Sequence[ParameterValue] = (),
        metadata: Optional[Mapping[str, Any]] = None,
    ) -> "Circuit":
        targets_tuple = tuple(targets)
        controls_tuple = tuple(controls)
        all_wires = controls_tuple + targets_tuple
        for wire in all_wires:
            self._check_wire(wire)
        if len(set(all_wires)) != len(all_wires):
            raise ValueError("QuantumBridge operations require distinct wires.")
        self.operations.append(
            Operation(name=name, targets=targets_tuple, controls=controls_tuple, params=tuple(params), metadata=dict(metadata or {}))
        )
        return self

    def x(self, q: int) -> "Circuit":
        return self.append("x", (q,))

    def y(self, q: int) -> "Circuit":
        return self.append("y", (q,))

    def z(self, q: int) -> "Circuit":
        return self.append("z", (q,))

    def h(self, q: int) -> "Circuit":
        return self.append("h", (q,))

    def s(self, q: int) -> "Circuit":
        return self.append("s", (q,))

    def sdg(self, q: int) -> "Circuit":
        return self.append("sdg", (q,))

    def t(self, q: int) -> "Circuit":
        return self.append("t", (q,))

    def tdg(self, q: int) -> "Circuit":
        return self.append("tdg", (q,))

    def rx(self, theta: ParameterValue, q: int) -> "Circuit":
        return self.append("rx", (q,), params=(theta,))

    def ry(self, theta: ParameterValue, q: int) -> "Circuit":
        return self.append("ry", (q,), params=(theta,))

    def rz(self, theta: ParameterValue, q: int) -> "Circuit":
        return self.append("rz", (q,), params=(theta,))

    def phase(self, theta: ParameterValue, q: int) -> "Circuit":
        return self.append("phase", (q,), params=(theta,))

    def cx(self, control: int, target: int) -> "Circuit":
        return self.append("cx", (target,), controls=(control,))

    def cz(self, control: int, target: int) -> "Circuit":
        return self.append("cz", (target,), controls=(control,))

    def swap(self, a: int, b: int) -> "Circuit":
        return self.append("swap", (a, b))

    def iswap(self, a: int, b: int) -> "Circuit":
        return self.append("iswap", (a, b), metadata={"experimental": True})

    def ccx(self, c0: int, c1: int, target: int) -> "Circuit":
        return self.append("ccx", (target,), controls=(c0, c1))

    def unitary(self, matrix: Any, wires: Sequence[int], name: str = "unitary") -> "Circuit":
        arr = np.asarray(matrix, dtype=complex)
        dim = 1 << len(tuple(wires))
        if arr.shape != (dim, dim):
            raise ValueError("QuantumBridge custom unitary shape must match target wires.")
        if not np.allclose(arr.conj().T @ arr, np.eye(dim), atol=1e-10):
            raise ValueError("QuantumBridge custom unitary matrix must be unitary within tolerance.")
        return self.append(name, tuple(wires), metadata={"matrix": arr})

    def measure(self, q: int, bit: Optional[int] = None) -> "Circuit":
        self._check_wire(q)
        if bit is None:
            bit = len(self.measurements)
        self._check_bit(bit)
        self.measurements.append(Measurement(wire=q, bit=bit))
        return self

    def copy(self) -> "Circuit":
        return deepcopy(self)

    def bind(self, mapping: Mapping[Union[Parameter, str], Real]) -> "Circuit":
        bound = Circuit(self.num_qubits, self.num_bits, self.name, self.metadata)
        for op in self.operations:
            params = tuple(resolve_parameter(param, mapping) for param in op.params)
            bound.operations.append(Operation(op.name, op.targets, op.controls, params, dict(op.metadata)))
        bound.measurements = list(self.measurements)
        return bound

    def to_ir(self):
        from quantumbridge.ir.qb_ir import IRProgram

        return IRProgram.from_circuit(self)

    def to_openqasm(self) -> str:
        from quantumbridge.qasm import dumps

        return dumps(self)
