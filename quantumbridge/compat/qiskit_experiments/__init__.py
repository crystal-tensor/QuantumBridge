# This file is independently implemented for QuantumBridge SDK.
# No source code from Qiskit or PennyLane was copied.
"""Qiskit Experiments optional adapter scaffold.

Design source: docs/compat/strategy/qiskit_ecosystem_coverage_strategy.md.
"""

from quantumbridge.compat.qiskit_experiments.calibration_adapter import ADAPTER as calibration_adapter
from quantumbridge.compat.qiskit_experiments.experiments_adapter import ADAPTER as experiments_adapter
from quantumbridge.compat.qiskit_experiments.rb_adapter import ADAPTER as rb_adapter
from quantumbridge.compat.qiskit_experiments.tomography_adapter import ADAPTER as tomography_adapter
from quantumbridge.compat.qiskit_common import QiskitAdapterFacade

ADAPTER = QiskitAdapterFacade(
    ecosystem="qiskit_experiments",
    upstream_package="qiskit-experiments",
    dependency_extra="qiskit-experiments",
    adapters=(experiments_adapter, tomography_adapter, rb_adapter, calibration_adapter),
    advisory=True,
    offline_only=True,
    notes="Qiskit Experiments advisory bridge; no real experiment execution or hardware calibration claim.",
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
    "calibration_adapter",
    "capability_level",
    "dependency_available",
    "experiments_adapter",
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
    "rb_adapter",
    "to_quantumbridge_schema",
    "tomography_adapter",
    "unsupported",
    "upstream_required",
    "validate_environment",
    "wrap_result",
]
