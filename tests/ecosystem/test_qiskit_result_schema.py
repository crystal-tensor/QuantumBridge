# This file is independently implemented for QuantumBridge SDK.
# No source code from Qiskit or IBM ecosystem packages was copied.

import json

from quantumbridge.schema.qiskit_results import (
    AddonsAdvisoryResult,
    AerResult,
    AlgorithmsResult,
    DynamicsResult,
    ExperimentsResult,
    FinanceResult,
    MachineLearningResult,
    MetalAdvisoryResult,
    NatureResult,
    OptimizationResult,
    QiskitConversionResult,
    QiskitCoreResult,
    RuntimeOfflineResult,
)


def _make(result_class, **kwargs):
    return result_class(
        upstream_package="qiskit-test",
        upstream_version="0.0",
        capability_level=2,
        mode="schema-adapter",
        raw_type="dict",
        data={"ok": True},
        metadata={"test": True},
        warnings=["This Qiskit ecosystem adapter is an optional passthrough/schema bridge, not a full native Qiskit replacement."],
        provenance={"official_endorsement": False, "cloud_access": False, "token_storage": False},
        **kwargs,
    )


def test_qiskit_result_schema_roundtrip():
    classes = [
        QiskitCoreResult,
        AerResult,
        NatureResult,
        AlgorithmsResult,
        FinanceResult,
        OptimizationResult,
        MachineLearningResult,
        DynamicsResult,
        ExperimentsResult,
        MetalAdvisoryResult,
        RuntimeOfflineResult,
        AddonsAdvisoryResult,
        QiskitConversionResult,
    ]
    for result_class in classes:
        result = _make(result_class, advisory=result_class in {DynamicsResult, ExperimentsResult, MetalAdvisoryResult, RuntimeOfflineResult, AddonsAdvisoryResult}, offline_only=result_class is RuntimeOfflineResult)
        payload = result.to_dict()
        restored = result_class.from_dict(payload)
        assert restored.validate() is True
        assert json.loads(restored.to_json())["schema_version"] == "0.1"
