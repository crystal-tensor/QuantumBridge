# This file is independently implemented for QuantumBridge SDK.
# No source code from Qiskit or PennyLane was copied.
"""Qiskit Machine Learning optional adapter scaffold.

Design source: docs/compat/strategy/qiskit_machine_learning_compatibility_strategy.md.
"""

from quantumbridge.compat.qiskit_machine_learning.classifier_adapter import ADAPTER as classifier_adapter
from quantumbridge.compat.qiskit_machine_learning.dataset_adapter import ADAPTER as dataset_adapter
from quantumbridge.compat.qiskit_machine_learning.kernel_adapter import ADAPTER as kernel_adapter
from quantumbridge.compat.qiskit_machine_learning.qnn_adapter import ADAPTER as qnn_adapter
from quantumbridge.compat.qiskit_machine_learning.regressor_adapter import ADAPTER as regressor_adapter
from quantumbridge.compat.qiskit_machine_learning.torch_connector_adapter import ADAPTER as torch_connector_adapter
from quantumbridge.compat.qiskit_common import QiskitAdapterFacade

ADAPTER = QiskitAdapterFacade(
    ecosystem="qiskit_machine_learning",
    upstream_package="qiskit-machine-learning",
    dependency_extra="qiskit-machine-learning",
    adapters=(qnn_adapter, kernel_adapter, classifier_adapter, regressor_adapter, torch_connector_adapter, dataset_adapter),
    notes="Qiskit Machine Learning bridge; no production ML or training-correctness guarantee.",
)

capability_level = ADAPTER.capability_level
production_ready = ADAPTER.production_ready
native_implementation = ADAPTER.native_implementation
upstream_required = ADAPTER.upstream_required
dependency_available = ADAPTER.dependency_available
get_upstream_version = ADAPTER.get_upstream_version
get_dependency_report = ADAPTER.get_dependency_report
list_public_api_inventory = ADAPTER.list_public_api_inventory
get_public_object = ADAPTER.get_public_object
passthrough_call = ADAPTER.passthrough_call
passthrough_class = ADAPTER.passthrough_class
wrap_result = ADAPTER.wrap_result
to_quantumbridge_schema = ADAPTER.to_quantumbridge_schema
get_warnings = ADAPTER.get_warnings
get_provenance = ADAPTER.get_provenance
unsupported = ADAPTER.unsupported
validate_environment = ADAPTER.validate_environment

__all__ = [
    "ADAPTER",
    "capability_level",
    "classifier_adapter",
    "dataset_adapter",
    "dependency_available",
    "get_dependency_report",
    "get_provenance",
    "get_public_object",
    "get_upstream_version",
    "get_warnings",
    "kernel_adapter",
    "list_public_api_inventory",
    "native_implementation",
    "passthrough_call",
    "passthrough_class",
    "production_ready",
    "qnn_adapter",
    "regressor_adapter",
    "to_quantumbridge_schema",
    "torch_connector_adapter",
    "unsupported",
    "upstream_required",
    "validate_environment",
    "wrap_result",
]
