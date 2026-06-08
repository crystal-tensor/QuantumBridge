#!/usr/bin/env python3
# This file is independently implemented for QuantumBridge SDK.
# No source code from Qiskit or PennyLane was copied.
"""Generate Qiskit Machine Learning public-name inventory."""

from quantumbridge.compat.qiskit_machine_learning.classifier_adapter import ADAPTER as CLASSIFIER
from quantumbridge.compat.qiskit_machine_learning.dataset_adapter import ADAPTER as DATASET
from quantumbridge.compat.qiskit_machine_learning.kernel_adapter import ADAPTER as KERNEL
from quantumbridge.compat.qiskit_machine_learning.qnn_adapter import ADAPTER as QNN
from quantumbridge.compat.qiskit_machine_learning.regressor_adapter import ADAPTER as REGRESSOR
from quantumbridge.compat.qiskit_machine_learning.torch_connector_adapter import ADAPTER as TORCH_CONNECTOR
from quantumbridge.ecosystem.registry import write_inventory


def main() -> None:
    for adapter in (QNN, KERNEL, CLASSIFIER, REGRESSOR, TORCH_CONNECTOR, DATASET):
        inventory_path, matrix_path = write_inventory(adapter)
        print(f"wrote {inventory_path} and {matrix_path}")


if __name__ == "__main__":
    main()
