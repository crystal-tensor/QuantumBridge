# Copyright 2026 QuantumBridge Contributors.
# Licensed under the Apache License, Version 2.0.
# This file is part of QuantumBridge SDK.
# This implementation is developed for the QuantumBridge native architecture.
#
# Adapter Integration: this module optionally imports Qiskit at runtime.
# No Qiskit source code is copied into this file.

from __future__ import annotations

from quantumbridge.core import Circuit, Measurement
from quantumbridge.results import Result


SUPPORTED_IMPORT = {"id", "x", "y", "z", "h", "s", "sdg", "sx", "sxdg", "rx", "ry", "rz", "p", "phase", "cx", "cnot", "cy", "cz", "swap", "dcx", "ecr", "iswap", "measure", "reset", "barrier", "delay", "if_else"}


def _require_qiskit():
    try:
        from qiskit import QuantumCircuit
    except Exception as exc:
        raise ImportError("QuantumBridge Qiskit adapter requires the optional qiskit package.") from exc
    return QuantumCircuit


def circuit_from_qiskit(qiskit_circuit) -> Circuit:
    qb = Circuit(qiskit_circuit.num_qubits, qiskit_circuit.num_clbits)
    for item in qiskit_circuit.data:
        name = item.operation.name
        if name not in SUPPORTED_IMPORT:
            raise ValueError(f"QuantumBridge Qiskit adapter does not support operation {name!r}.")
        qubits = [qiskit_circuit.find_bit(qubit).index for qubit in item.qubits]
        clbits = [qiskit_circuit.find_bit(clbit).index for clbit in item.clbits]
        params = [] if name == "if_else" else [float(param) for param in getattr(item.operation, "params", [])]
        if name in {"id", "x", "y", "z", "h", "s", "sdg", "sx", "sxdg", "reset"}:
            getattr(qb, name)(qubits[0])
        elif name in {"rx", "ry", "rz"}:
            getattr(qb, name)(params[0], qubits[0])
        elif name in {"p", "phase"}:
            qb.phase(params[0], qubits[0])
        elif name in {"cx", "cnot", "cy", "cz"}:
            gate = "cx" if name in {"cx", "cnot"} else "cz"
            getattr(qb, gate)(qubits[0], qubits[1])
        elif name in {"swap", "dcx", "ecr", "iswap"}:
            getattr(qb, name)(qubits[0], qubits[1])
        elif name == "measure":
            qb.measure(qubits[0], clbits[0])
        elif name == "barrier":
            qb.barrier(*qubits)
        elif name == "delay":
            qb.delay(params[0], qubits[0], unit=item.operation.unit)
        elif name == "if_else":
            classical, value = item.operation.condition
            condition_bits = [qiskit_circuit.find_bit(bit).index for bit in classical] if hasattr(classical, "__iter__") else [qiskit_circuit.find_bit(classical).index]
            blocks = item.operation.blocks
            true_body = circuit_from_qiskit(blocks[0])
            false_body = circuit_from_qiskit(blocks[1]) if len(blocks) > 1 else None
            qb.if_else((condition_bits, int(value)), true_body, false_body, qubits=qubits, clbits=clbits, inplace=True)
    return qb


def ir_from_qiskit(qiskit_circuit):
    return circuit_from_qiskit(qiskit_circuit).to_ir()


def circuit_to_qiskit(circuit: Circuit):
    QuantumCircuit = _require_qiskit()
    qc = QuantumCircuit(circuit.num_qubits, circuit.num_bits)
    for op in circuit.iter_instructions():
        if any(key in op.metadata for key in ("condition", "control_flow", "control_flow_stack")):
            raise ValueError("QuantumBridge Qiskit export does not yet reconstruct conditional blocks.")
        if isinstance(op, Measurement):
            qc.measure(op.wire, op.bit)
        elif op.name in {"id", "x", "y", "z", "h", "s", "sdg", "sx", "sxdg", "reset"}:
            getattr(qc, op.name)(op.targets[0])
        elif op.name in {"rx", "ry", "rz"}:
            getattr(qc, op.name)(float(op.params[0]), op.targets[0])
        elif op.name == "phase":
            qc.p(float(op.params[0]), op.targets[0])
        elif op.name in {"cx", "cy", "cz"}:
            getattr(qc, op.name)(op.controls[0], op.targets[0])
        elif op.name in {"swap", "dcx", "ecr", "iswap"}:
            getattr(qc, op.name)(op.targets[0], op.targets[1])
        elif op.name == "barrier":
            qc.barrier(*op.targets)
        elif op.name == "delay":
            qc.delay(float(op.params[0]), op.targets[0], unit=op.metadata.get("unit", "dt"))
        else:
            raise ValueError(f"QuantumBridge Qiskit export does not support operation {op.name!r}.")
    return qc


def circuit_from_ir(program) -> Circuit:
    circuit = Circuit(program.num_qubits, program.num_bits, program.name, program.metadata)
    for instruction in program.instructions:
        circuit.append(instruction.op, instruction.targets, controls=instruction.controls,
                       params=instruction.params, metadata=instruction.metadata)
    for measurement in program.measurements:
        circuit.measurements.append(Measurement(measurement.wire, measurement.bit, measurement.kind, dict(getattr(measurement, "metadata", {}))))
    return circuit


def ir_to_qiskit(program):
    return circuit_to_qiskit(circuit_from_ir(program))


def result_from_qiskit_counts(qiskit_result_or_counts) -> Result:
    if isinstance(qiskit_result_or_counts, dict):
        counts = qiskit_result_or_counts
    elif hasattr(qiskit_result_or_counts, "get_counts"):
        counts = qiskit_result_or_counts.get_counts()
    else:
        raise TypeError("QuantumBridge Qiskit result adapter expects a counts mapping or an object with get_counts().")
    counts = {str(key): int(value) for key, value in counts.items()}
    total = sum(counts.values())
    probabilities = {key: value / total for key, value in counts.items()} if total else {}
    return Result(
        counts_data=counts,
        probabilities_data=probabilities,
        metadata_data={"adapter": "qiskit_result_counts", "shots": total},
    )
