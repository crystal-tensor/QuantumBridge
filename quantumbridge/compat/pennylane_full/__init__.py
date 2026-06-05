# This file is independently implemented for QuantumBridge SDK.
# No source code from Qiskit or PennyLane was copied.
"""PennyLane full-ecosystem optional adapter scaffold.

Design source: docs/compat/strategy/pennylane_full_coverage_strategy.md.
"""

from quantumbridge.compat.pennylane_full.device_adapter import ADAPTER as device_adapter
from quantumbridge.compat.pennylane_full.gradients_adapter import ADAPTER as gradients_adapter
from quantumbridge.compat.pennylane_full.measurement_adapter import ADAPTER as measurement_adapter
from quantumbridge.compat.pennylane_full.operations_adapter import ADAPTER as operations_adapter
from quantumbridge.compat.pennylane_full.plugin_adapter import ADAPTER as plugin_adapter
from quantumbridge.compat.pennylane_full.qchem_adapter import ADAPTER as qchem_adapter
from quantumbridge.compat.pennylane_full.qnode_adapter import ADAPTER as qnode_adapter
from quantumbridge.compat.pennylane_full.resource_adapter import ADAPTER as resource_adapter
from quantumbridge.compat.pennylane_full.templates_adapter import ADAPTER as templates_adapter
from quantumbridge.compat.pennylane_full.transforms_adapter import ADAPTER as transforms_adapter

__all__ = [
    "device_adapter",
    "gradients_adapter",
    "measurement_adapter",
    "operations_adapter",
    "plugin_adapter",
    "qchem_adapter",
    "qnode_adapter",
    "resource_adapter",
    "templates_adapter",
    "transforms_adapter",
]
