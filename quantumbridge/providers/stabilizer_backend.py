# Copyright 2026 QuantumBridge Contributors.
# Licensed under the Apache License, Version 2.0.
# This implementation is developed for the QuantumBridge native architecture.

from quantumbridge.core import Circuit
from quantumbridge.devices import StabilizerDevice

from .backend import BackendV2, _as_circuit_sequence, _parameter_sets_for_circuits


class StabilizerBackend(BackendV2):
    """Native Backend/Job execution for Clifford circuits and classical feedback."""

    def __init__(self, name="stabilizer", max_qubits=None, noise_model=None, max_branches=100000, **options):
        device = StabilizerDevice(max_qubits=max_qubits, noise_model=noise_model, max_branches=max_branches)
        defaults = {"shots": 1024, **options}
        super().__init__(name=name, device=device, max_qubits=max_qubits,
                         basis_gates=("id", "x", "y", "z", "h", "s", "sdg", "sx", "sxdg", "cx", "cy", "cz", "swap", "dcx", "ecr", "iswap", "reset"),
                         **defaults)

    def _execute(self, circuits, options, parameter_values=None, observable=None):
        circuit_sequence = _as_circuit_sequence(circuits)
        parameter_sets = _parameter_sets_for_circuits(parameter_values, len(circuit_sequence))
        device = self.device
        if "noise_model" in options:
            device = StabilizerDevice(self.max_qubits, options.get("noise_model"), self.device.max_branches)
        results = []
        for circuit, parameters in zip(circuit_sequence, parameter_sets):
            self._validate_circuit(circuit)
            if observable is not None or options.get("shots") is None:
                result = device.run(circuit, parameters=parameters, observable=observable)
            else:
                result = device.run_shots(circuit, shots=options.shots, seed=options.get("seed_simulator"),
                                          parameters=parameters, memory=options.get("memory", False))
            result.metadata_data["backend_name"] = self.name
            results.append(result)
        return results[0] if isinstance(circuits, Circuit) else results
