from quantumbridge.compat.qiskit_machine_learning import (
    make_toy_binary_classification_dataset,
    predict_qnn_classifier_native,
    run_qnn_classifier_native,
    score_qnn_classifier_native,
    split_toy_dataset,
    train_qnn_classifier_grid_search_native,
)


def test_qnn_classifier_grid_search_returns_weights_and_predictions():
    x_values, y_values = make_toy_binary_classification_dataset()
    x_train, x_test, y_train, y_test = split_toy_dataset(x_values, y_values, train_size=4)
    model = train_qnn_classifier_grid_search_native(x_train, y_train, weight_grid=(0.0, 1.57079632679))
    predictions = predict_qnn_classifier_native(model, x_test)
    accuracy = score_qnn_classifier_native(model, x_test, y_test)

    assert model.weights
    assert len(predictions) == len(y_test)
    assert 0.0 <= accuracy <= 1.0


def test_run_qnn_classifier_native_result():
    result = run_qnn_classifier_native()

    assert result.validate() is True
    assert result.weights
    assert result.predictions
    assert result.accuracy is not None
