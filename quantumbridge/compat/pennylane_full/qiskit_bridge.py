# This file is independently implemented for QuantumBridge SDK.
# No source code from Qiskit or PennyLane was copied.
"""Minimal PennyLane-to-QuantumBridge-to-Qiskit bridge scaffold."""

from __future__ import annotations

from quantumbridge.compat.contracts import CapabilityLevel

from .operations_adapter import operation_to_quantumbridge_ir_fragment
from .warnings import unsupported


def pennylane_operations_to_quantumbridge_ir(operations) -> dict:
    instructions = []
    warnings = []
    max_wire = -1
    for op in operations:
        fragment = operation_to_quantumbridge_ir_fragment(op)
        if isinstance(fragment, dict) and fragment.get("supported") is False:
            warnings.append(fragment)
            continue
        instructions.append(fragment)
        for wire in fragment.get("targets", []) + fragment.get("controls", []):
            max_wire = max(max_wire, int(wire))
    return {
        "ir_version": "qb-ir-v0.1",
        "registers": {"quantum": {"size": max_wire + 1 if max_wire >= 0 else 1}, "classical": {"size": 0}},
        "instructions": instructions,
        "measurements": [],
        "metadata": {"source": "pennylane", "warnings": warnings},
    }


def quantumbridge_ir_to_qiskit_circuit(ir):
    try:
        from qiskit import QuantumCircuit
    except Exception:
        return unsupported("Qiskit is not installed; cannot build a Qiskit circuit.", CapabilityLevel.INVENTORY)

    payload = ir.to_dict() if hasattr(ir, "to_dict") else ir
    registers = payload.get("registers", {}) if isinstance(payload, dict) else {}
    num_qubits = registers.get("quantum", {}).get("size", getattr(ir, "num_qubits", 1))
    circuit = QuantumCircuit(num_qubits)
    warnings = []
    for instruction in payload.get("instructions", []):
        op = instruction.get("op")
        targets = instruction.get("targets", [])
        controls = instruction.get("controls", [])
        params = instruction.get("params", [])
        try:
            if op == "h":
                circuit.h(targets[0])
            elif op == "x":
                circuit.x(targets[0])
            elif op == "y":
                circuit.y(targets[0])
            elif op == "z":
                circuit.z(targets[0])
            elif op == "rx":
                circuit.rx(float(params[0]), targets[0])
            elif op == "ry":
                circuit.ry(float(params[0]), targets[0])
            elif op == "rz":
                circuit.rz(float(params[0]), targets[0])
            elif op == "phase":
                circuit.p(float(params[0]), targets[0])
            elif op == "cx":
                circuit.cx(controls[0], targets[0])
            elif op == "cz":
                circuit.cz(controls[0], targets[0])
            elif op == "swap":
                circuit.swap(targets[0], targets[1])
            else:
                warnings.append(f"Unsupported QuantumBridge operation for Qiskit bridge: {op}")
        except Exception as exc:
            warnings.append(f"Could not convert operation {op}: {type(exc).__name__}: {exc}")
    if warnings:
        circuit.metadata = {"quantumbridge_warnings": warnings}
    return circuit
