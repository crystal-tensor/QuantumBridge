# This file is independently implemented for QuantumBridge SDK.
# No source code from Qiskit or PennyLane was copied.
"""PennyLane QNode inventory and passthrough scaffold.

Design source: docs/compat/strategy/pennylane_full_coverage_strategy.md.
"""

from quantumbridge.ecosystem.registry import EcosystemAdapter
from quantumbridge.compat.contracts import CapabilityLevel
from quantumbridge.compat.pennylane_full.result_adapter import wrap_qnode_result as _result_wrap_qnode_result
from quantumbridge.compat.pennylane_full.warnings import adapter_metadata

ADAPTER = EcosystemAdapter("pennylane", "pennylane", ("pennylane",), "pennylane-full", "pennylane_qnode")

dependency_available = ADAPTER.dependency_available
get_upstream_version = ADAPTER.get_upstream_version
list_public_api_inventory = ADAPTER.list_public_api_inventory
passthrough_class = ADAPTER.passthrough_class
passthrough_function = ADAPTER.passthrough_function
wrap_result = ADAPTER.wrap_result
to_quantumbridge_schema = ADAPTER.to_quantumbridge_schema
provenance_metadata = ADAPTER.provenance_metadata
warn_unsupported = ADAPTER.warn_unsupported


def describe_qnode(qnode) -> dict:
    return {
        "name": getattr(qnode, "__name__", type(qnode).__name__),
        "callable": callable(qnode),
        "device": repr(getattr(qnode, "device", None)),
        "metadata_only": True,
        **adapter_metadata(CapabilityLevel.SCHEMA_ADAPTER),
    }


def run_qnode_passthrough(qnode, *args, **kwargs):
    return _result_wrap_qnode_result(qnode(*args, **kwargs), metadata={"adapter": "qnode_adapter"})


def wrap_qnode_result(raw):
    return _result_wrap_qnode_result(raw, metadata={"adapter": "qnode_adapter"})
