#!/usr/bin/env python3
# This file is independently implemented for QuantumBridge SDK.
# No source code from Qiskit or PennyLane was copied.
"""Generate Qiskit Dynamics public API inventories."""

from quantumbridge.compat.qiskit_dynamics.backend_adapter import ADAPTER as BACKEND
from quantumbridge.compat.qiskit_dynamics.model_adapter import ADAPTER as MODEL
from quantumbridge.compat.qiskit_dynamics.signal_adapter import ADAPTER as SIGNAL
from quantumbridge.compat.qiskit_dynamics.solver_adapter import ADAPTER as SOLVER
from quantumbridge.ecosystem.registry import EcosystemAdapter, write_inventory

EXTENDED = EcosystemAdapter(
    "qiskit-dynamics",
    "qiskit-dynamics",
    ("qiskit_dynamics.perturbation", "qiskit_dynamics.array"),
    "qiskit-dynamics",
    "qiskit_dynamics_extended",
)


def main() -> None:
    for adapter in (SOLVER, MODEL, SIGNAL, BACKEND, EXTENDED):
        inventory_path, matrix_path = write_inventory(adapter)
        print(f"wrote {inventory_path} and {matrix_path}")


if __name__ == "__main__":
    main()
