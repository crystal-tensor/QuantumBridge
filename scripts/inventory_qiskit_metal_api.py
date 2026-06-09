from qiskit_inventory_common import write_public_api_inventory
#!/usr/bin/env python3
# This file is independently implemented for QuantumBridge SDK.
# No source code from Qiskit or PennyLane was copied.
"""Generate Qiskit Metal public API inventories."""

from quantumbridge.compat.qiskit_metal.component_adapter import ADAPTER as COMPONENT
from quantumbridge.compat.qiskit_metal.design_adapter import ADAPTER as DESIGN
from quantumbridge.compat.qiskit_metal.renderer_adapter import ADAPTER as RENDERER
from quantumbridge.compat.qiskit_metal.simulation_adapter import ADAPTER as SIMULATION
from quantumbridge.compat import qiskit_metal as QISKIT_METAL
from quantumbridge.ecosystem.registry import write_inventory


def main() -> None:
    for adapter in (DESIGN, COMPONENT, RENDERER, SIMULATION):
        inventory_path, matrix_path = write_inventory(adapter)
        print(f"wrote {inventory_path} and {matrix_path}")
    inventory_path, matrix_path, summary = write_public_api_inventory(
        ecosystem="qiskit_metal",
        facade=QISKIT_METAL.ADAPTER,
        adapters=(DESIGN, COMPONENT, RENDERER, SIMULATION),
    )
    print(f"wrote {inventory_path} and {matrix_path} ({summary['records']} records)")


if __name__ == "__main__":
    main()
