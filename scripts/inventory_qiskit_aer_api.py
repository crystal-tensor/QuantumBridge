#!/usr/bin/env python3
# This file is independently implemented for QuantumBridge SDK.
# No source code from Qiskit or PennyLane was copied.
"""Generate Qiskit Aer public-name inventory."""

from quantumbridge.compat.qiskit_aer.aer_adapter import ADAPTER as AER
from quantumbridge.compat.qiskit_aer.noise_adapter import ADAPTER as NOISE
from quantumbridge.ecosystem.registry import write_inventory


def main() -> None:
    for adapter in (AER, NOISE):
        inventory_path, matrix_path = write_inventory(adapter)
        print(f"wrote {inventory_path} and {matrix_path}")


if __name__ == "__main__":
    main()
