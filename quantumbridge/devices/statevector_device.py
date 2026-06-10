# Copyright 2026 QuantumBridge Contributors.
# Licensed under the Apache License, Version 2.0.
# This file is part of QuantumBridge SDK.
# This implementation is developed for the QuantumBridge native architecture.
# Design source: docs/mvp/simulator_design_v0.1.md and docs/mvp/api_contract_v0.1.md.

from __future__ import annotations

from numbers import Real
from typing import Mapping, Optional, Union

import numpy as np

from quantumbridge.core.parameters import Parameter
from quantumbridge.results import Result
from quantumbridge.utils.math import apply_unitary, expectation_observable, gate_matrix, probabilities_from_state, variance_observable


class StatevectorDevice:
    """Exact pure-state simulator for QuantumBridge MVP circuits."""

    def __init__(self, max_qubits: Optional[int] = None) -> None:
        self.max_qubits = max_qubits

    def _bound_circuit(self, circuit, parameters: Optional[Mapping[Union[Parameter, str], Real]]):
        return circuit.bind(parameters) if parameters else circuit

    def statevector(self, circuit, parameters: Optional[Mapping[Union[Parameter, str], Real]] = None) -> np.ndarray:
        circuit = self._bound_circuit(circuit, parameters)
        if self.max_qubits is not None and circuit.num_qubits > self.max_qubits:
            raise ValueError("QuantumBridge circuit exceeds this device qubit limit.")
        state = np.zeros(1 << circuit.num_qubits, dtype=complex)
        state[0] = 1.0
        for op in circuit.operations:
            matrix = gate_matrix(op.name, op.params, op.metadata)
            wires = op.controls + op.targets
            state = apply_unitary(state, matrix, wires, circuit.num_qubits)
        return state

    def probabilities(self, circuit, wires=None, parameters: Optional[Mapping[Union[Parameter, str], Real]] = None) -> dict[str, float]:
        state = self.statevector(circuit, parameters)
        return probabilities_from_state(state, circuit.num_qubits, wires)

    def expectation(self, circuit, observable, parameters: Optional[Mapping[Union[Parameter, str], Real]] = None) -> float:
        state = self.statevector(circuit, parameters)
        value = expectation_observable(state, circuit.num_qubits, observable)
        return float(np.real_if_close(value))

    def variance(self, circuit, observable, parameters: Optional[Mapping[Union[Parameter, str], Real]] = None) -> float:
        state = self.statevector(circuit, parameters)
        return variance_observable(state, circuit.num_qubits, observable)

    def density_matrix(self, circuit, parameters: Optional[Mapping[Union[Parameter, str], Real]] = None) -> np.ndarray:
        state = self.statevector(circuit, parameters)
        return np.outer(state, np.conjugate(state))

    def sample(
        self,
        circuit,
        wires=None,
        shots: int = 1,
        seed: int | None = None,
        parameters: Optional[Mapping[Union[Parameter, str], Real]] = None,
    ) -> list[str]:
        from quantumbridge.information import Statevector

        state = Statevector(self.statevector(circuit, parameters))
        return state.sample_memory(shots, qargs=wires, seed=seed)

    def counts(
        self,
        circuit,
        wires=None,
        shots: int = 1024,
        seed: int | None = None,
        parameters: Optional[Mapping[Union[Parameter, str], Real]] = None,
    ) -> dict[str, int]:
        counts: dict[str, int] = {}
        for bitstring in self.sample(circuit, wires=wires, shots=shots, seed=seed, parameters=parameters):
            counts[bitstring] = counts.get(bitstring, 0) + 1
        return counts

    def run(self, circuit, parameters: Optional[Mapping[Union[Parameter, str], Real]] = None, observable=None) -> Result:
        state = self.statevector(circuit, parameters)
        probs = probabilities_from_state(state, circuit.num_qubits)
        expectation = None if observable is None else float(np.real_if_close(expectation_observable(state, circuit.num_qubits, observable)))
        return Result(
            state=state,
            probabilities_data=probs,
            expectation_data=expectation,
            metadata_data={
                "device": "StatevectorDevice",
                "qubit_order": "q0-first bitstrings",
                "num_qubits": circuit.num_qubits,
            },
        )
