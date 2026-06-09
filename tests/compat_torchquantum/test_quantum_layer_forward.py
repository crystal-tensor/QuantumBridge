from quantumbridge.compat.torchquantum.quantum_layer_native import (
    build_torchquantum_like_feature_encoder,
    quantum_layer_forward_native,
    quantum_layer_to_quantumbridge_ir,
)
from quantumbridge.schema.torchquantum_results import QuantumLayerResult


def test_quantum_layer_forward_actually_runs():
    result = quantum_layer_forward_native([0.25, -0.5], [0.0, 0.0, 0.0, 0.0], num_qubits=2)
    assert isinstance(result, QuantumLayerResult)
    assert result.num_qubits == 2
    assert len(result.forward_outputs) == 1
    assert 0.0 <= result.forward_outputs[0] <= 1.0
    assert set(result.probabilities[0])
    assert result.production_ready is False
    assert result.metadata["cloud_access"] is False


def test_quantum_layer_ir_metadata():
    encoder = build_torchquantum_like_feature_encoder(2, 2)
    circuit = quantum_layer_to_quantumbridge_ir([0.1, 0.2], [0.0, 0.0, 0.0, 0.0], 2)
    assert encoder["type"] == "deterministic_angle_encoder"
    assert circuit.metadata["torchquantum_like_layer"]["num_qubits"] == 2
