# Copyright 2026 QuantumBridge Contributors.
# Licensed under the Apache License, Version 2.0.
# This file is independently implemented for QuantumBridge SDK.
# No source code from Qiskit or PennyLane was copied.
# Design source: docs/roadmap/p2_execution_plan_v0.1.md.

from __future__ import annotations

from numbers import Real


def _format_param(value) -> str:
    if not isinstance(value, Real):
        raise ValueError("QuantumBridge QASM export requires numeric bound parameters.")
    return format(float(value), ".17g")


def dumps(circuit) -> str:
    lines = ["OPENQASM 2.0;", 'include "qelib1.inc";', f"qreg q[{circuit.num_qubits}];"]
    if circuit.num_bits:
        lines.append(f"creg c[{circuit.num_bits}];")
    for op in circuit.operations:
        if op.name == "barrier":
            lines.append("barrier " + ",".join(f"q[{wire}]" for wire in op.targets) + ";")
        elif op.name == "delay":
            unit = op.metadata.get("unit", "dt")
            lines.append(f"// delay({_format_param(op.params[0])} {unit}) q[{op.targets[0]}];")
        elif op.name in {"x", "y", "z", "h", "s", "sdg", "t", "tdg"}:
            lines.append(f"{op.name} q[{op.targets[0]}];")
        elif op.name in {"rx", "ry", "rz"}:
            lines.append(f"{op.name}({_format_param(op.params[0])}) q[{op.targets[0]}];")
        elif op.name == "phase":
            lines.append(f"phase({_format_param(op.params[0])}) q[{op.targets[0]}];")
        elif op.name in {"p", "u1"}:
            lines.append(f"u1({_format_param(op.params[0])}) q[{op.targets[0]}];")
        elif op.name == "u2":
            lines.append(f"u2({_format_param(op.params[0])},{_format_param(op.params[1])}) q[{op.targets[0]}];")
        elif op.name in {"u", "u3"}:
            lines.append(
                f"u3({_format_param(op.params[0])},{_format_param(op.params[1])},{_format_param(op.params[2])}) q[{op.targets[0]}];"
            )
        elif op.name in {"cx", "cy", "cz", "ch"}:
            lines.append(f"{op.name} q[{op.controls[0]}],q[{op.targets[0]}];")
        elif op.name == "swap":
            lines.append(f"swap q[{op.targets[0]}],q[{op.targets[1]}];")
        elif op.name == "ccx":
            lines.append(f"ccx q[{op.controls[0]}],q[{op.controls[1]}],q[{op.targets[0]}];")
        elif op.name == "cswap":
            lines.append(f"cswap q[{op.controls[0]}],q[{op.targets[0]}],q[{op.targets[1]}];")
        else:
            raise ValueError(f"QuantumBridge QASM export does not support operation {op.name!r}.")
    for measurement in circuit.measurements:
        lines.append(f"measure q[{measurement.wire}] -> c[{measurement.bit}];")
    return "\n".join(lines) + "\n"
