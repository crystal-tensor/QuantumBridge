from qiskit_inventory_common import write_public_api_inventory
#!/usr/bin/env python3
# This file is independently implemented for QuantumBridge SDK.
# No source code from Qiskit or PennyLane was copied.
"""Generate Qiskit Dynamics public API inventories."""

from quantumbridge.compat.qiskit_dynamics.backend_adapter import ADAPTER as BACKEND
from quantumbridge.compat.qiskit_dynamics.model_adapter import ADAPTER as MODEL
from quantumbridge.compat.qiskit_dynamics.signal_adapter import ADAPTER as SIGNAL
from quantumbridge.compat.qiskit_dynamics.solver_adapter import ADAPTER as SOLVER
from quantumbridge.compat import qiskit_dynamics as QISKIT_DYNAMICS
from quantumbridge.ecosystem.registry import EcosystemAdapter, write_inventory

EXTENDED = EcosystemAdapter(
    "qiskit-dynamics",
    "qiskit-dynamics",
    ("qiskit_dynamics.perturbation", "qiskit_dynamics.array"),
    "qiskit-dynamics",
    "qiskit_dynamics_extended",
)


def main() -> None:
    for adapter in (SOLVER, MODEL, SIGNAL, BACKEND, EXTENDED):
        inventory_path, matrix_path = write_inventory(adapter)
        print(f"wrote {inventory_path} and {matrix_path}")
    inventory_path, matrix_path, summary = write_public_api_inventory(
        ecosystem="qiskit_dynamics",
        facade=QISKIT_DYNAMICS.ADAPTER,
        adapters=(SOLVER, MODEL, SIGNAL, BACKEND, EXTENDED),
    )
    print(f"wrote {inventory_path} and {matrix_path} ({summary['records']} records)")


if __name__ == "__main__":
    main()
