# Copyright 2026 QuantumBridge Contributors.
# Licensed under the Apache License, Version 2.0.
# This file is part of QuantumBridge SDK.
# This implementation is developed for the QuantumBridge native architecture.

from __future__ import annotations

import numpy as np

from quantumbridge.devices import StatevectorDevice
from quantumbridge.utils.math import Hamiltonian, PauliString
from .measurements import ClassicalShadowResult, MeasurementRequest
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
        requests = _returned_measurements(returned) or tuple(tape.measurements)
        if requests:
            results = tuple(self._execute_measurement(tape, request) for request in requests)
            return results[0] if len(results) == 1 else results
        observable = tape.observable if tape.observable is not None else returned
        if tape.measurement == "var":
            return self.device.variance(tape.circuit, observable)
        return self.device.expectation(tape.circuit, observable)

    def _execute_measurement(self, tape: Tape, request: MeasurementRequest):
        wires = _validate_wires(request.wires, self.num_qubits)
        if request.kind == "expval":
            return self.device.expectation(tape.circuit, request.observable)
        if request.kind == "var":
            return self.device.variance(tape.circuit, request.observable)
        if request.kind == "probs":
            return self.device.probabilities(tape.circuit, wires=wires)
        if request.kind == "state":
            if hasattr(self.device, "state"):
                return self.device.state(tape.circuit)
            return self.device.statevector(tape.circuit)
        if request.kind == "density_matrix":
            matrix = self.device.density_matrix(tape.circuit)
            return matrix if wires is None else _partial_density_matrix(matrix, self.num_qubits, wires)
        if request.kind == "sample":
            shots = _resolve_shots(request.shots, self.shots, "sample")
            seed = request.seed if request.seed is not None else self.seed
            return self.device.sample(tape.circuit, wires=wires, shots=shots, seed=seed)
        if request.kind == "counts":
            shots = _resolve_shots(request.shots, self.shots, "counts")
            seed = request.seed if request.seed is not None else self.seed
            return self.device.counts(tape.circuit, wires=wires, shots=shots, seed=seed)
        if request.kind == "classical_shadow":
            shots = _resolve_shots(request.shots, self.shots, "classical_shadow")
            seed = request.seed if request.seed is not None else self.seed
            return _classical_shadow(self.device, tape.circuit, self.num_qubits, wires, shots, seed)
        if request.kind == "shadow_expval":
            shots = _resolve_shots(request.shots, self.shots, "shadow_expval")
            seed = request.seed if request.seed is not None else self.seed
            shadow = _classical_shadow(self.device, tape.circuit, self.num_qubits, wires, shots, seed)
            k = None if request.metadata is None else request.metadata.get("k")
            return _shadow_expectation(shadow, request.observable, k=k)
        raise ValueError(f"Unsupported QuantumBridge QML measurement kind: {request.kind!r}")


def _returned_measurements(returned) -> tuple[MeasurementRequest, ...]:
    if isinstance(returned, MeasurementRequest):
        return (returned,)
    if isinstance(returned, (list, tuple)) and all(isinstance(item, MeasurementRequest) for item in returned):
        return tuple(returned)
    return ()


def _validate_wires(wires: tuple[int, ...] | None, num_qubits: int) -> tuple[int, ...] | None:
    if wires is None:
        return None
    selected = tuple(wires)
    if len(set(selected)) != len(selected):
        raise ValueError("QuantumBridge QML measurement wires must be unique.")
    if any(wire < 0 or wire >= num_qubits for wire in selected):
        raise ValueError(f"QuantumBridge QML measurement wires must be in [0, {num_qubits}).")
    return selected


def _resolve_shots(request_shots, node_shots, measurement: str) -> int:
    shots = request_shots if request_shots is not None else node_shots
    if isinstance(shots, bool) or not isinstance(shots, (int, np.integer)) or shots <= 0:
        raise ValueError(f"QuantumBridge QML {measurement} requires a positive integer number of shots.")
    return int(shots)


def _partial_density_matrix(matrix: np.ndarray, num_qubits: int, wires: tuple[int, ...]) -> np.ndarray:
    selected = tuple(wires)
    traced = tuple(wire for wire in range(num_qubits) if wire not in selected)
    size = 1 << len(selected)
    reduced = np.zeros((size, size), dtype=complex)
    for row in range(1 << num_qubits):
        for col in range(1 << num_qubits):
            if all(_bit(row, wire, num_qubits) == _bit(col, wire, num_qubits) for wire in traced):
                reduced[
                    _project_index(row, selected, num_qubits),
                    _project_index(col, selected, num_qubits),
                ] += matrix[row, col]
    return reduced


