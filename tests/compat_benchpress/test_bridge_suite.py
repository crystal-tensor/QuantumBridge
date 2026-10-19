from quantumbridge.compat.benchpress import bridge_suite, run_benchmark_suite


def test_bridge_suite_runs():
    result = run_benchmark_suite(bridge_suite(), suite_name="bridge")
    assert result.passed
    assert result.metrics["failed"] == 0
    assert result.metrics["passed"] + result.metrics["skipped"] == len(bridge_suite())
