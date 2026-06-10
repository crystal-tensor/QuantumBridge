# Copyright 2026 QuantumBridge Contributors.
# Licensed under the Apache License, Version 2.0.
# This file is part of QuantumBridge SDK.
# This implementation is developed for the QuantumBridge native architecture.

from __future__ import annotations

from quantumbridge.devices import StatevectorDevice
from .tape import Tape


class QNode:
    def __init__(self, fn, num_qubits: int, device=None, shots: int | None = None, seed: int | None = None):
        self.fn = fn
        self.num_qubits = num_qubits
        self.device = device or StatevectorDevice()
        self.shots = shots
        self.seed = seed

    def __call__(self, *args, **kwargs):
        tape = Tape(self.num_qubits)
        returned = self.fn(tape, *args, **kwargs)
        if tape.measurement == "probs":
            return self.device.probabilities(tape.circuit, wires=tape.measurement_wires)
        if tape.measurement == "state":
            return self.device.statevector(tape.circuit)
        if tape.measurement == "density_matrix":
            return self.device.density_matrix(tape.circuit)
        if tape.measurement == "sample":
            shots = tape.measurement_shots if tape.measurement_shots is not None else (self.shots or 1)
            seed = tape.measurement_seed if tape.measurement_seed is not None else self.seed
            return self.device.sample(tape.circuit, wires=tape.measurement_wires, shots=shots, seed=seed)
        if tape.measurement == "counts":
            shots = tape.measurement_shots if tape.measurement_shots is not None else (self.shots or 1024)
            seed = tape.measurement_seed if tape.measurement_seed is not None else self.seed
            return self.device.counts(tape.circuit, wires=tape.measurement_wires, shots=shots, seed=seed)
        observable = tape.observable if tape.observable is not None else returned
        if tape.measurement == "var":
            return self.device.variance(tape.circuit, observable)
        return self.device.expectation(tape.circuit, observable)
