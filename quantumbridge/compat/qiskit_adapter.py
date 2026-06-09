# Copyright 2026 QuantumBridge Contributors.
# Licensed under the Apache License, Version 2.0.
# This file is part of QuantumBridge SDK.
# This implementation is developed for the QuantumBridge native architecture.
#
# Adapter Integration: this module optionally imports Qiskit at runtime.
# No Qiskit source code is copied into this file.

from __future__ import annotations

from quantumbridge.core import Circuit
from quantumbridge.results import Result


SUPPORTED_IMPORT = {"x", "y", "z", "h", "rx", "ry", "rz", "p", "phase", "cx", "cnot", "cz", "swap", "measure"}


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
        params = [float(param) for param in getattr(item.operation, "params", [])]
        if name in {"x", "y", "z", "h"}:
            getattr(qb, name)(qubits[0])
        elif name in {"rx", "ry", "rz"}:
            getattr(qb, name)(params[0], qubits[0])
        elif name in {"p", "phase"}:
            qb.phase(params[0], qubits[0])
        elif name in {"cx", "cnot", "cz"}:
            gate = "cx" if name in {"cx", "cnot"} else "cz"
            getattr(qb, gate)(qubits[0], qubits[1])
        elif name == "swap":
            qb.swap(qubits[0], qubits[1])
        elif name == "measure":
            qb.measure(qubits[0], clbits[0])
    return qb


def ir_from_qiskit(qiskit_circuit):
    return circuit_from_qiskit(qiskit_circuit).to_ir()


def circuit_to_qiskit(circuit: Circuit):
    QuantumCircuit = _require_qiskit()
    qc = QuantumCircuit(circuit.num_qubits, circuit.num_bits)
    for op in circuit.operations:
        if op.name in {"x", "y", "z", "h"}:
            getattr(qc, op.name)(op.targets[0])
        elif op.name in {"rx", "ry", "rz"}:
            getattr(qc, op.name)(float(op.params[0]), op.targets[0])
        elif op.name == "phase":
            qc.p(float(op.params[0]), op.targets[0])
        elif op.name in {"cx", "cz"}:
            getattr(qc, op.name)(op.controls[0], op.targets[0])
        elif op.name == "swap":
            qc.swap(op.targets[0], op.targets[1])
        else:
            raise ValueError(f"QuantumBridge Qiskit export does not support operation {op.name!r}.")
    for meas in circuit.measurements:
        qc.measure(meas.wire, meas.bit)
    return qc


def circuit_from_ir(program) -> Circuit:
    circuit = Circuit(program.num_qubits, program.num_bits, program.name, program.metadata)
    for instruction in program.instructions:
        if instruction.op in {"x", "y", "z", "h"}:
            getattr(circuit, instruction.op)(instruction.targets[0])
        elif instruction.op in {"rx", "ry", "rz"}:
            getattr(circuit, instruction.op)(instruction.params[0], instruction.targets[0])
        elif instruction.op == "phase":
            circuit.phase(instruction.params[0], instruction.targets[0])
        elif instruction.op in {"cx", "cz"}:
            getattr(circuit, instruction.op)(instruction.controls[0], instruction.targets[0])
        elif instruction.op == "swap":
            circuit.swap(instruction.targets[0], instruction.targets[1])
        else:
            raise ValueError(f"QuantumBridge IR to Qiskit bridge does not support operation {instruction.op!r}.")
    for measurement in program.measurements:
        circuit.measure(measurement.wire, measurement.bit)
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
