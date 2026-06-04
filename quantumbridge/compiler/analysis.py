# Copyright 2026 QuantumBridge Contributors.
# Licensed under the Apache License, Version 2.0.
# This file is part of QuantumBridge SDK.
# This implementation is developed for the QuantumBridge native architecture.

from .pass_base import AnalysisPass, PassResult


class DepthAnalysisPass(AnalysisPass):
    def run(self, circuit):
        wire_depth = [0] * circuit.num_qubits
        for op in circuit.operations:
            level = 1 + max(wire_depth[wire] for wire in op.wires)
            for wire in op.wires:
                wire_depth[wire] = level
        return PassResult(circuit, {"depth": max(wire_depth, default=0)}, False)


class TwoQubitCountAnalysisPass(AnalysisPass):
    def run(self, circuit):
        count = sum(1 for op in circuit.operations if len(op.wires) == 2)
        return PassResult(circuit, {"two_qubit_gate_count": count}, False)

