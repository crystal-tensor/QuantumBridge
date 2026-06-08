# Copyright 2026 QuantumBridge Contributors.
# Licensed under the Apache License, Version 2.0.
# This file is part of QuantumBridge SDK.
# This implementation is developed for the QuantumBridge native architecture.

from quantumbridge.core import Circuit


class Tape:
    def __init__(self, num_qubits: int):
        self.circuit = Circuit(num_qubits)
        self.observable = None
        self.measurement = None
        self.measurement_wires = None

    def x(self, wire: int):
        self.circuit.x(wire)

    def y(self, wire: int):
        self.circuit.y(wire)

    def z(self, wire: int):
        self.circuit.z(wire)

    def h(self, wire: int):
        self.circuit.h(wire)

    def rx(self, theta, wire: int):
        self.circuit.rx(theta, wire)

    def ry(self, theta, wire: int):
        self.circuit.ry(theta, wire)

    def rz(self, theta, wire: int):
        self.circuit.rz(theta, wire)

    def phase(self, theta, wire: int):
        self.circuit.phase(theta, wire)

    def rot(self, phi, theta, omega, wire: int):
        self.circuit.rz(phi, wire)
        self.circuit.ry(theta, wire)
        self.circuit.rz(omega, wire)

    def cx(self, control: int, target: int):
        self.circuit.cx(control, target)

    def cz(self, control: int, target: int):
        self.circuit.cz(control, target)

    def swap(self, a: int, b: int):
        self.circuit.swap(a, b)

    def expval(self, observable):
        self.observable = observable
        self.measurement = "expval"
        return observable

    def probs(self, wires=None):
        self.measurement = "probs"
        self.measurement_wires = None if wires is None else tuple(wires)
        return self.measurement

    def sample(self, wires=None):
        self.measurement = "sample"
        self.measurement_wires = None if wires is None else tuple(wires)
        return self.measurement

    def state(self):
        self.measurement = "state"
        return self.measurement
