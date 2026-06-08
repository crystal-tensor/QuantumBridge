# Copyright 2026 QuantumBridge Contributors.
# Licensed under the Apache License, Version 2.0.
# This file is part of QuantumBridge SDK.
# This implementation is developed for the QuantumBridge native architecture.


def needs_decomposition(circuit, basis_gates) -> bool:
    basis = set(basis_gates)
    return any(op.name not in basis for op in circuit.operations)


from quantumbridge.core import Circuit
from .pass_base import PassResult, TransformationPass


class BasisGateConversionPass(TransformationPass):
    def __init__(self, basis_gates):
        self.basis_gates = set(basis_gates)

    def run(self, circuit):
        unsupported = sorted({op.name for op in circuit.operations if op.name not in self.basis_gates})
        if unsupported:
            raise ValueError(f"QuantumBridge basis conversion does not support operations outside basis: {unsupported}.")
        return PassResult(circuit, {"basis_gates": sorted(self.basis_gates)}, False)


class GateDecompositionPass(TransformationPass):
    def __init__(self, basis_gates=None):
        self.basis_gates = set(basis_gates or {"x", "y", "z", "h", "rx", "ry", "rz", "cx", "cz", "swap"})

    def run(self, circuit):
        out = Circuit(circuit.num_qubits, circuit.num_bits, circuit.name, circuit.metadata)
        decomposed = []
        for op in circuit.operations:
            if op.name == "phase" and "rz" in self.basis_gates:
                out.rz(op.params[0], op.targets[0])
                decomposed.append("phase->rz-up-to-global-phase")
            elif op.name == "sdg" and "s" in self.basis_gates:
                out.s(op.targets[0])
                out.s(op.targets[0])
                out.s(op.targets[0])
                decomposed.append("sdg->s,s,s")
            elif op.name == "tdg" and "t" in self.basis_gates:
                for _ in range(7):
                    out.t(op.targets[0])
                decomposed.append("tdg->t*7")
            elif op.name in self.basis_gates:
                out.operations.append(op)
            else:
                raise ValueError(f"QuantumBridge gate decomposition does not support operation {op.name!r}.")
        out.measurements = list(circuit.measurements)
        return PassResult(out, {"decomposed": decomposed}, bool(decomposed))
