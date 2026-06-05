#!/usr/bin/env python3
# This file is independently implemented for QuantumBridge SDK.
# No source code from Qiskit or PennyLane was copied.
"""Generate Qiskit Experiments public-name inventory."""

from quantumbridge.compat.qiskit_experiments.calibration_adapter import ADAPTER as CALIBRATION
from quantumbridge.compat.qiskit_experiments.experiments_adapter import ADAPTER as EXPERIMENTS
from quantumbridge.compat.qiskit_experiments.tomography_adapter import ADAPTER as TOMOGRAPHY
from quantumbridge.ecosystem.registry import write_inventory


def main() -> None:
    for adapter in (EXPERIMENTS, TOMOGRAPHY, CALIBRATION):
        inventory_path, matrix_path = write_inventory(adapter)
        print(f"wrote {inventory_path} and {matrix_path}")


if __name__ == "__main__":
    main()
