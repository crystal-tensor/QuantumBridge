from quantumbridge.compat.torchquantum.quantum_layer_native import batch_quantum_layer_forward_native


def test_batch_forward_actually_runs():
    result = batch_quantum_layer_forward_native(
        [[-1.0, -0.8], [0.8, 0.5]],
        [0.0, 0.0, 0.0, 0.0],
        num_qubits=2,
    )
    assert result.batch_size == 2
    assert len(result.forward_outputs) == 2
    assert len(result.predictions) == 2
    assert all(0.0 <= value <= 1.0 for value in result.forward_outputs)
