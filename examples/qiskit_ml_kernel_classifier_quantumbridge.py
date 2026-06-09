#!/usr/bin/env python3
# This file is independently implemented for QuantumBridge SDK.
# No source code from Qiskit Machine Learning was copied.
"""Run the QuantumBridge native educational kernel-classifier example."""

from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from quantumbridge.compat.qiskit_machine_learning import run_kernel_classifier_example


def main() -> None:
    results = run_kernel_classifier_example()
    native = results["native"]
    upstream = results["upstream"]
    print("QuantumBridge native QML kernel classifier")
    print(native.to_json())
    print("predictions:", native.predictions)
    print("accuracy:", native.accuracy)
    print("warnings:", native.warnings)
    print("provenance:", native.provenance)
    print("optional upstream qiskit-machine-learning classifier path")
    print(upstream.to_json())
    print("warnings:", upstream.warnings)
    print("provenance:", upstream.provenance)
    print("cloud_access:", native.metadata["cloud_access"])
    print("token_read:", native.metadata["token_read"])
    print("hardware_access:", native.metadata["hardware_access"])
    print("production_ml:", native.production_ready)


if __name__ == "__main__":
    main()
