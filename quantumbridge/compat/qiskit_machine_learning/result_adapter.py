# This file is independently implemented for QuantumBridge SDK.
# No source code from Qiskit or PennyLane was copied.
"""Qiskit Machine Learning result schema adapter."""

import warnings

warnings.warn(
    "This adapter is a SCAFFOLD adapter. "
    "Full implementation is not yet available. "
    "This adapter only provides the Result schema wrapper. "
    "Level 0: inventory only; Level 1: passthrough; Level 2: schema wrapper. "
    "No native implementation or production parity is claimed.",
    UserWarning,
    stacklevel=2
)

try:
    from quantumbridge.compat.qiskit_machine_learning.dependency import get_version
    upstream_version = get_version()
except ImportError:
    upstream_version = "unknown"


def wrap_ml_result(obj, result_type: str = "generic", metadata=None):
    """Wrap a Qiskit ML result in QuantumBridge MLResult schema."""
    from quantumbridge.schema import MLResult
    return MLResult(
        ecosystem="qiskit",
        upstream_package="qiskit-machine-learning",
        upstream_version=upstream_version,
        capability_level=2,
        mode="scaffold",
        raw_type=result_type,
        data=obj,
        metadata=metadata or {},
        provenance={
            "upstream_package": "qiskit-machine-learning",
            "adapter": "result_adapter",
            "capability_level": 2,
        },
        warnings=[
            "This is a scaffold adapter. Advisory: not production ML."
        ]
    )