def _bit(index: int, wire: int, num_qubits: int) -> int:
    return (index >> (num_qubits - 1 - wire)) & 1


def _project_index(index: int, wires: tuple[int, ...], num_qubits: int) -> int:
    out = 0
    for wire in wires:
        out = (out << 1) | _bit(index, wire, num_qubits)
    return out


def _classical_shadow(device, circuit, num_qubits: int, wires: tuple[int, ...] | None, shots: int, seed: int | None):
    selected = tuple(range(num_qubits)) if wires is None else tuple(wires)
    rng = np.random.default_rng(seed)
    recipes = rng.integers(0, 3, size=(shots, len(selected)), dtype=np.int8)
    bits = np.zeros((shots, len(selected)), dtype=np.int8)
    unique_recipes, groups = np.unique(recipes, axis=0, return_inverse=True)
    for group, recipe_row in enumerate(unique_recipes):
        indices = np.flatnonzero(groups == group)
        rotated = circuit.copy()
        for wire, recipe_value in zip(selected, recipe_row):
            recipe = int(recipe_value)
            if recipe == 0:
                rotated.h(wire)
            elif recipe == 1:
                rotated.sdg(wire)
                rotated.h(wire)
        group_seed = int(rng.integers(0, 2**32 - 1))
        samples = device.sample(rotated, wires=selected, shots=len(indices), seed=group_seed)
        for index, bitstring in zip(indices, samples):
            bits[index] = np.fromiter((int(bit) for bit in bitstring), dtype=np.int8, count=len(selected))
    return ClassicalShadowResult(
        bits=bits,
        recipes=recipes,
        wires=selected,
        metadata={
            "measurement": "classical_shadow",
            "shots": shots,
            "seed": seed,
            "recipe_encoding": {"X": 0, "Y": 1, "Z": 2},
        },
    )


def _shadow_expectation(shadow: ClassicalShadowResult, observable, k=None):
    if isinstance(observable, (list, tuple)):
        return np.asarray([_shadow_expectation(shadow, item, k=k) for item in observable], dtype=float)
    per_shot = _shadow_observable_samples(shadow, observable)
    partitions = _resolve_shadow_partitions(k, len(per_shot))
    means = [float(np.mean(partition)) for partition in np.array_split(per_shot, partitions)]
    return float(np.median(means))


def _shadow_observable_samples(shadow: ClassicalShadowResult, observable) -> np.ndarray:
    if hasattr(observable, "to_hamiltonian"):
        observable = observable.to_hamiltonian()
    if isinstance(observable, PauliString):
        return _shadow_pauli_samples(shadow, observable)
    if isinstance(observable, Hamiltonian):
        estimate = np.zeros(len(shadow.bits), dtype=float)
        for coefficient, pauli in observable.terms:
            estimate += coefficient * _shadow_pauli_samples(shadow, pauli)
        return estimate
    raise TypeError("QuantumBridge shadow_expval supports PauliString and Hamiltonian observables.")


def _shadow_pauli_samples(shadow: ClassicalShadowResult, observable: PauliString) -> np.ndarray:
    wire_positions = {wire: offset for offset, wire in enumerate(shadow.wires)}
    seen: set[int] = set()
    estimate = np.ones(len(shadow.bits), dtype=float)
    recipe_for = {"X": 0, "Y": 1, "Z": 2}
    for wire, label in observable.terms:
        if label == "I":
            continue
        if wire in seen:
            raise ValueError("QuantumBridge shadow_expval Pauli terms must use unique wires.")
        seen.add(wire)
        if wire not in wire_positions:
            raise ValueError(f"Observable wire {wire} is not present in the classical shadow wires.")
        offset = wire_positions[wire]
        matches = shadow.recipes[:, offset] == recipe_for[label]
        eigenvalues = 1.0 - 2.0 * shadow.bits[:, offset]
        estimate *= np.where(matches, 3.0 * eigenvalues, 0.0)
    return estimate


def _resolve_shadow_partitions(k, shots: int) -> int:
    if k is None:
        return 1
    if isinstance(k, bool) or not isinstance(k, (int, np.integer)) or k <= 0 or k > shots:
        raise ValueError("QuantumBridge shadow_expval k must be a positive integer no larger than shots.")
    return int(k)
