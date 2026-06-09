# This file is independently implemented for QuantumBridge SDK.
# No source code from Qiskit Algorithms was copied.
"""Run the QuantumBridge Qiskit Algorithms Grover executable adapter example."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from quantumbridge.compat.qiskit_algorithms import (
    run_grover_native,
    run_grover_upstream,
    validate_algorithms_dependencies,
)


def main() -> None:
    native = run_grover_native(["11"], num_qubits=2)
    upstream = run_grover_upstream()
    print("QuantumBridge native Grover")
    print(native.to_json())
    print("Optional upstream Grover")
    print(upstream.to_json())
    print("Dependency report")
    print(validate_algorithms_dependencies())
    print("Warnings")
    for warning in native.warnings + upstream.warnings:
        print(f"- {warning}")
    print("Provenance")
    print(native.provenance)
    print(upstream.provenance)


if __name__ == "__main__":
    main()
