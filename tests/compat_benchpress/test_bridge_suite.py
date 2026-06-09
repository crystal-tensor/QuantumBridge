from quantumbridge.compat.benchpress import bridge_suite, run_benchmark_suite


def test_bridge_suite_runs():
    result = run_benchmark_suite(bridge_suite(), suite_name="bridge")
    assert result.passed
    assert result.metrics["passed"] == len(bridge_suite())
