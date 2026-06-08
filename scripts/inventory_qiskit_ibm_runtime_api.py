#!/usr/bin/env python3
# This file is independently implemented for QuantumBridge SDK.
# No source code from Qiskit or PennyLane was copied.
"""Generate Qiskit IBM Runtime public-name inventory."""

from quantumbridge.compat.qiskit_runtime.backend_adapter import ADAPTER as BACKEND
from quantumbridge.compat.qiskit_runtime.job_adapter import ADAPTER as JOB
from quantumbridge.compat.qiskit_runtime.runtime_adapter import ADAPTER as RUNTIME
from quantumbridge.ecosystem.registry import write_inventory


def main() -> None:
    for adapter in (RUNTIME, BACKEND, JOB):
        inventory_path, matrix_path = write_inventory(adapter)
        print(f"wrote {inventory_path} and {matrix_path}")


if __name__ == "__main__":
    main()
