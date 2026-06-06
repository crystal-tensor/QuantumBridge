# This file is independently implemented for QuantumBridge SDK.
# No source code from Qiskit or PennyLane was copied.
"""Qiskit Experiments result schema adapter."""

import warnings

warnings.warn(
    "This adapter is a SCAFFOLD adapter. "
    "Full implementation is not yet available. "
    "This adapter only provides the Result schema wrapper. "
    "Level 0: inventory only; Level 1: passthrough; Level 2: schema wrapper. "
    "Not production experiments.",
    UserWarning,
    stacklevel=2
)

try:
    from quantumbridge.compat.qiskit_experiments.dependency import get_version
    upstream_version = get_version()
except ImportError:
    upstream_version = "unknown"


def wrap_experiment_result(obj, experiment_type: str = "generic", metadata=None):
    """Wrap a Qiskit Experiments result in QuantumBridge ExperimentsResult schema."""
    from quantumbridge.schema import ExperimentsResult
    return ExperimentsResult(
        ecosystem="qiskit",
        upstream_package="qiskit-experiments",
        upstream_version=upstream_version,
        capability_level=2,
        mode="scaffold",
        raw_type=experiment_type,
        data=obj,
        metadata=metadata or {},
        provenance={
            "upstream_package": "qiskit-experiments",
            "adapter": "result_adapter",
            "capability_level": 2,
        },
        warnings=[
            "This is a scaffold adapter. Advisory: not production backend/calibration/laboratory."
        ]
    )


# Alias for backward compatibility
wrap_experiments_result = wrap_experiment_result
