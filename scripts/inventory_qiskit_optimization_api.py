#!/usr/bin/env python3
# This file is independently implemented for QuantumBridge SDK.
# No source code from Qiskit or PennyLane was copied.
"""Generate Qiskit Optimization public-name inventory."""

from quantumbridge.compat.qiskit_optimization.converter_adapter import ADAPTER as CONVERTER
from quantumbridge.compat.qiskit_optimization.optimizer_adapter import ADAPTER as OPTIMIZER
from quantumbridge.compat.qiskit_optimization.quadratic_program_adapter import ADAPTER as QUADRATIC_PROGRAM
from quantumbridge.ecosystem.registry import write_inventory


def main() -> None:
    for adapter in (QUADRATIC_PROGRAM, OPTIMIZER, CONVERTER):
        inventory_path, matrix_path = write_inventory(adapter)
        print(f"wrote {inventory_path} and {matrix_path}")


if __name__ == "__main__":
    main()
