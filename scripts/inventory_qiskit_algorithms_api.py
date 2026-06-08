#!/usr/bin/env python3
# This file is independently implemented for QuantumBridge SDK.
# No source code from Qiskit or PennyLane was copied.
"""Generate Qiskit Algorithms public API inventories."""

from quantumbridge.compat.qiskit_algorithms.amplitude_adapter import ADAPTER as AMPLITUDE
from quantumbridge.compat.qiskit_algorithms.eigensolver_adapter import ADAPTER as EIGENSOLVER
from quantumbridge.compat.qiskit_algorithms.gradient_adapter import ADAPTER as GRADIENT
from quantumbridge.compat.qiskit_algorithms.grover_adapter import ADAPTER as GROVER
from quantumbridge.compat.qiskit_algorithms.minimum_eigensolver_adapter import ADAPTER as MINIMUM
from quantumbridge.compat.qiskit_algorithms.optimizer_adapter import ADAPTER as OPTIMIZER
from quantumbridge.ecosystem.registry import EcosystemAdapter, write_inventory

EXTENDED = EcosystemAdapter(
    "qiskit-algorithms",
    "qiskit-algorithms",
    (
        "qiskit_algorithms.state_fidelities",
        "qiskit_algorithms.time_evolvers",
        "qiskit_algorithms.phase_estimators",
    ),
    "qiskit-algorithms",
    "qiskit_algorithms_extended",
)


def main() -> None:
    for adapter in (EIGENSOLVER, MINIMUM, AMPLITUDE, GROVER, OPTIMIZER, GRADIENT, EXTENDED):
        inventory_path, matrix_path = write_inventory(adapter)
        print(f"wrote {inventory_path} and {matrix_path}")


if __name__ == "__main__":
    main()
