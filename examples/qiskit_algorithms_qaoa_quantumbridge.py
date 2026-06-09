# This file is independently implemented for QuantumBridge SDK.
# No source code from Qiskit Algorithms was copied.
"""Run the QuantumBridge Qiskit Algorithms QAOA executable adapter example."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from quantumbridge.compat.qiskit_algorithms import (
    run_qaoa_native_maxcut,
    run_qaoa_upstream,
    validate_algorithms_dependencies,
)


def main() -> None:
    edges = ((0, 1), (1, 2), (2, 0))
    native = run_qaoa_native_maxcut(edges, num_nodes=3, p=1)
    upstream = run_qaoa_upstream()
    print("QuantumBridge native QAOA-compatible MaxCut")
    print(native.to_json())
    print("Optional upstream QAOA")
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
