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

