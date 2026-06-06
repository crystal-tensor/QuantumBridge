#!/usr/bin/env python3
# This file is independently implemented for QuantumBridge SDK.
# No source code from Qiskit or PennyLane was copied.
"""Generate Qiskit Nature and OpenFermion public API inventories."""

from quantumbridge.compat.qiskit_nature.driver_adapter import ADAPTER as DRIVERS
from quantumbridge.compat.qiskit_nature.nature_adapter import ADAPTER as NATURE
from quantumbridge.compat.qiskit_nature.openfermion_adapter import ADAPTER as OPENFERMION
from quantumbridge.compat.qiskit_nature.problem_adapter import ADAPTER as PROBLEMS
from quantumbridge.ecosystem.registry import write_inventory


def main() -> None:
    for adapter in (NATURE, DRIVERS, PROBLEMS, OPENFERMION):
        inventory_path, matrix_path = write_inventory(adapter)
        print(f"wrote {inventory_path} and {matrix_path}")


if __name__ == "__main__":
    main()
