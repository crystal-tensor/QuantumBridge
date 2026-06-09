#!/usr/bin/env python3
# This file is independently implemented for QuantumBridge SDK.
# No source code from Qiskit or PennyLane was copied.
"""Generate Qiskit Aer public-name inventory."""

from qiskit_inventory_common import write_public_api_inventory
from quantumbridge.compat.qiskit_aer.aer_adapter import ADAPTER as AER
from quantumbridge.compat.qiskit_aer.noise_adapter import ADAPTER as NOISE
from quantumbridge.compat import qiskit_aer as QISKIT_AER
from quantumbridge.ecosystem.registry import write_inventory


def main() -> None:
    for adapter in (AER, NOISE):
        inventory_path, matrix_path = write_inventory(adapter)
        print(f"wrote {inventory_path} and {matrix_path}")
    inventory_path, matrix_path, summary = write_public_api_inventory(
        ecosystem="qiskit_aer",
        facade=QISKIT_AER.ADAPTER,
        adapters=(AER, NOISE),
    )
    print(f"wrote {inventory_path} and {matrix_path} ({summary['records']} records)")


if __name__ == "__main__":
    main()
