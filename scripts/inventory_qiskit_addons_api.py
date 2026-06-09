from qiskit_inventory_common import write_public_api_inventory
#!/usr/bin/env python3
# This file is independently implemented for QuantumBridge SDK.
# No source code from Qiskit or PennyLane was copied.
"""Generate Qiskit Addons public-name inventory."""

from quantumbridge.compat.qiskit_addons.aqc_adapter import ADAPTER as AQC
from quantumbridge.compat.qiskit_addons.mpf_adapter import ADAPTER as MPF
from quantumbridge.compat.qiskit_addons.obp_adapter import ADAPTER as OBP
from quantumbridge.compat.qiskit_addons.sqd_adapter import ADAPTER as SQD
from quantumbridge.compat import qiskit_addons as QISKIT_ADDONS
from quantumbridge.ecosystem.registry import write_inventory


def main() -> None:
    for adapter in (SQD, MPF, AQC, OBP):
        inventory_path, matrix_path = write_inventory(adapter)
        print(f"wrote {inventory_path} and {matrix_path}")
    inventory_path, matrix_path, summary = write_public_api_inventory(
        ecosystem="qiskit_addons",
        facade=QISKIT_ADDONS.ADAPTER,
        adapters=(SQD, MPF, AQC, OBP),
    )
    print(f"wrote {inventory_path} and {matrix_path} ({summary['records']} records)")


if __name__ == "__main__":
    main()
