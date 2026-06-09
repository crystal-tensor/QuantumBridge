# This file is independently implemented for QuantumBridge SDK.
# No source code from Qiskit or PennyLane was copied.
"""Qiskit Dynamics optional adapter coverage."""

from quantumbridge.compat.qiskit_dynamics.solver_adapter import ADAPTER as solver_adapter
from quantumbridge.compat.qiskit_dynamics.backend_adapter import ADAPTER as backend_adapter
from quantumbridge.compat.qiskit_dynamics.model_adapter import ADAPTER as model_adapter
from quantumbridge.compat.qiskit_dynamics.signal_adapter import ADAPTER as signal_adapter
from quantumbridge.compat.qiskit_common import QiskitAdapterFacade

ADAPTER = QiskitAdapterFacade(
    ecosystem="qiskit_dynamics",
    upstream_package="qiskit-dynamics",
    dependency_extra="qiskit-dynamics",
    adapters=(solver_adapter, model_adapter, signal_adapter, backend_adapter),
    advisory=True,
    notes="Qiskit Dynamics advisory bridge; no production dynamics simulation claim.",
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
    "backend_adapter",
    "capability_level",
    "dependency_available",
    "get_dependency_report",
    "get_provenance",
    "get_public_object",
    "get_upstream_version",
    "get_warnings",
    "list_public_api_inventory",
    "model_adapter",
    "native_implementation",
    "passthrough_call",
    "passthrough_class",
    "production_ready",
    "signal_adapter",
    "solver_adapter",
    "to_quantumbridge_schema",
    "unsupported",
    "upstream_required",
    "validate_environment",
    "wrap_result",
]
