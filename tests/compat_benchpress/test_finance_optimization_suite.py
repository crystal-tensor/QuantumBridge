from quantumbridge.compat.benchpress import finance_optimization_suite, run_benchmark_suite


def test_finance_optimization_suite_runs():
    result = run_benchmark_suite(finance_optimization_suite(), suite_name="finance_optimization")
    assert result.passed
    assert result.metrics["passed"] == len(finance_optimization_suite())
