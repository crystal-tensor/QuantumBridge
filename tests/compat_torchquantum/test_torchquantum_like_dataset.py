from quantumbridge.compat.torchquantum.qml_dataset_native import (
    dataset_summary,
    make_torchquantum_like_toy_dataset,
)


def test_toy_dataset_is_deterministic_and_small():
    X, y = make_torchquantum_like_toy_dataset()
    assert X.shape == (6, 2)
    assert y.tolist() == [0, 0, 0, 1, 1, 1]
    summary = dataset_summary(X, y)
    assert summary["deterministic"] is True
    assert summary["real_user_data"] is False
    assert summary["high_risk_decision_use"] is False
