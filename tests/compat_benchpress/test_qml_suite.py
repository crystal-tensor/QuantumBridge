from quantumbridge.compat.benchpress import qml_suite, run_benchmark_suite


def test_qml_suite_runs():
    result = run_benchmark_suite(qml_suite(), suite_name="qml")
    assert result.passed
    assert result.metrics["passed"] == len(qml_suite())
