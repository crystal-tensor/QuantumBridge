import numpy as np

from quantumbridge.compat.qiskit_machine_learning import (
    make_toy_binary_classification_dataset,
    make_xor_dataset,
    normalize_features_for_angles,
    split_toy_dataset,
)


def test_xor_dataset_is_deterministic():
    x_one, y_one = make_xor_dataset()
    x_two, y_two = make_xor_dataset()

    assert np.array_equal(x_one, x_two)
    assert np.array_equal(y_one, y_two)
    assert x_one.shape == (4, 2)
    assert set(y_one.tolist()) == {0, 1}


def test_binary_dataset_and_split():
    x_values, y_values = make_toy_binary_classification_dataset()
    x_train, x_test, y_train, y_test = split_toy_dataset(x_values, y_values, train_size=4)

    assert x_values.shape == (6, 2)
    assert len(x_train) == 4
    assert len(x_test) == 2
    assert len(y_train) + len(y_test) == len(y_values)


def test_normalize_features_for_angles():
    angles = normalize_features_for_angles([[1.0, -1.0]])

    assert angles.shape == (1, 2)
    assert np.all(np.abs(angles) <= np.pi)
