from qiskit_inventory_common import write_public_api_inventory
#!/usr/bin/env python3
# This file is independently implemented for QuantumBridge SDK.
# No source code from Qiskit or PennyLane was copied.
"""Generate Qiskit IBM Runtime public-name inventory."""

from quantumbridge.compat.qiskit_runtime.backend_adapter import ADAPTER as BACKEND
from quantumbridge.compat.qiskit_runtime.job_adapter import ADAPTER as JOB
from quantumbridge.compat.qiskit_runtime.runtime_adapter import ADAPTER as RUNTIME
from quantumbridge.compat import qiskit_runtime as QISKIT_RUNTIME
from quantumbridge.ecosystem.registry import write_inventory


def main() -> None:
    for adapter in (RUNTIME, BACKEND, JOB):
        inventory_path, matrix_path = write_inventory(adapter)
        print(f"wrote {inventory_path} and {matrix_path}")
    inventory_path, matrix_path, summary = write_public_api_inventory(
        ecosystem="qiskit_runtime",
        facade=QISKIT_RUNTIME.ADAPTER,
        adapters=(RUNTIME, BACKEND, JOB),
    )
    print(f"wrote {inventory_path} and {matrix_path} ({summary['records']} records)")


if __name__ == "__main__":
    main()
