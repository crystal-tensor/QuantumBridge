from quantumbridge.compat.qiskit_machine_learning import (
    make_toy_binary_classification_dataset,
    predict_kernel_classifier_native,
    run_kernel_classifier_native,
    score_kernel_classifier_native,
    split_toy_dataset,
    train_kernel_classifier_native,
)


def test_kernel_classifier_trains_predicts_and_scores():
    x_values, y_values = make_toy_binary_classification_dataset()
    x_train, x_test, y_train, y_test = split_toy_dataset(x_values, y_values, train_size=4)
    model = train_kernel_classifier_native(x_train, y_train)
    predictions = predict_kernel_classifier_native(model, x_test)
    accuracy = score_kernel_classifier_native(model, x_test, y_test)

    assert len(predictions) == len(y_test)
    assert 0.0 <= accuracy <= 1.0


def test_run_kernel_classifier_native_result():
    result = run_kernel_classifier_native()

    assert result.validate() is True
    assert result.predictions
    assert result.accuracy is not None
    assert result.metadata["cloud_access"] is False
