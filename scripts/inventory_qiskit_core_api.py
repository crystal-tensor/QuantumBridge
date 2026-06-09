#!/usr/bin/env python3
# This file is independently implemented for QuantumBridge SDK.
# No source code from Qiskit or PennyLane was copied.
"""Generate Qiskit core public-name inventory."""

from qiskit_inventory_common import write_public_api_inventory
from quantumbridge.compat.qiskit_core.circuit_adapter import ADAPTER as CIRCUIT
from quantumbridge.compat.qiskit_core.primitives_adapter import ADAPTER as PRIMITIVES
from quantumbridge.compat.qiskit_core.quantum_info_adapter import ADAPTER as QUANTUM_INFO
from quantumbridge.compat.qiskit_core.result_adapter import ADAPTER as RESULT
from quantumbridge.compat.qiskit_core.transpiler_adapter import ADAPTER as TRANSPILER
from quantumbridge.compat import qiskit_core as QISKIT_CORE
from quantumbridge.ecosystem.registry import EcosystemAdapter, write_inventory

CORE_EXTENDED = EcosystemAdapter(
    "qiskit",
    "qiskit",
    (
        "qiskit.providers",
        "qiskit.visualization",
        "qiskit.qasm2",
        "qiskit.qasm3",
        "qiskit.qpy",
        "qiskit.synthesis",
        "qiskit.converters",
        "qiskit.dagcircuit",
    ),
    "qiskit-core",
    "qiskit_core_extended",
)


def main() -> None:
    for adapter in (CIRCUIT, TRANSPILER, QUANTUM_INFO, PRIMITIVES, RESULT, CORE_EXTENDED):
        inventory_path, matrix_path = write_inventory(adapter)
        print(f"wrote {inventory_path} and {matrix_path}")
    inventory_path, matrix_path, summary = write_public_api_inventory(
        ecosystem="qiskit_core",
        facade=QISKIT_CORE.ADAPTER,
        adapters=(CIRCUIT, TRANSPILER, QUANTUM_INFO, PRIMITIVES, RESULT, CORE_EXTENDED),
    )
    print(f"wrote {inventory_path} and {matrix_path} ({summary['records']} records)")


if __name__ == "__main__":
    main()
