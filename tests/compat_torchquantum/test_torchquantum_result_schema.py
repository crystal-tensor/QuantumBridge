from quantumbridge.schema.torchquantum_results import (
    QuantumLayerResult,
    TorchQuantumCompatibilityResult,
)


def test_torchquantum_result_schema_roundtrip():
    result = QuantumLayerResult(
        workflow="unit",
        mode="native_minimal",
        capability_level=3,
        production_ready=False,
        num_qubits=2,
        feature_dim=2,
        weights=[0.0, 0.0, 0.0, 0.0],
        forward_outputs=[0.5],
        probabilities=[{"00": 0.5, "11": 0.5}],
        predictions=[1],
        warnings=["warning"],
        provenance={"source": "test"},
    )
    payload = result.to_dict()
    restored = TorchQuantumCompatibilityResult.from_dict(payload)
    assert restored.validate() is True
    assert restored.to_json()
    assert restored.production_ready is False
