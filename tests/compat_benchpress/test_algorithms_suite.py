from quantumbridge.compat.benchpress import algorithms_suite, run_benchmark_suite


def test_algorithms_suite_runs():
    result = run_benchmark_suite(algorithms_suite(), suite_name="algorithms")
    assert result.passed
    assert result.metrics["passed"] == len(algorithms_suite())
