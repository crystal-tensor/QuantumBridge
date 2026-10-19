# Copyright 2026 QuantumBridge Contributors.
# Licensed under the Apache License, Version 2.0.
# This file is part of QuantumBridge SDK.
# This implementation is developed for the QuantumBridge native architecture.

from quantumbridge.core import Circuit
from .measurements import MeasurementRequest, normalize_wires


class Tape:
    def __init__(self, num_qubits: int):
        self.circuit = Circuit(num_qubits)
        self.observable = None
        self.measurement = None
        self.measurement_wires = None
        self.measurement_shots = None
        self.measurement_seed = None
        self.measurements: list[MeasurementRequest] = []

    def _record_measurement(self, request: MeasurementRequest):
        self.measurements.append(request)
        self.observable = request.observable
        self.measurement = request.kind
        self.measurement_wires = request.wires
        self.measurement_shots = request.shots
        self.measurement_seed = request.seed
        return request

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

    def kraus(self, operators, wires):
        self.circuit.kraus(operators, normalize_wires(wires))

    def channel(self, channel, wires):
        self.circuit.channel(channel, normalize_wires(wires))

    def amplitude_damping(self, probability, wire):
        from quantumbridge.noise.channels import AmplitudeDampingChannel

        self.channel(AmplitudeDampingChannel(probability), wire)

    def phase_damping(self, probability, wire):
        from quantumbridge.noise.channels import PhaseDampingChannel

        self.channel(PhaseDampingChannel(probability), wire)

    def depolarizing(self, probability, wire):
        from quantumbridge.noise.channels import DepolarizingChannel

        self.channel(DepolarizingChannel(probability), wire)

    def bit_flip(self, probability, wire):
        from quantumbridge.noise.channels import BitFlipChannel

        self.channel(BitFlipChannel(probability), wire)

    def phase_flip(self, probability, wire):
        from quantumbridge.noise.channels import PhaseFlipChannel

        self.channel(PhaseFlipChannel(probability), wire)

    def expval(self, observable):
        return self._record_measurement(MeasurementRequest("expval", observable=observable))

    def var(self, observable):
        return self._record_measurement(MeasurementRequest("var", observable=observable))

    def probs(self, wires=None):
        return self._record_measurement(MeasurementRequest("probs", wires=normalize_wires(wires)))

    def sample(self, wires=None, shots=None, seed=None):
        return self._record_measurement(MeasurementRequest("sample", wires=normalize_wires(wires), shots=shots, seed=seed))

    def counts(self, wires=None, shots=None, seed=None):
        return self._record_measurement(MeasurementRequest("counts", wires=normalize_wires(wires), shots=shots, seed=seed))

    def state(self):
        return self._record_measurement(MeasurementRequest("state"))

    def density_matrix(self, wires=None):
        return self._record_measurement(MeasurementRequest("density_matrix", wires=normalize_wires(wires)))

    def classical_shadow(self, wires=None, shots=None, seed=None):
        return self._record_measurement(
            MeasurementRequest("classical_shadow", wires=normalize_wires(wires), shots=shots, seed=seed)
        )

    def shadow_expval(self, observable, wires=None, shots=None, seed=None, k=None):
        return self._record_measurement(
            MeasurementRequest(
                "shadow_expval",
                observable=observable,
                wires=normalize_wires(wires),
                shots=shots,
                seed=seed,
                metadata={"k": k} if k is not None else None,
            )
        )
