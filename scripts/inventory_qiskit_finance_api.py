#!/usr/bin/env python3
# This file is independently implemented for QuantumBridge SDK.
# No source code from Qiskit or PennyLane was copied.
"""Generate Qiskit Finance public-name inventory."""

from quantumbridge.compat.qiskit_finance.applications_adapter import ADAPTER as APPLICATIONS
from quantumbridge.compat.qiskit_finance.circuits_adapter import ADAPTER as CIRCUITS
from quantumbridge.compat.qiskit_finance.data_provider_adapter import ADAPTER as DATA_PROVIDER
from quantumbridge.compat.qiskit_finance.uncertainty_adapter import ADAPTER as UNCERTAINTY
from quantumbridge.ecosystem.registry import write_inventory


def main() -> None:
    for adapter in (APPLICATIONS, DATA_PROVIDER, CIRCUITS, UNCERTAINTY):
        inventory_path, matrix_path = write_inventory(adapter)
        print(f"wrote {inventory_path} and {matrix_path}")


if __name__ == "__main__":
    main()
