# This file is independently implemented for QuantumBridge SDK.
# No source code from Qiskit or PennyLane was copied.
"""Qiskit Optimization optional adapter scaffold.

Design source: docs/compat/strategy/qiskit_optimization_compatibility_strategy.md.
"""

from quantumbridge.compat.qiskit_optimization.converter_adapter import ADAPTER as converter_adapter
from quantumbridge.compat.qiskit_optimization.applications_adapter import ADAPTER as applications_adapter
from quantumbridge.compat.qiskit_optimization.optimizer_adapter import ADAPTER as optimizer_adapter
from quantumbridge.compat.qiskit_optimization.quadratic_program_adapter import ADAPTER as quadratic_program_adapter
from quantumbridge.compat.qiskit_common import QiskitAdapterFacade

ADAPTER = QiskitAdapterFacade(
    ecosystem="qiskit_optimization",
    upstream_package="qiskit-optimization",
    dependency_extra="qiskit-optimization",
    adapters=(quadratic_program_adapter, optimizer_adapter, converter_adapter, applications_adapter),
    notes="Qiskit Optimization schema bridge; no production optimizer parity claim.",
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
    "applications_adapter",
    "capability_level",
    "converter_adapter",
    "dependency_available",
    "get_dependency_report",
    "get_provenance",
    "get_public_object",
    "get_upstream_version",
    "get_warnings",
    "list_public_api_inventory",
    "native_implementation",
    "optimizer_adapter",
    "passthrough_call",
    "passthrough_class",
    "production_ready",
    "quadratic_program_adapter",
    "to_quantumbridge_schema",
    "unsupported",
    "upstream_required",
    "validate_environment",
    "wrap_result",
]
