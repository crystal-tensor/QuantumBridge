#!/usr/bin/env python3
# This file is independently implemented for QuantumBridge SDK.
# No source code from Qiskit Aer was copied.
"""Run the QuantumBridge native educational Aer noisy-counts example."""

from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from quantumbridge.compat.qiskit_aer.examples import run_noisy_counts_example


def main() -> None:
    results = run_noisy_counts_example(shots=128, seed=7)
    native = results["native"]
    upstream = results["upstream"]
    print("QuantumBridge native Aer-style noisy qasm counts")
    print(native.to_json())
    print("warnings:", native.warnings)
    print("provenance:", native.provenance)
    print("optional upstream qiskit-aer path")
    print(upstream.to_json())
    print("warnings:", upstream.warnings)
    print("provenance:", upstream.provenance)
    print("cloud_access:", native.metadata["cloud_access"])
    print("token_read:", native.metadata["token_read"])
    print("hardware_access:", native.metadata["hardware_access"])
    print("production_simulator:", native.production_ready)


if __name__ == "__main__":
    main()
