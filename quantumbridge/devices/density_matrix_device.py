# Copyright 2026 QuantumBridge Contributors.
# Licensed under the Apache License, Version 2.0.
# This implementation is developed for the QuantumBridge native architecture.

from __future__ import annotations

from numbers import Integral

import numpy as np

from quantumbridge.results import Result
from quantumbridge.utils.math import (
    apply_density_channel, apply_density_operator, observable_matrix,
)
from .execution import (
    apply_readout_distribution, condition_enabled, decision_liveness, readout_probability,
    prepare_program, validate_wires, needs_dynamic_engine,
)


class DensityMatrixDevice:
    """Native mixed-state simulation with local Kraus contractions and feedback."""

    simulation = "exact_density_matrix"
    supports_classical_control = True

    def __init__(self, max_qubits=None, noise_model=None, initial_state=None, max_branches=4096, max_memory_mb=1024, execution_limits=None):
        if max_qubits is not None and (not isinstance(max_qubits, Integral) or max_qubits < 1):
            raise ValueError("QuantumBridge density max_qubits must be a positive integer.")
        if not isinstance(max_branches, Integral) or max_branches < 1:
            raise ValueError("QuantumBridge max_branches must be a positive integer.")
        if max_memory_mb is not None and (not np.isfinite(max_memory_mb) or max_memory_mb <= 0):
            raise ValueError("QuantumBridge max_memory_mb must be positive or None.")
        self.max_qubits = max_qubits
        self.noise_model = noise_model
        self.initial_state = initial_state
        self.max_branches = int(max_branches)
        self.max_memory_mb = max_memory_mb
        self.execution_limits = execution_limits

    def with_noise_model(self, noise_model):
        return DensityMatrixDevice(self.max_qubits, noise_model, self.initial_state, self.max_branches, self.max_memory_mb, self.execution_limits)

    def with_initial_state(self, initial_state):
        return DensityMatrixDevice(self.max_qubits, self.noise_model, initial_state, self.max_branches, self.max_memory_mb, self.execution_limits)

    def _check_memory(self, width, branches=1):
        estimated = 16 * (1 << (2 * width)) * (6 + 2 * branches)
        if self.max_memory_mb is not None and estimated > self.max_memory_mb * 1024 ** 2:
            raise MemoryError("QuantumBridge dense simulation exceeds max_memory_mb; reduce width/branches or select another method.")

    def _initial(self, width):
        from quantumbridge.information.density_matrix import DensityMatrix

        self._check_memory(width)
        dimension = 1 << width
        if self.initial_state is None:
            density = np.zeros((dimension, dimension), dtype=complex)
            density[0, 0] = 1
            return density
        value = self.initial_state
        if hasattr(value, "data") and not isinstance(value, np.ndarray):
            value = value.data
        density = np.asarray(value, dtype=complex)
        if density.ndim == 1:
            density = np.outer(density, density.conj())
        if density.shape != (dimension, dimension) or not np.all(np.isfinite(density)):
            raise ValueError("QuantumBridge initial state must match circuit width and contain finite values.")
        if not DensityMatrix(density).is_valid():
            raise ValueError("QuantumBridge initial density matrix must be positive, Hermitian and trace one.")
        return np.array(density, copy=True)

    def _prepare(self, circuit, parameters=None):
        bound, program = prepare_program(circuit, parameters, self.max_qubits, self.noise_model)
        self._check_memory(bound.num_qubits)
        return bound, program

    @staticmethod
    def _apply(density, kind, value, wires, width):
        if kind == "gate":
            return apply_density_operator(density, value, wires, width)
        return apply_density_channel(density, value, wires, width)

    @staticmethod
    def _project(density, wire, outcome, width):
        mask = ((np.arange(1 << width) >> (width - 1 - wire)) & 1) == outcome
        probability = float(np.trace(density[np.ix_(mask, mask)]).real)
        probability = float(np.clip(probability, 0, 1))
        if probability <= 0:
            return None, 0.0
        return density * mask[:, None] * mask[None, :] / probability, probability

    @classmethod
    def _measure(cls, density, wire, width, rng):
        zero, p0 = cls._project(density, wire, 0, width)
        outcome = int(rng.random() >= p0)
        if outcome == 0:
            return zero, 0
        one, _ = cls._project(density, wire, 1, width)
        return one, 1

    @staticmethod
    def _merge(branches):
        grouped = {}
        for density, bits, decisions, weight in branches:
            key = (tuple(bits), tuple(sorted(decisions.items())))
            if key in grouped:
                value = grouped[key]
                value[0] += density * weight
                value[3] += weight
            else:
                grouped[key] = [density * weight, bits, decisions, weight]
        return [(value / weight, bits, decisions, weight) for value, bits, decisions, weight in grouped.values()]

    def _branches(self, circuit, program):
        if needs_dynamic_engine(circuit,self.noise_model):
            from quantumbridge.execution.control_flow_engine import dynamic_branches
            return dynamic_branches(self, circuit)
        width = circuit.num_qubits
        branches = [(self._initial(width), [0] * circuit.num_bits, {}, 1.0)]
        live = decision_liveness(program)
        for index, (kind, value, wires, metadata) in enumerate(program):
            updated = []
            for density, bits, decisions, weight in branches:
                if not condition_enabled(metadata, bits, decisions):
                    updated.append((density, bits, decisions, weight))
                elif kind != "measure":
                    updated.append((self._apply(density, kind, value, wires, width), bits, decisions, weight))
                else:
                    self._check_memory(width, len(branches) + len(updated) + 4)
                    for outcome in (0, 1):
                        projected, probability = self._project(density, value, outcome, width)
                        if not probability:
                            continue
                        readout = readout_probability(self.noise_model, value, outcome)
                        for flip, factor in ((0, 1 - readout), (1, readout)):
                            if factor:
                                recorded = bits.copy()
                                recorded[wires] = outcome ^ flip
                                updated.append((projected, recorded, decisions.copy(), weight * probability * factor))
            pruned = any(set(decisions) - live[index] for _, _, decisions, _ in updated)
            if pruned:
                updated = [(density, bits, {key: value for key, value in decisions.items() if key in live[index]}, weight)
                           for density, bits, decisions, weight in updated]
            branches = self._merge(updated) if kind == "measure" or pruned else updated
            if len(branches) > self.max_branches:
                raise RuntimeError("QuantumBridge exact density branches exceeded max_branches; use shot execution.")
        return branches

    def _trajectories(self, circuit, program, shots, seed):
        if needs_dynamic_engine(circuit,self.noise_model):
            from quantumbridge.execution.control_flow_engine import DynamicExecutionEngine
            yield from DynamicExecutionEngine(self, circuit).trajectories(shots, seed)
            return
        rng = np.random.default_rng(seed)
        width = circuit.num_qubits
        prefix, offset = self._initial(width), 0
        for kind, value, wires, metadata in program:
            if kind == "measure" or metadata.get("condition") or metadata.get("control_flow_stack"):
                break
            prefix = self._apply(prefix, kind, value, wires, width)
            offset += 1
        for _ in range(shots):
            density, bits, decisions = prefix.copy(), [0] * circuit.num_bits, {}
            for kind, value, wires, metadata in program[offset:]:
                if not condition_enabled(metadata, bits, decisions):
                    continue
                if kind == "measure":
                    density, outcome = self._measure(density, value, width, rng)
                    p = readout_probability(self.noise_model, value, outcome)
                    bits[wires] = outcome ^ int(p > 0 and rng.random() < p)
                else:
                    density = self._apply(density, kind, value, wires, width)
            yield density, bits, rng

    @staticmethod
    def _probabilities(density, selected, width):
        result = {}
        for index, value in enumerate(np.diag(density).real):
            label = "".join(str((index >> (width - 1 - wire)) & 1) for wire in selected)
            result[label] = result.get(label, 0.0) + max(0.0, float(value))
        return result

    def density_matrix(self, circuit, parameters=None):
        bound, program = self._prepare(circuit, parameters)
        return sum(weight * density for density, _, _, weight in self._branches(bound, program))

    state = density_matrix

    def reduced_density_matrix(self, circuit, wires=None, parameters=None):
        selected = validate_wires(wires, circuit.num_qubits)
        remaining = tuple(wire for wire in range(circuit.num_qubits) if wire not in selected)
        order = selected + remaining
        axes = order + tuple(circuit.num_qubits + wire for wire in order)
        tensor = self.density_matrix(circuit, parameters).reshape((2,) * (2 * circuit.num_qubits)).transpose(axes)
        size = 1 << len(selected)
        rest = 1 << len(remaining)
        return np.trace(tensor.reshape(size, rest, size, rest), axis1=1, axis2=3)

    def statevector(self, circuit, parameters=None):
        from quantumbridge.information.density_matrix import DensityMatrix

        return DensityMatrix(self.density_matrix(circuit, parameters)).to_statevector().data

    def probabilities(self, circuit, wires=None, parameters=None):
        selected = validate_wires(wires, circuit.num_qubits)
        return self._probabilities(self.density_matrix(circuit, parameters), selected, circuit.num_qubits)

    @staticmethod
    def _observable(observable, width):
        matrix = observable_matrix(observable, width)
        if matrix.shape != (1 << width, 1 << width) or not np.all(np.isfinite(matrix)) or not np.allclose(matrix, matrix.conj().T, atol=1e-10, rtol=0):
            raise ValueError("QuantumBridge density observables must be finite Hermitian matrices matching the circuit.")
        return matrix

    def expectation(self, circuit, observable, parameters=None):
        density = self.density_matrix(circuit, parameters)
        return float(np.trace(density @ self._observable(observable, circuit.num_qubits)).real)

    def variance(self, circuit, observable, parameters=None):
        density = self.density_matrix(circuit, parameters)
        matrix = self._observable(observable, circuit.num_qubits)
        mean = np.trace(density @ matrix).real
        return max(0.0, float(np.trace(density @ matrix @ matrix).real - mean ** 2))

    @staticmethod
    def _shots(shots, allow_zero=False):
        if isinstance(shots, bool) or not isinstance(shots, Integral) or shots < (0 if allow_zero else 1):
            raise ValueError("QuantumBridge density shots must be a positive integer (or zero for sample/counts).")

    def sample(self, circuit, wires=None, shots=1, seed=None, parameters=None):
        self._shots(shots, allow_zero=True)
        bound, program = self._prepare(circuit, parameters)
        if needs_dynamic_engine(bound,self.noise_model):
            from quantumbridge.execution.control_flow_engine import DynamicExecutionEngine
            return DynamicExecutionEngine(self, bound).quantum_samples(wires, shots, seed)
        selected = validate_wires(wires, bound.num_qubits)
        if not bound.measurements:
            density = sum(weight * state for state, _, _, weight in self._branches(bound, program))
            probabilities = apply_readout_distribution(self._probabilities(density, selected, bound.num_qubits), self.noise_model, selected)
            labels = sorted(probabilities)
            weights = np.array([probabilities[label] for label in labels])
            return np.random.default_rng(seed).choice(labels, size=shots, p=weights / weights.sum()).tolist()
        memory = []
        for density, _, rng in self._trajectories(bound, program, shots, seed):
            outcomes = []
            for wire in selected:
                density, outcome = self._measure(density, wire, bound.num_qubits, rng)
                p = readout_probability(self.noise_model, wire, outcome)
                outcomes.append(str(outcome ^ int(p > 0 and rng.random() < p)))
            memory.append("".join(outcomes))
        return memory

    @staticmethod
    def _counts(memory):
        counts = {}
        for label in memory:
            counts[label] = counts.get(label, 0) + 1
        return counts

    def counts(self, circuit, wires=None, shots=1024, seed=None, parameters=None):
        return self._counts(self.sample(circuit, wires=wires, shots=shots, seed=seed, parameters=parameters))

    def _metadata(self, circuit):
        return {"device": "DensityMatrixDevice", "simulation": self.simulation,
                "num_qubits": circuit.num_qubits, "qubit_order": "q0-first bitstrings",
                "classical_order": "c0-first bitstrings",
                "noise_model_metadata": {} if self.noise_model is None else self.noise_model.summary()}

    def run_shots(self, circuit, shots=1024, seed=None, parameters=None, memory=False):
        if needs_dynamic_engine(circuit,self.noise_model):
            from quantumbridge.execution.control_flow_engine import dynamic_shots
            return dynamic_shots(self, circuit, shots, seed, parameters, memory)
        self._shots(shots)
        bound, program = self._prepare(circuit, parameters)
        if bound.measurements:
            samples = ["".join(map(str, bits)) for _, bits, _ in self._trajectories(bound, program, shots, seed)]
        else:
            samples = self.sample(bound, shots=shots, seed=seed)
        counts = self._counts(samples)
        metadata = {**self._metadata(bound), "shots": int(shots), "seed": seed,
                    "num_bits": bound.num_bits if bound.measurements else bound.num_qubits}
        if memory:
            metadata["memory"] = samples
        return Result(counts_data=counts, probabilities_data={key: value / shots for key, value in counts.items()}, metadata_data=metadata)

    def run(self, circuit, parameters=None, observable=None):
        bound, program = self._prepare(circuit, parameters)
        branches = self._branches(bound, program)
        density = sum(weight * state for state, _, _, weight in branches)
        expectation = None
        if observable is not None:
            expectation = float(np.trace(density @ self._observable(observable, bound.num_qubits)).real)
        if bound.has_measurements:
            probabilities = {}
            for _, bits, _, weight in branches:
                label = "".join(map(str, bits))
                probabilities[label] = probabilities.get(label, 0.0) + weight
        else:
            probabilities = apply_readout_distribution(self._probabilities(density, range(bound.num_qubits), bound.num_qubits), self.noise_model, range(bound.num_qubits))
        return Result(density=density, probabilities_data=probabilities, expectation_data=expectation,
                      metadata_data={**self._metadata(bound), **getattr(branches, "metadata", {})})
