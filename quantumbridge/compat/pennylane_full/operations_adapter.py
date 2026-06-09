# This file is independently implemented for QuantumBridge SDK.
# No source code from Qiskit or PennyLane was copied.
"""PennyLane operations inventory and passthrough scaffold.

Design source: docs/compat/strategy/pennylane_full_coverage_strategy.md.
"""

from quantumbridge.ecosystem.registry import EcosystemAdapter
from quantumbridge.compat.contracts import CapabilityLevel
from quantumbridge.compat.pennylane_full.passthrough import get_public_object
from quantumbridge.compat.pennylane_full.warnings import adapter_metadata, unsupported

ADAPTER = EcosystemAdapter("pennylane", "pennylane", ("pennylane.ops",), "pennylane-full", "pennylane_operations")

BASIC_OPERATION_NAMES = (
    "H",
    "X",
    "Y",
    "Z",
    "RX",
    "RY",
    "RZ",
    "PhaseShift",
    "CNOT",
    "CZ",
    "SWAP",
    "Hadamard",
    "PauliX",
    "PauliY",
    "PauliZ",
)

_ALIASES = {
    "H": "Hadamard",
    "X": "PauliX",
    "Y": "PauliY",
    "Z": "PauliZ",
    "Phase": "PhaseShift",
}

dependency_available = ADAPTER.dependency_available
get_upstream_version = ADAPTER.get_upstream_version
list_public_api_inventory = ADAPTER.list_public_api_inventory
passthrough_class = ADAPTER.passthrough_class
passthrough_function = ADAPTER.passthrough_function
wrap_result = ADAPTER.wrap_result
to_quantumbridge_schema = ADAPTER.to_quantumbridge_schema
provenance_metadata = ADAPTER.provenance_metadata
warn_unsupported = ADAPTER.warn_unsupported


def list_operations() -> list[str]:
    return list(BASIC_OPERATION_NAMES)


def get_operation(name: str):
    return get_public_object("pennylane", _ALIASES.get(name, name))


def describe_operation(name: str) -> dict:
    normalized = _ALIASES.get(name, name)
    supported = normalized in {_ALIASES.get(item, item) for item in BASIC_OPERATION_NAMES}
    return {
        "name": name,
        "upstream_name": normalized,
        "supported": supported,
        "metadata_only": True,
        **adapter_metadata(CapabilityLevel.SCHEMA_ADAPTER if supported else CapabilityLevel.INVENTORY),
    }


def operation_to_metadata(obj) -> dict:
    return {
        "name": getattr(obj, "name", type(obj).__name__),
        "wires": [int(wire) for wire in getattr(obj, "wires", [])],
        "parameters": list(getattr(obj, "parameters", [])),
        "metadata_only": True,
        **adapter_metadata(CapabilityLevel.SCHEMA_ADAPTER),
    }


def operation_to_quantumbridge_ir_fragment(obj):
    name = getattr(obj, "name", type(obj).__name__)
    wires = [int(wire) for wire in getattr(obj, "wires", [])]
    params = list(getattr(obj, "parameters", []))
    mapping = {
        "Hadamard": "h",
        "PauliX": "x",
        "PauliY": "y",
        "PauliZ": "z",
        "RX": "rx",
        "RY": "ry",
        "RZ": "rz",
        "PhaseShift": "phase",
        "CNOT": "cx",
        "CZ": "cz",
        "SWAP": "swap",
    }
    if name not in mapping:
        return unsupported(f"PennyLane operation {name!r} is not in the Stage 8B basic gate subset.").to_dict()
    controls = wires[:1] if mapping[name] in {"cx", "cz"} else []
    targets = wires[1:] if controls else wires
    return {"op": mapping[name], "targets": targets, "controls": controls, "params": params}
