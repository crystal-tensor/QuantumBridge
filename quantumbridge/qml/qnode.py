# Copyright 2026 QuantumBridge Contributors.
# Licensed under the Apache License, Version 2.0.
# This file is part of QuantumBridge SDK.
# This implementation is developed for the QuantumBridge native architecture.

from quantumbridge.devices import StatevectorDevice
from .tape import Tape


class QNode:
    def __init__(self, fn, num_qubits: int, device=None):
        self.fn = fn
        self.num_qubits = num_qubits
        self.device = device or StatevectorDevice()

    def __call__(self, *args, **kwargs):
        tape = Tape(self.num_qubits)
        returned = self.fn(tape, *args, **kwargs)
        if tape.measurement == "probs":
            return self.device.probabilities(tape.circuit, wires=tape.measurement_wires)
        if tape.measurement == "state":
            return self.device.statevector(tape.circuit)
        observable = tape.observable if tape.observable is not None else returned
        return self.device.expectation(tape.circuit, observable)
