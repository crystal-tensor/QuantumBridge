# Copyright 2026 QuantumBridge Contributors.
# Licensed under the Apache License, Version 2.0.
# This file is part of QuantumBridge SDK.
# This implementation is developed for the QuantumBridge native architecture.

from __future__ import annotations

import re

from quantumbridge.core import Circuit


def _strip_comment(line: str) -> str:
    return line.split("//", 1)[0].strip()


def circuit_from_openqasm(text: str) -> Circuit:
    qregs = {}
    cregs = {}
    pending: list[tuple[str, tuple]] = []

    def q_index(register: str, index: int) -> int:
        if not qregs:
            raise ValueError("QuantumBridge QASM import requires a qreg declaration before quantum operations.")
        if register not in qregs or not 0 <= index < qregs[register][1]:
            raise ValueError(f"QuantumBridge QASM import has invalid quantum reference {register}[{index}].")
        return qregs[register][0] + index

    def c_index(register: str, index: int) -> int:
        if register not in cregs or not 0 <= index < cregs[register][1]:
            raise ValueError(f"QuantumBridge QASM import has invalid classical reference {register}[{index}].")
        return cregs[register][0] + index

    for raw_line in text.splitlines():
        line = _strip_comment(raw_line)
        if not line or line == "OPENQASM 2.0;" or line == 'include "qelib1.inc";':
            continue
        if line.startswith("qreg "):
            match = re.fullmatch(r"qreg\s+([A-Za-z_][A-Za-z0-9_]*)\[(\d+)\];", line)
            if not match:
                raise ValueError("QuantumBridge QASM import could not parse qreg declaration.")
            name, size = match.group(1), int(match.group(2))
            qregs[name] = (sum(width for _, width in qregs.values()), size)
        elif line.startswith("creg "):
            match = re.fullmatch(r"creg\s+([A-Za-z_][A-Za-z0-9_]*)\[(\d+)\];", line)
            if not match:
                raise ValueError("QuantumBridge QASM import could not parse creg declaration.")
            name, size = match.group(1), int(match.group(2))
            cregs[name] = (sum(width for _, width in cregs.values()), size)
        elif line.startswith("barrier "):
            continue
        elif line.startswith("measure "):
            whole = re.fullmatch(r"measure\s+([A-Za-z_][A-Za-z0-9_]*)\s*->\s*([A-Za-z_][A-Za-z0-9_]*);", line)
            indexed = re.fullmatch(
                r"measure\s+([A-Za-z_][A-Za-z0-9_]*)\[(\d+)\]\s*->\s*([A-Za-z_][A-Za-z0-9_]*)\[(\d+)\];",
                line,
            )
            if whole:
                qname, cname = whole.group(1), whole.group(2)
                if qname not in qregs or cname not in cregs or qregs[qname][1] != cregs[cname][1]:
                    raise ValueError("QuantumBridge QASM whole-register measurement requires matching qreg and creg sizes.")
                for offset in range(qregs[qname][1]):
                    pending.append(("measure", (qregs[qname][0] + offset, cregs[cname][0] + offset)))
            elif indexed:
                pending.append(("measure", (q_index(indexed.group(1), int(indexed.group(2))), c_index(indexed.group(3), int(indexed.group(4))))))
            else:
                raise ValueError("QuantumBridge QASM import supports indexed or whole-register measurements.")
        else:
            qref = r"([A-Za-z_][A-Za-z0-9_]*)\[(\d+)\]"
            rot = re.fullmatch(r"(rx|ry|rz)\(([^)]+)\)\s+" + qref + r";", line)
            one = re.fullmatch(r"(x|y|z|h)\s+" + qref + r";", line)
            two = re.fullmatch(r"(cx|cz)\s+" + qref + r"\s*,\s*" + qref + r";", line)
            if rot:
                pending.append((rot.group(1), (float(rot.group(2)), q_index(rot.group(3), int(rot.group(4))))))
            elif one:
                pending.append((one.group(1), (q_index(one.group(2), int(one.group(3))),)))
            elif two:
                pending.append((two.group(1), (q_index(two.group(2), int(two.group(3))), q_index(two.group(4), int(two.group(5))))))
            else:
                raise ValueError(f"QuantumBridge QASM import does not support line: {line}")
    if not qregs:
        raise ValueError("QuantumBridge QASM import requires a qreg declaration.")
    circuit = Circuit(sum(width for _, width in qregs.values()), sum(width for _, width in cregs.values()))
    for name, args in pending:
        if name in {"x", "y", "z", "h"}:
            getattr(circuit, name)(args[0])
        elif name in {"rx", "ry", "rz"}:
            getattr(circuit, name)(args[0], args[1])
        elif name in {"cx", "cz"}:
            getattr(circuit, name)(args[0], args[1])
        elif name == "measure":
            circuit.measure(args[0], args[1])
    return circuit
