from quantumbridge.compat.torchquantum.qml_dataset_native import make_torchquantum_like_toy_dataset
from quantumbridge.compat.torchquantum.training_native import (
    binary_cross_entropy_like_loss,
    grid_search_train_quantum_layer_native,
    mse_loss,
)


def test_training_native_returns_weights_trace_and_accuracy():
    X, y = make_torchquantum_like_toy_dataset()
    result = grid_search_train_quantum_layer_native(X, y)
    assert len(result.weights) == 4
    assert len(result.training_trace) > 0
    assert result.accuracy is not None
    assert result.accuracy >= 0.5
    assert result.loss is not None
    assert result.metadata["cloud_access"] is False


def test_losses_are_finite():
    assert mse_loss([0.1, 0.9], [0, 1]) < 0.02
    assert binary_cross_entropy_like_loss([0.1, 0.9], [0, 1]) > 0.0
