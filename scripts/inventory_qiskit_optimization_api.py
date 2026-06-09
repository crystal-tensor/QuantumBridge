from qiskit_inventory_common import write_public_api_inventory
#!/usr/bin/env python3
# This file is independently implemented for QuantumBridge SDK.
# No source code from Qiskit or PennyLane was copied.
"""Generate Qiskit Optimization public-name inventory."""

from quantumbridge.compat.qiskit_optimization.converter_adapter import ADAPTER as CONVERTER
from quantumbridge.compat.qiskit_optimization.applications_adapter import ADAPTER as APPLICATIONS
from quantumbridge.compat.qiskit_optimization.optimizer_adapter import ADAPTER as OPTIMIZER
from quantumbridge.compat.qiskit_optimization.quadratic_program_adapter import ADAPTER as QUADRATIC_PROGRAM
from quantumbridge.compat import qiskit_optimization as QISKIT_OPTIMIZATION
from quantumbridge.ecosystem.registry import write_inventory


def main() -> None:
    for adapter in (QUADRATIC_PROGRAM, OPTIMIZER, CONVERTER, APPLICATIONS):
        inventory_path, matrix_path = write_inventory(adapter)
        print(f"wrote {inventory_path} and {matrix_path}")
    inventory_path, matrix_path, summary = write_public_api_inventory(
        ecosystem="qiskit_optimization",
        facade=QISKIT_OPTIMIZATION.ADAPTER,
        adapters=(QUADRATIC_PROGRAM, OPTIMIZER, CONVERTER, APPLICATIONS),
    )
    print(f"wrote {inventory_path} and {matrix_path} ({summary['records']} records)")


if __name__ == "__main__":
    main()
