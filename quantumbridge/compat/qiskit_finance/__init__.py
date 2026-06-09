# This file is independently implemented for QuantumBridge SDK.
# No source code from Qiskit or PennyLane was copied.
"""Qiskit Finance optional adapter scaffold.

Design source: docs/compat/strategy/qiskit_finance_compatibility_strategy.md.
"""

from quantumbridge.compat.qiskit_finance.applications_adapter import ADAPTER as applications_adapter
from quantumbridge.compat.qiskit_finance.circuits_adapter import ADAPTER as circuits_adapter
from quantumbridge.compat.qiskit_finance.data_provider_adapter import ADAPTER as data_provider_adapter
from quantumbridge.compat.qiskit_finance.uncertainty_adapter import ADAPTER as uncertainty_adapter
from quantumbridge.compat.qiskit_common import QiskitAdapterFacade

ADAPTER = QiskitAdapterFacade(
    ecosystem="qiskit_finance",
    upstream_package="qiskit-finance",
    dependency_extra="qiskit-finance",
    adapters=(applications_adapter, circuits_adapter, data_provider_adapter, uncertainty_adapter),
    notes="Qiskit Finance inventory/schema bridge; no production finance, trading, or advice claim.",
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
    "circuits_adapter",
    "data_provider_adapter",
    "dependency_available",
    "get_dependency_report",
    "get_provenance",
    "get_public_object",
    "get_upstream_version",
    "get_warnings",
    "list_public_api_inventory",
    "native_implementation",
    "passthrough_call",
    "passthrough_class",
    "production_ready",
    "to_quantumbridge_schema",
    "uncertainty_adapter",
    "unsupported",
    "upstream_required",
    "validate_environment",
    "wrap_result",
]
