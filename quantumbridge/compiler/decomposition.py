# Copyright 2026 QuantumBridge Contributors.
# Licensed under the Apache License, Version 2.0.
# This file is part of QuantumBridge SDK.
# This implementation is developed for the QuantumBridge native architecture.


def needs_decomposition(circuit, basis_gates) -> bool:
    basis = set(basis_gates)
    return any(op.name not in basis for op in circuit.operations)

