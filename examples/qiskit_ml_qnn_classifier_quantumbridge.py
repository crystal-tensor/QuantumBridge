#!/usr/bin/env python3
# This file is independently implemented for QuantumBridge SDK.
# No source code from Qiskit Machine Learning was copied.
"""Run the QuantumBridge native educational QNN-classifier example."""

from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from quantumbridge.compat.qiskit_machine_learning import qnn_forward_native, run_qnn_classifier_example


def main() -> None:
    results = run_qnn_classifier_example()
    native = results["native"]
    upstream = results["upstream"]
    forward = qnn_forward_native([0.2, -0.1], native.weights)
    print("QuantumBridge native QML QNN classifier")
    print(native.to_json())
    print("predictions:", native.predictions)
    print("accuracy:", native.accuracy)
    print("forward:", forward.to_json())
    print("warnings:", native.warnings)
    print("provenance:", native.provenance)
    print("optional upstream qiskit-machine-learning QNN path")
    print(upstream.to_json())
    print("warnings:", upstream.warnings)
    print("provenance:", upstream.provenance)
    print("cloud_access:", native.metadata["cloud_access"])
    print("token_read:", native.metadata["token_read"])
    print("hardware_access:", native.metadata["hardware_access"])
    print("production_ml:", native.production_ready)


if __name__ == "__main__":
    main()
