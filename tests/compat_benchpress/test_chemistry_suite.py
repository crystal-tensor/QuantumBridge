from quantumbridge.compat.benchpress import chemistry_suite, run_benchmark_suite


def test_chemistry_suite_runs():
    result = run_benchmark_suite(chemistry_suite(), suite_name="chemistry")
    assert result.passed
    assert result.metrics["passed"] == len(chemistry_suite())
