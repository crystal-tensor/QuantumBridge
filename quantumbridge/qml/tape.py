# Copyright 2026 QuantumBridge Contributors.
# Licensed under the Apache License, Version 2.0.
# This file is part of QuantumBridge SDK.
# This implementation is developed for the QuantumBridge native architecture.

from copy import deepcopy

from quantumbridge.core import Circuit
from .measurements import MeasurementRequest, normalize_wires


class Tape:
    def __init__(self, num_qubits: int, parameter_transform=None, *, shots=None, seed=None):
        self.circuit = Circuit(num_qubits)
        self.parameter_transform = parameter_transform or (lambda value: value)
        self.observable = None
        self.measurement = None
        self.measurement_wires = None
        self.measurement_shots = None
        self.measurement_seed = None
        self.measurements: list[MeasurementRequest] = []
        self.output_tree = None
        self.shots, self.seed = shots, seed

    def set_output(self, tree):
        """Retain an explicit nested terminal-measurement return structure."""
        pending, count = [(tree, 0)], 0
        recorded = {id(request) for request in self.measurements}
        while pending:
            value, depth = pending.pop()
            count += 1
            if count > 100000 or depth > 64:
                raise MemoryError("Tape output structure exceeds the native budget.")
            if isinstance(value, MeasurementRequest):
                if id(value) not in recorded:
                    raise ValueError("Tape outputs must refer to its recorded measurements.")
            elif isinstance(value, (dict, tuple, list)) and value:
                values = value.values() if isinstance(value, dict) else value
                pending.extend((child, depth + 1) for child in values)
            else:
                raise TypeError("Tape outputs require a nonempty measurement tree.")
        self.output_tree = tree
        return self

    def copy(self):
        """Copy owned structure without detaching scalar parameter graphs."""
        memo = {id(self.parameter_transform): self.parameter_transform}
        pending, seen = [self.circuit], set()
        while pending:
            circuit = pending.pop()
            if id(circuit) in seen:
                continue
            seen.add(id(circuit))
            memo[id(circuit.global_phase)] = circuit.global_phase
            for operation in circuit.operations:
                for value in operation.params:
                    memo[id(value)] = value
                node = operation.metadata.get("control_node")
                if node is not None:
                    pending.extend(node.bodies)
        return deepcopy(self, memo)

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
        self.circuit.rx(self.parameter_transform(theta), wire)

    def ry(self, theta, wire: int):
        self.circuit.ry(self.parameter_transform(theta), wire)

    def rz(self, theta, wire: int):
        self.circuit.rz(self.parameter_transform(theta), wire)

    def phase(self, theta, wire: int):
        self.circuit.phase(self.parameter_transform(theta), wire)

    def rot(self, phi, theta, omega, wire: int):
        self.rz(phi, wire)
        self.ry(theta, wire)
        self.rz(omega, wire)

    def crx(self, theta, control, target):
        self.circuit.crx(self.parameter_transform(theta), control, target)

    def cry(self, theta, control, target):
        self.circuit.cry(self.parameter_transform(theta), control, target)

    def crz(self, theta, control, target):
        self.circuit.crz(self.parameter_transform(theta), control, target)

    def cp(self, theta, control, target):
        self.circuit.cp(self.parameter_transform(theta), control, target)

    def rxx(self, theta, a, b):
        self.circuit.rxx(self.parameter_transform(theta), a, b)

    def ryy(self, theta, a, b):
        self.circuit.ryy(self.parameter_transform(theta), a, b)

    def rzz(self, theta, a, b):
        self.circuit.rzz(self.parameter_transform(theta), a, b)

    def cx(self, control: int, target: int):
        self.circuit.cx(control, target)

    def cz(self, control: int, target: int):
        self.circuit.cz(control, target)

    def swap(self, a: int, b: int):
        self.circuit.swap(a, b)

    def measure(self, wire, reset=False):
        from quantumbridge.core.classical import bit
        position = self.circuit.num_bits
        self.circuit.num_bits += 1
        self.circuit.measure(wire, position)
        if reset: self.circuit.reset(wire)
        return bit(position)

    def cond(self, condition, true_fn, false_fn=None):
        from quantumbridge.core.classical import ClassicalExpression
        if not isinstance(condition, ClassicalExpression):
            raise TypeError("QuantumBridge Tape.cond requires a runtime classical expression.")
        def record(fn):
            if fn is None: return None
            branch = Tape(self.circuit.num_qubits, self.parameter_transform)
            branch.circuit.num_bits = self.circuit.num_bits
            fn(branch)
            if branch.measurements:
                raise ValueError("QuantumBridge conditional Tape callbacks cannot return terminal measurements.")
            self.circuit.num_bits = max(self.circuit.num_bits, branch.circuit.num_bits)
            return branch.circuit
        true, false = record(true_fn), record(false_fn)
        if true is None: raise TypeError("QuantumBridge Tape.cond requires a true callback.")
        true.num_bits = self.circuit.num_bits
        if false is not None: false.num_bits = self.circuit.num_bits
        self.circuit.if_else(condition, true, false, inplace=True)

    def reset(self, wire):
        self.circuit.reset(wire)

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
