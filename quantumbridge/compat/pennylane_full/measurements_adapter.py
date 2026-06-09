# This file is independently implemented for QuantumBridge SDK.
# No source code from Qiskit or PennyLane was copied.
"""PennyLane measurement metadata adapter."""

from __future__ import annotations

from quantumbridge.compat.contracts import CapabilityLevel

from .measurement_adapter import ADAPTER
from .result_adapter import wrap_measurement_result as _wrap_measurement_result
from .warnings import adapter_metadata


MEASUREMENT_NAMES = ("expval", "probs", "sample", "counts", "state", "density_matrix")

dependency_available = ADAPTER.dependency_available
get_upstream_version = ADAPTER.get_upstream_version
list_public_api_inventory = ADAPTER.list_public_api_inventory


def list_measurements() -> list[str]:
    return list(MEASUREMENT_NAMES)


def describe_measurement(name: str) -> dict:
    supported = name in MEASUREMENT_NAMES
    return {
        "name": name,
        "supported": supported,
        "metadata_only": True,
        **adapter_metadata(CapabilityLevel.SCHEMA_ADAPTER if supported else CapabilityLevel.INVENTORY),
    }


def wrap_measurement_result(raw):
    return _wrap_measurement_result(raw, metadata={"adapter": "measurements_adapter"})
