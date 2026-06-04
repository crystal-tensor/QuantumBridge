# Copyright 2026 QuantumBridge Contributors.
# Licensed under the Apache License, Version 2.0.
# This file is part of QuantumBridge SDK.
# This implementation is developed for the QuantumBridge native architecture.

from quantumbridge.core import Circuit

from .pass_base import PassResult, TransformationPass


class SimpleGateCancellationPass(TransformationPass):
    cancellable = {"x", "h", "cx", "cz"}

    def run(self, circuit):
        out = Circuit(circuit.num_qubits, circuit.num_bits, circuit.name, circuit.metadata)
        index = 0
        changed = False
        while index < len(circuit.operations):
            current = circuit.operations[index]
            nxt = circuit.operations[index + 1] if index + 1 < len(circuit.operations) else None
            if (
                nxt is not None
                and current.name == nxt.name
                and current.name in self.cancellable
                and current.targets == nxt.targets
                and current.controls == nxt.controls
            ):
                changed = True
                index += 2
                continue
            out.operations.append(current)
            index += 1
        out.measurements = list(circuit.measurements)
        return PassResult(out, {}, changed)


class SingleQubitMergePlaceholderPass(TransformationPass):
    def run(self, circuit):
        return PassResult(circuit, {"single_qubit_merge": "placeholder-not-implemented"}, False)


class RemoveZeroRotationPass(TransformationPass):
    def __init__(self, tolerance: float = 1e-12):
        self.tolerance = tolerance

    def run(self, circuit):
        out = Circuit(circuit.num_qubits, circuit.num_bits, circuit.name, circuit.metadata)
        changed = False
        for op in circuit.operations:
            if op.name in {"rx", "ry", "rz", "phase"} and abs(float(op.params[0])) <= self.tolerance:
                changed = True
                continue
            out.operations.append(op)
        out.measurements = list(circuit.measurements)
        return PassResult(out, {}, changed)


class MergeAdjacentRotationPass(TransformationPass):
    def __init__(self, tolerance: float = 1e-12):
        self.tolerance = tolerance

    def run(self, circuit):
        out = Circuit(circuit.num_qubits, circuit.num_bits, circuit.name, circuit.metadata)
        changed = False
        index = 0
        while index < len(circuit.operations):
            current = circuit.operations[index]
            nxt = circuit.operations[index + 1] if index + 1 < len(circuit.operations) else None
            if (
                nxt is not None
                and current.name == nxt.name
                and current.name in {"rx", "ry", "rz", "phase"}
                and current.targets == nxt.targets
                and current.controls == nxt.controls
            ):
                angle = float(current.params[0]) + float(nxt.params[0])
                if abs(angle) > self.tolerance:
                    getattr(out, current.name)(angle, current.targets[0])
                changed = True
                index += 2
                continue
            out.operations.append(current)
            index += 1
        out.measurements = list(circuit.measurements)
        return PassResult(out, {}, changed)
