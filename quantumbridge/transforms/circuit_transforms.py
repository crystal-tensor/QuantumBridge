# Copyright 2026 QuantumBridge Contributors.
# Licensed under the Apache License, Version 2.0.
# This file is part of QuantumBridge SDK.
# This implementation is developed for the QuantumBridge native architecture.


def identity_circuit_transform(circuit):
    return circuit.copy()


def merge_rotations(tape):
    """Merge adjacent same-axis native rotations within safe dynamic segments."""
    from dataclasses import replace
    from quantumbridge.core import Circuit, Measurement
    from quantumbridge.compiler.cancellation import MergeAdjacentRotationPass
    from .program import TransformLimits, check_batch

    check_batch((tape,), TransformLimits())
    out = tape.copy()
    ordered = tuple(out.circuit.iter_instructions())
    out.circuit.operations, out.circuit.measurements = [], []
    segment = Circuit(out.circuit.num_qubits, out.circuit.num_bits)

    def flush():
        nonlocal segment
        if segment.operations:
            # Reuse the existing native algebra on already-owned operations.
            # No deepcopy of nonleaf framework scalars: retain their graphs.
            merged = MergeAdjacentRotationPass(tolerance=0).run(segment).circuit
            while len(merged.operations) < len(segment.operations):
                segment = merged
                merged = MergeAdjacentRotationPass(tolerance=0).run(segment).circuit
            out.circuit.operations.extend(merged.operations)
            segment = Circuit(out.circuit.num_qubits, out.circuit.num_bits)

    for item in ordered:
        if isinstance(item, Measurement):
            flush()
            out.circuit.measurements.append(replace(item, metadata={**item.metadata, "operation_index": len(out.circuit.operations)}))
        elif item.name in {"reset", "kraus", "store"} or item.metadata:
            flush()
            out.circuit.operations.append(item)
        else:
            segment.operations.append(item)
    flush()
    return (out,), lambda results: results[0]

