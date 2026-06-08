# This file is independently implemented for QuantumBridge SDK.
# No source code from Qiskit or PennyLane was copied.
"""Qiskit Dynamics result schema adapter."""

import warnings

warnings.warn(
    "This adapter is a SCAFFOLD adapter. "
    "Full implementation is not yet available. "
    "This adapter only provides the Result schema wrapper. "
    "Level 0: inventory only; Level 1: passthrough; Level 2: schema wrapper. "
    "Not production control-system.",
    UserWarning,
    stacklevel=2
)

try:
    from quantumbridge.compat.qiskit_dynamics.dependency import get_version
    upstream_version = get_version()
except ImportError:
    upstream_version = "unknown"


def wrap_dynamics_result(obj, metadata=None):
    """Wrap a Qiskit Dynamics result in QuantumBridge DynamicsResult schema."""
    from quantumbridge.schema import DynamicsResult
    return DynamicsResult(
        ecosystem="qiskit",
        upstream_package="qiskit-dynamics",
        upstream_version=upstream_version,
        capability_level=2,
        mode="scaffold",
        raw_type="dynamics",
        data=obj,
        metadata=metadata or {},
        provenance={
            "upstream_package": "qiskit-dynamics",
            "adapter": "result_adapter",
            "capability_level": 2,
        },
        warnings=[
            "This is a scaffold adapter. Advisory: not production control-system."
        ]
    )
