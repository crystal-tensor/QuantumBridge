from quantumbridge.results import Result


def test_result_json_roundtrip():
    result = Result(probabilities_data={"0": 1.0}, expectation_data=1.0)
    restored = Result.from_json(result.to_json())
    assert restored.probabilities() == {"0": 1.0}
    assert restored.expectation_value() == 1.0
