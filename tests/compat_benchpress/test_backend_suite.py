from quantumbridge.compat.benchpress import backend_suite, run_benchmark_suite


def test_backend_suite_runs():
    result = run_benchmark_suite(backend_suite(), suite_name="backend")
    assert result.passed
    assert result.metrics["passed"] == len(backend_suite())
