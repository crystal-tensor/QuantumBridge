# Copyright 2026 QuantumBridge Contributors.
# Licensed under the Apache License, Version 2.0.
# This file is part of QuantumBridge SDK.
# This implementation is developed for the QuantumBridge native architecture.

from __future__ import annotations

from dataclasses import dataclass

from .coupling import CouplingMap


@dataclass(frozen=True)
class Target:
    num_qubits: int
    basis_gates: tuple[str, ...]
    coupling_map: CouplingMap | None = None
    dt: float | None = None

    def __init__(self, num_qubits: int, basis_gates, coupling_map=None, dt: float | None = None):
        object.__setattr__(self, "num_qubits", int(num_qubits))
        object.__setattr__(self, "basis_gates", tuple(str(gate) for gate in basis_gates))
        if coupling_map is None or isinstance(coupling_map, CouplingMap):
            normalized_coupling = coupling_map
        else:
            normalized_coupling = CouplingMap(coupling_map)
        object.__setattr__(self, "coupling_map", normalized_coupling)
        object.__setattr__(self, "dt", None if dt is None else float(dt))

    @classmethod
    def from_backend(cls, backend) -> "Target":
        config = backend.configuration() if hasattr(backend, "configuration") else {}
        num_qubits = getattr(backend, "max_qubits", config.get("n_qubits", config.get("num_qubits", 1)))
        basis_gates = getattr(backend, "basis_gates", config.get("basis_gates", ()))
        coupling = config.get("coupling_map")
        return cls(num_qubits=num_qubits, basis_gates=basis_gates, coupling_map=coupling)

    def supports_operation(self, name: str) -> bool:
        return str(name) in set(self.basis_gates)

    def is_connected(self, left: int, right: int) -> bool:
        if self.coupling_map is None:
            return True
        return self.coupling_map.is_connected(left, right)

    def to_dict(self) -> dict:
        return {
            "num_qubits": self.num_qubits,
            "basis_gates": list(self.basis_gates),
            "coupling_map": None if self.coupling_map is None else [list(edge) for edge in self.coupling_map.edges],
            "dt": self.dt,
        }
