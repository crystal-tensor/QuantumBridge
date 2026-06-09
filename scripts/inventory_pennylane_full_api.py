#!/usr/bin/env python3
# This file is independently implemented for QuantumBridge SDK.
# No source code from Qiskit or PennyLane was copied.
"""Generate PennyLane full-ecosystem public-name inventory."""

from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from quantumbridge.compat.pennylane_full.device_adapter import ADAPTER as DEVICE
from quantumbridge.compat.pennylane_full.gradients_adapter import ADAPTER as GRADIENTS
from quantumbridge.compat.pennylane_full.measurement_adapter import ADAPTER as MEASUREMENT
from quantumbridge.compat.pennylane_full.operations_adapter import ADAPTER as OPERATIONS
from quantumbridge.compat.pennylane_full.plugin_adapter import ADAPTER as PLUGIN
from quantumbridge.compat.pennylane_full.qchem_adapter import ADAPTER as QCHEM
from quantumbridge.compat.pennylane_full.qnode_adapter import ADAPTER as QNODE
from quantumbridge.compat.pennylane_full.resource_adapter import ADAPTER as RESOURCE
from quantumbridge.compat.pennylane_full.templates_adapter import ADAPTER as TEMPLATES
from quantumbridge.compat.pennylane_full.transforms_adapter import ADAPTER as TRANSFORMS
from quantumbridge.compat.pennylane_full.inventory import write_full_inventory
from quantumbridge.ecosystem.registry import write_inventory


def main() -> None:
    full_inventory_path, full_matrix_path, records = write_full_inventory()
    print(f"wrote {full_inventory_path} and {full_matrix_path} ({len(records)} records)")
    for adapter in (
        OPERATIONS,
        MEASUREMENT,
        QNODE,
        DEVICE,
        QCHEM,
        TRANSFORMS,
        GRADIENTS,
        TEMPLATES,
        RESOURCE,
        PLUGIN,
    ):
        inventory_path, matrix_path = write_inventory(adapter)
        print(f"wrote {inventory_path} and {matrix_path}")


if __name__ == "__main__":
    main()
