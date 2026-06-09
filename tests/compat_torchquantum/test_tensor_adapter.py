import numpy as np

from quantumbridge.compat.torchquantum.tensor_adapter import (
    batch_iter,
    normalize_batch_features,
    to_numpy_array,
    to_tensor_like,
)


def test_tensor_adapter_supports_list_and_numpy():
    assert to_numpy_array([1.0, 2.0]).shape == (1, 2)
    array = to_numpy_array(np.asarray([[1.0, -2.0], [0.5, 0.25]]))
    assert array.shape == (2, 2)
    tensor_like = to_tensor_like(array)
    assert tensor_like.shape == (2, 2)
    assert tensor_like.backend == "numpy"
    normalized = normalize_batch_features([[2.0, -2.0]])
    assert normalized.tolist() == [[1.0, -1.0]]


def test_batch_iter_with_labels():
    batches = list(batch_iter([[1, 2], [3, 4], [5, 6]], [0, 1, 1], batch_size=2))
    assert len(batches) == 2
    assert batches[0][0].shape == (2, 2)
    assert batches[0][1].tolist() == [0, 1]
