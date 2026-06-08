# Copyright 2026 QuantumBridge Contributors.
# Licensed under the Apache License, Version 2.0.
# This file is independently implemented for QuantumBridge SDK.
# No source code from Qiskit or PennyLane was copied.
# Design source: docs/roadmap/p2_execution_plan_v0.1.md.

from __future__ import annotations

import numpy as np

from quantumbridge.devices import StatevectorDevice
from quantumbridge.results import Result
from quantumbridge.utils.math import bit_at, expectation_hamiltonian, probabilities_from_state, set_bit


def _apply_single_qubit_kraus_density(rho: np.ndarray, kraus_ops, wire: int, num_qubits: int) -> np.ndarray:
    dim = 1 << num_qubits
    out = np.zeros_like(rho, dtype=complex)
    for kraus in kraus_ops:
        full = np.zeros((dim, dim), dtype=complex)
        for col in range(dim):
            col_bit = bit_at(col, wire, num_qubits)
            base = set_bit(col, wire, 0, num_qubits)
            for row_bit in (0, 1):
                row = set_bit(base, wire, row_bit, num_qubits)
                full[row, col] = kraus[row_bit, col_bit]
        out += full @ rho @ full.conj().T
    return out


def _density_probabilities(rho: np.ndarray, num_qubits: int) -> dict[str, float]:
    probs = {}
    for index, value in enumerate(np.real(np.diag(rho))):
        key = "".join(str(bit_at(index, wire, num_qubits)) for wire in range(num_qubits))
        probs[key] = max(0.0, float(value))
    total = sum(probs.values())
    return {key: value / total for key, value in probs.items()} if total else probs


def _apply_readout(probabilities: dict[str, float], readout_errors, num_qubits: int) -> dict[str, float]:
    out = dict(probabilities)
    for wire, error in readout_errors.items():
        updated = {key: 0.0 for key in out}
        for key, prob in out.items():
            bit = key[wire]
            flipped = key[:wire] + ("1" if bit == "0" else "0") + key[wire + 1 :]
            if bit == "0":
                updated[key] = updated.get(key, 0.0) + (1 - error.p0_to_1) * prob
                updated[flipped] = updated.get(flipped, 0.0) + error.p0_to_1 * prob
            else:
                updated[key] = updated.get(key, 0.0) + (1 - error.p1_to_0) * prob
                updated[flipped] = updated.get(flipped, 0.0) + error.p1_to_0 * prob
        out = updated
    return out


class NoisySampler:
    def __init__(self, shots: int, noise_model, seed: int | None = None, base_device=None):
        self.shots = int(shots)
        if self.shots <= 0:
            raise ValueError("QuantumBridge NoisySampler shots must be positive.")
        self.noise_model = noise_model
        self.seed = seed
        self.base_device = base_device or StatevectorDevice()

    def probabilities(self, circuit) -> dict[str, float]:
        state = self.base_device.statevector(circuit)
        rho = np.outer(state, state.conj())
        for entry in self.noise_model.channels:
            channel = entry["channel"]
            wires = tuple(range(circuit.num_qubits)) if entry["wires"] is None else entry["wires"]
            for wire in wires:
                rho = _apply_single_qubit_kraus_density(rho, channel.kraus(), wire, circuit.num_qubits)
        probs = _density_probabilities(rho, circuit.num_qubits)
        return _apply_readout(probs, self.noise_model.readout_errors, circuit.num_qubits)

    def run(self, circuit) -> Result:
        probabilities = self.probabilities(circuit)
        labels = sorted(probabilities)
        weights = np.array([probabilities[label] for label in labels], dtype=float)
        weights = weights / weights.sum()
        rng = np.random.default_rng(self.seed)
        draws = rng.choice(labels, size=self.shots, p=weights)
        counts = {label: int(np.count_nonzero(draws == label)) for label in labels}
        counts = {label: count for label, count in counts.items() if count}
        return Result(
            probabilities_data={label: count / self.shots for label, count in counts.items()},
            counts_data=counts,
            metadata_data={
                "device": "NoisySampler",
                "shots": self.shots,
                "seed": self.seed,
                "noise_model_metadata": self.noise_model.summary(),
                "provenance": {"mode": "Native Core", "component": "quantumbridge.noise"},
            },
        )


class NoisyEstimator:
    def __init__(self, noise_model, seed: int | None = None, base_device=None):
        self.noise_model = noise_model
        self.seed = seed
        self.base_device = base_device or StatevectorDevice()

    def expectation(self, circuit, observable) -> float:
        sampler = NoisySampler(20000, self.noise_model, self.seed, self.base_device)
        probs = sampler.probabilities(circuit)
        if hasattr(observable, "terms"):
            value = 0.0
            for bitstring, prob in probs.items():
                sign = 1.0
                for wire, label in observable.terms:
                    if label == "Z" and bitstring[wire] == "1":
                        sign *= -1
                value += sign * prob
            return float(value)
        state = self.base_device.statevector(circuit)
        return expectation_hamiltonian(state, circuit.num_qubits, observable)

    def run(self, circuit, observable) -> Result:
        value = self.expectation(circuit, observable)
        return Result(
            expectation_data=value,
            metadata_data={
                "device": "NoisyEstimator",
                "seed": self.seed,
                "noise_model_metadata": self.noise_model.summary(),
                "provenance": {"mode": "Native Core", "component": "quantumbridge.noise"},
            },
        )
