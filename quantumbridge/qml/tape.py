# Copyright 2026 QuantumBridge Contributors.
# Licensed under the Apache License, Version 2.0.
# This file is part of QuantumBridge SDK.
# This implementation is developed for the QuantumBridge native architecture.

from quantumbridge.core import Circuit


class Tape:
    def __init__(self, num_qubits: int):
        self.circuit = Circuit(num_qubits)
        self.observable = None

    def x(self, wire: int):
        self.circuit.x(wire)

    def h(self, wire: int):
        self.circuit.h(wire)

    def rx(self, theta, wire: int):
        self.circuit.rx(theta, wire)

    def ry(self, theta, wire: int):
        self.circuit.ry(theta, wire)

    def rz(self, theta, wire: int):
        self.circuit.rz(theta, wire)

    def cx(self, control: int, target: int):
        self.circuit.cx(control, target)

    def expval(self, observable):
        self.observable = observable
        return observable

