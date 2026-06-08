# Copyright 2026 QuantumBridge Contributors.
# Licensed under the Apache License, Version 2.0.
# This file is part of QuantumBridge SDK.
# This implementation is developed for the QuantumBridge native architecture.


def routing_required(circuit, coupling_map) -> bool:
    edges = set(coupling_map.edges)
    for op in circuit.operations:
        if op.controls:
            edge = (op.controls[0], op.targets[0])
            if edge not in edges and (edge[1], edge[0]) not in edges:
                return True
    return False


from quantumbridge.core import Circuit
from .pass_base import PassResult, TransformationPass


class BasicRoutingPass(TransformationPass):
    def __init__(self, coupling_map):
        self.coupling_map = coupling_map

    def run(self, circuit):
        unsupported = []
        for op in circuit.operations:
            if len(op.wires) == 2 and not self.coupling_map.is_connected(op.wires[0], op.wires[1]):
                unsupported.append({"operation": op.name, "wires": op.wires})
        return PassResult(circuit, {"routing_required": bool(unsupported), "unsupported_interactions": unsupported}, False)


class SwapInsertionPass(TransformationPass):
    def __init__(self, coupling_map):
        self.coupling_map = coupling_map

    def run(self, circuit):
        out = Circuit(circuit.num_qubits, circuit.num_bits, circuit.name, circuit.metadata)
        inserted = 0
        for op in circuit.operations:
            if len(op.wires) == 2 and not self.coupling_map.is_connected(op.wires[0], op.wires[1]):
                neighbors = self.coupling_map.neighbors(op.wires[0])
                if not neighbors:
                    raise ValueError("QuantumBridge routing cannot insert a swap without coupling neighbors.")
                bridge = neighbors[0]
                out.swap(op.wires[0], bridge)
                inserted += 1
            out.operations.append(op)
        out.measurements = list(circuit.measurements)
        return PassResult(out, {"inserted_swaps": inserted}, bool(inserted))
