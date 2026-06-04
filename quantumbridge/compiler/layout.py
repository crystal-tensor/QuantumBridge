# Copyright 2026 QuantumBridge Contributors.
# Licensed under the Apache License, Version 2.0.
# This file is part of QuantumBridge SDK.
# This implementation is developed for the QuantumBridge native architecture.


def identity_layout(num_qubits: int) -> dict[int, int]:
    return {wire: wire for wire in range(num_qubits)}

