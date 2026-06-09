# This file is independently implemented for QuantumBridge SDK.
# No source code from Qiskit or PennyLane was copied.
"""Qiskit Nature optional adapter coverage."""

from quantumbridge.compat.qiskit_nature.nature_adapter import ADAPTER as nature_adapter
from quantumbridge.compat.qiskit_nature.driver_adapter import ADAPTER as driver_adapter
from quantumbridge.compat.qiskit_nature.openfermion_adapter import ADAPTER as openfermion_adapter
from quantumbridge.compat.qiskit_nature.problem_adapter import ADAPTER as problem_adapter
from quantumbridge.compat.qiskit_common import QiskitAdapterFacade

ADAPTER = QiskitAdapterFacade(
    ecosystem="qiskit_nature",
    upstream_package="qiskit-nature",
    dependency_extra="qiskit-nature",
    adapters=(nature_adapter, driver_adapter, problem_adapter, openfermion_adapter),
    notes="Qiskit Nature chemistry metadata bridge; no production chemistry or material band-gap claim.",
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
    "dependency_available",
    "driver_adapter",
    "get_dependency_report",
    "get_provenance",
    "get_public_object",
    "get_upstream_version",
    "get_warnings",
    "list_public_api_inventory",
    "native_implementation",
    "nature_adapter",
    "openfermion_adapter",
    "passthrough_call",
    "passthrough_class",
    "problem_adapter",
    "production_ready",
    "to_quantumbridge_schema",
    "unsupported",
    "upstream_required",
    "validate_environment",
    "wrap_result",
]
