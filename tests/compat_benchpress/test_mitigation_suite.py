from quantumbridge.compat.benchpress import mitigation_suite, run_benchmark_suite


def test_mitigation_suite_runs():
    result = run_benchmark_suite(mitigation_suite(), suite_name="mitigation")
    assert result.passed
    assert result.metrics["passed"] == len(mitigation_suite())
