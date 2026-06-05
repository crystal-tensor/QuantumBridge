#!/usr/bin/env python3
# This file is independently implemented for QuantumBridge SDK.
# No source code from Qiskit or PennyLane was copied.
"""Generate Qiskit Addons public-name inventory."""

from quantumbridge.compat.qiskit_addons.aqc_adapter import ADAPTER as AQC
from quantumbridge.compat.qiskit_addons.mpf_adapter import ADAPTER as MPF
from quantumbridge.compat.qiskit_addons.obp_adapter import ADAPTER as OBP
from quantumbridge.compat.qiskit_addons.sqd_adapter import ADAPTER as SQD
from quantumbridge.ecosystem.registry import write_inventory


def main() -> None:
    for adapter in (SQD, MPF, AQC, OBP):
        inventory_path, matrix_path = write_inventory(adapter)
        print(f"wrote {inventory_path} and {matrix_path}")


if __name__ == "__main__":
    main()
