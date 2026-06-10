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
from quantumbridge.utils.math import gate_matrix


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

    @property
    def calibrations(self) -> dict:
        return self.metadata.setdefault("calibrations", {})

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

    def compose(
        self,
        other: "Circuit",
        qubits: Optional[Sequence[int]] = None,
        clbits: Optional[Sequence[int]] = None,
        inplace: bool = False,
        front: bool = False,
    ) -> "Circuit":
        if not isinstance(other, Circuit):
            raise TypeError("QuantumBridge Circuit.compose expects another Circuit.")
        target = self if inplace else self.copy()
        qubit_map = _index_map(other.num_qubits, target.num_qubits, qubits, "qubits")
        clbit_map = _index_map(other.num_bits, target.num_bits, clbits, "clbits")
        mapped_ops = [_remap_operation(op, qubit_map) for op in other.operations]
        mapped_measurements = [
            Measurement(kind=measurement.kind, wire=qubit_map[measurement.wire], bit=clbit_map[measurement.bit])
            for measurement in other.measurements
        ]
        if front:
            target.operations = mapped_ops + target.operations
            target.measurements = mapped_measurements + target.measurements
        else:
            target.operations.extend(mapped_ops)
            target.measurements.extend(mapped_measurements)
        return target

    def inverse(self, inplace: bool = False) -> "Circuit":
        if self.measurements:
            raise ValueError("QuantumBridge Circuit.inverse does not invert measured circuits.")
        target = Circuit(self.num_qubits, self.num_bits, self.name, self.metadata)
        target.operations = [_inverse_operation(op) for op in reversed(self.operations)]
        return _replace_self(self, target) if inplace else target

    def power(self, exponent: int, inplace: bool = False) -> "Circuit":
        if not isinstance(exponent, int):
            raise ValueError("QuantumBridge Circuit.power requires an integer exponent.")
        if self.measurements:
            raise ValueError("QuantumBridge Circuit.power does not repeat measured circuits.")
        unit = self.inverse() if exponent < 0 else self
        target = Circuit(self.num_qubits, self.num_bits, self.name, self.metadata)
        for _ in range(abs(exponent)):
            target.compose(unit, inplace=True)
        return _replace_self(self, target) if inplace else target

    def control(
        self,
        num_ctrl_qubits: int = 1,
        label: Optional[str] = None,
        ctrl_state: Optional[int] = None,
    ) -> "Circuit":
        if not isinstance(num_ctrl_qubits, int) or num_ctrl_qubits <= 0:
            raise ValueError("QuantumBridge Circuit.control requires a positive control-qubit count.")
        if self.measurements:
            raise ValueError("QuantumBridge Circuit.control does not control measured circuits.")
        ctrl_state = (1 << num_ctrl_qubits) - 1 if ctrl_state is None else int(ctrl_state)
        if not 0 <= ctrl_state < (1 << num_ctrl_qubits):
            raise ValueError("QuantumBridge Circuit.control ctrl_state is outside the control register.")
        out = Circuit(num_ctrl_qubits + self.num_qubits, self.num_bits, label or self.name, self.metadata)
        prefix = tuple(range(num_ctrl_qubits))
        for op in self.operations:
            base_wires = op.controls + op.targets
            mapped_wires = prefix + tuple(num_ctrl_qubits + wire for wire in base_wires)
            base = gate_matrix(op.name, op.params, op.metadata)
            controlled = _controlled_matrix(base, num_ctrl_qubits, ctrl_state)
            metadata = {
                "matrix": controlled,
                "controlled_operation": op.name,
                "ctrl_state": ctrl_state,
                "base_wires": base_wires,
            }
            out.unitary(controlled, mapped_wires, name=f"c{num_ctrl_qubits}_{op.name}").operations[-1].metadata.update(metadata)
        return out

    def with_condition(self, classical: Union[int, tuple[int, ...]], value: int, inplace: bool = False) -> "Circuit":
        target = self if inplace else self.copy()
        bits = (classical,) if isinstance(classical, int) else tuple(classical)
        for bit in bits:
            target._check_bit(bit)
        condition = {"bits": list(bits), "value": int(value)}
        target.operations = [_operation_with_metadata(op, {"condition": condition}) for op in target.operations]
        return target

    def c_if(self, classical: Union[int, tuple[int, ...]], value: int) -> "Circuit":
        return self.with_condition(classical, value, inplace=True)

    def add_calibration(
        self,
        name: str,
        qubits: Sequence[int],
        schedule: Any,
        params: Sequence[ParameterValue] = (),
    ) -> "Circuit":
        qubits_tuple = tuple(qubits)
        for wire in qubits_tuple:
            self._check_wire(wire)
        key = _calibration_key(name, qubits_tuple, tuple(params))
        self.calibrations[key] = {
            "name": name,
            "qubits": qubits_tuple,
            "params": tuple(params),
            "schedule": schedule,
        }
        return self

    def get_calibration(self, name: str, qubits: Sequence[int], params: Sequence[ParameterValue] = ()) -> Any:
        key = _calibration_key(name, tuple(qubits), tuple(params))
        return self.calibrations[key]["schedule"]

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


