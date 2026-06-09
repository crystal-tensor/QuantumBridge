from qiskit_inventory_common import write_public_api_inventory
#!/usr/bin/env python3
# This file is independently implemented for QuantumBridge SDK.
# No source code from Qiskit or PennyLane was copied.
"""Generate Qiskit Experiments public-name inventory."""

from quantumbridge.compat.qiskit_experiments.calibration_adapter import ADAPTER as CALIBRATION
from quantumbridge.compat.qiskit_experiments.experiments_adapter import ADAPTER as EXPERIMENTS
from quantumbridge.compat.qiskit_experiments.rb_adapter import ADAPTER as RB
from quantumbridge.compat.qiskit_experiments.tomography_adapter import ADAPTER as TOMOGRAPHY
from quantumbridge.compat import qiskit_experiments as QISKIT_EXPERIMENTS
from quantumbridge.ecosystem.registry import write_inventory


def main() -> None:
    for adapter in (EXPERIMENTS, TOMOGRAPHY, RB, CALIBRATION):
        inventory_path, matrix_path = write_inventory(adapter)
        print(f"wrote {inventory_path} and {matrix_path}")
    inventory_path, matrix_path, summary = write_public_api_inventory(
        ecosystem="qiskit_experiments",
        facade=QISKIT_EXPERIMENTS.ADAPTER,
        adapters=(EXPERIMENTS, TOMOGRAPHY, RB, CALIBRATION),
    )
    print(f"wrote {inventory_path} and {matrix_path} ({summary['records']} records)")


if __name__ == "__main__":
    main()
