# This file is independently implemented for QuantumBridge SDK.
# No source code from Qiskit or PennyLane was copied.

import json

import pytest

from quantumbridge.schema import (
    AerResult,
    AlgorithmsResult,
    ChemistryResult,
    DynamicsResult,
    ExperimentsResult,
    FinanceResult,
    MLResult,
    MetalDesignResult,
    OptimizationResult,
    PennyLaneResult,
)


@pytest.mark.parametrize(
    "result_class",
    [
        AerResult,
        AlgorithmsResult,
        ChemistryResult,
        DynamicsResult,
        ExperimentsResult,
        FinanceResult,
        MLResult,
        MetalDesignResult,
        OptimizationResult,
        PennyLaneResult,
    ],
)
def test_ecosystem_result_roundtrip(result_class):
    result = result_class(
        ecosystem="overridden-by-class",
        upstream_package="upstream",
        upstream_version="1.0",
        capability_level=2,
        mode="Adapter",
        raw_type="dict",
        data={"ok": True},
        metadata={"test": True},
        provenance={"source_policy": "optional_dependency_no_vendored_source"},
        warnings=[],
    )

    restored = result_class.from_dict(json.loads(result.to_json()))

    assert restored.validate()
    assert restored.to_dict() == result.to_dict()