def _index_map(source_size: int, target_size: int, selected: Optional[Sequence[int]], label: str) -> dict[int, int]:
    if selected is None:
        selected_tuple = tuple(range(source_size))
    else:
        selected_tuple = tuple(int(item) for item in selected)
    if len(selected_tuple) != source_size:
        raise ValueError(f"QuantumBridge compose {label} length must match the composed circuit.")
    if any(item < 0 or item >= target_size for item in selected_tuple):
        raise ValueError(f"QuantumBridge compose {label} are outside the target circuit.")
    if len(set(selected_tuple)) != len(selected_tuple):
        raise ValueError(f"QuantumBridge compose {label} must be distinct.")
    return {source: target for source, target in enumerate(selected_tuple)}


def _remap_operation(op: Operation, qubit_map: Mapping[int, int]) -> Operation:
    return Operation(
        name=op.name,
        targets=tuple(qubit_map[wire] for wire in op.targets),
        controls=tuple(qubit_map[wire] for wire in op.controls),
        params=op.params,
        metadata=deepcopy(op.metadata),
    )


def _operation_with_metadata(op: Operation, metadata: Mapping[str, Any]) -> Operation:
    merged = deepcopy(op.metadata)
    merged.update(metadata)
    return Operation(op.name, op.targets, op.controls, op.params, merged)


def _inverse_operation(op: Operation) -> Operation:
    if op.name in {"x", "y", "z", "h", "cx", "cz", "swap", "ccx"}:
        return _operation_with_metadata(op, {})
    inverse_name = {"s": "sdg", "sdg": "s", "t": "tdg", "tdg": "t"}.get(op.name)
    if inverse_name:
        return Operation(inverse_name, op.targets, op.controls, op.params, deepcopy(op.metadata))
    if op.name in {"rx", "ry", "rz", "phase"}:
        return Operation(op.name, op.targets, op.controls, (-op.params[0],), deepcopy(op.metadata))
    matrix = op.metadata.get("matrix")
    if matrix is not None:
        metadata = deepcopy(op.metadata)
        metadata["matrix"] = np.asarray(matrix, dtype=complex).conj().T
        metadata["inverse_of"] = op.name
        return Operation(f"{op.name}_dg", op.targets, op.controls, op.params, metadata)
    raise ValueError(f"QuantumBridge cannot invert operation {op.name!r}.")


def _controlled_matrix(base: np.ndarray, num_ctrl_qubits: int, ctrl_state: int) -> np.ndarray:
    base = np.asarray(base, dtype=complex)
    base_dim = base.shape[0]
    ctrl_dim = 1 << num_ctrl_qubits
    out = np.eye(ctrl_dim * base_dim, dtype=complex)
    start = ctrl_state * base_dim
    out[start : start + base_dim, start : start + base_dim] = base
    return out


def _replace_self(original: Circuit, replacement: Circuit) -> Circuit:
    original.operations = replacement.operations
    original.measurements = replacement.measurements
    original.metadata = replacement.metadata
    return original


def _calibration_key(name: str, qubits: tuple[int, ...], params: tuple[ParameterValue, ...]) -> str:
    param_key = ",".join(repr(param) for param in params)
    return f"{name}|{','.join(str(wire) for wire in qubits)}|{param_key}"
