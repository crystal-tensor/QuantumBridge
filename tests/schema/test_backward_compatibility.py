from quantumbridge.results import Result


def test_result_from_p1_payload():
    restored = Result.from_dict({"counts": {"1": 3}, "probabilities": {"1": 1.0}, "expectation": 0.5, "metadata": {}})
    assert restored.counts() == {"1": 3}
    assert restored.expectation_value() == 0.5
