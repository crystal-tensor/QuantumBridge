#!/usr/bin/env python3
# This file is independently implemented for QuantumBridge SDK.
# No source code from Qiskit or PennyLane was copied.
"""Generate Qiskit Metal public API inventories."""

from quantumbridge.compat.qiskit_metal.component_adapter import ADAPTER as COMPONENT
from quantumbridge.compat.qiskit_metal.design_adapter import ADAPTER as DESIGN
from quantumbridge.compat.qiskit_metal.renderer_adapter import ADAPTER as RENDERER
from quantumbridge.compat.qiskit_metal.simulation_adapter import ADAPTER as SIMULATION
from quantumbridge.ecosystem.registry import write_inventory


def main() -> None:
    for adapter in (DESIGN, COMPONENT, RENDERER, SIMULATION):
        inventory_path, matrix_path = write_inventory(adapter)
        print(f"wrote {inventory_path} and {matrix_path}")


if __name__ == "__main__":
    main()
