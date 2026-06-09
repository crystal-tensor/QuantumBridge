# This file is independently implemented for QuantumBridge SDK.
# No source code from Qiskit or PennyLane was copied.
"""Qiskit Algorithms optional adapter coverage."""

from quantumbridge.compat.qiskit_algorithms.minimum_eigensolver_adapter import ADAPTER as minimum_eigensolver_adapter
from quantumbridge.compat.qiskit_algorithms.amplitude_adapter import ADAPTER as amplitude_adapter
from quantumbridge.compat.qiskit_algorithms.eigensolver_adapter import ADAPTER as eigensolver_adapter
from quantumbridge.compat.qiskit_algorithms.gradient_adapter import ADAPTER as gradient_adapter
from quantumbridge.compat.qiskit_algorithms.grover_adapter import ADAPTER as grover_adapter
from quantumbridge.compat.qiskit_algorithms.optimizer_adapter import ADAPTER as optimizer_adapter
from quantumbridge.compat.qiskit_common import QiskitAdapterFacade

ADAPTER = QiskitAdapterFacade(
    ecosystem="qiskit_algorithms",
    upstream_package="qiskit-algorithms",
    dependency_extra="qiskit-algorithms",
    adapters=(
        minimum_eigensolver_adapter,
        eigensolver_adapter,
        optimizer_adapter,
        gradient_adapter,
        amplitude_adapter,
        grover_adapter,
    ),
    notes="Qiskit Algorithms passthrough/schema bridge; no algorithm parity claim.",
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
    "amplitude_adapter",
    "capability_level",
    "dependency_available",
    "eigensolver_adapter",
    "get_dependency_report",
    "get_provenance",
    "get_public_object",
    "get_upstream_version",
    "get_warnings",
    "gradient_adapter",
    "grover_adapter",
    "list_public_api_inventory",
    "minimum_eigensolver_adapter",
    "native_implementation",
    "optimizer_adapter",
    "passthrough_call",
    "passthrough_class",
    "production_ready",
    "to_quantumbridge_schema",
    "unsupported",
    "upstream_required",
    "validate_environment",
    "wrap_result",
]
