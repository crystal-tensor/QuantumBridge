# This file is independently implemented for QuantumBridge SDK.
# No source code from Qiskit or PennyLane was copied.
"""Qiskit Machine Learning optional adapter scaffold.

Design source: docs/compat/strategy/qiskit_machine_learning_compatibility_strategy.md.
"""

from quantumbridge.compat.qiskit_machine_learning.classifier_adapter import ADAPTER as classifier_adapter
from quantumbridge.compat.qiskit_machine_learning.kernel_adapter import ADAPTER as kernel_adapter
from quantumbridge.compat.qiskit_machine_learning.qnn_adapter import ADAPTER as qnn_adapter
from quantumbridge.compat.qiskit_machine_learning.torch_connector_adapter import ADAPTER as torch_connector_adapter

__all__ = ["classifier_adapter", "kernel_adapter", "qnn_adapter", "torch_connector_adapter"]
