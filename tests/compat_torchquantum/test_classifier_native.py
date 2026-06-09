from quantumbridge.compat.torchquantum.qml_dataset_native import make_torchquantum_like_toy_dataset
from quantumbridge.compat.torchquantum.training_native import (
    predict_quantum_layer_classifier_native,
    run_torchquantum_like_classifier_native,
    score_quantum_layer_classifier_native,
)


def test_classifier_native_runs_predictions_and_score():
    result = run_torchquantum_like_classifier_native()
    assert len(result.predictions) == 6
    assert result.accuracy is not None
    assert result.accuracy >= 0.5
    assert result.metadata["high_risk_decision_use"] is False
    X, y = make_torchquantum_like_toy_dataset()
    model = result.metadata["model"]
    assert len(predict_quantum_layer_classifier_native(model, X)) == len(y)
    assert score_quantum_layer_classifier_native(model, X, y) == result.accuracy
