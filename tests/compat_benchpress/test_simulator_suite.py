from quantumbridge.compat.benchpress import run_benchmark_suite, simulator_suite


def test_simulator_suite_runs():
    result = run_benchmark_suite(simulator_suite(), suite_name="simulator")
    assert result.passed
    assert result.metrics["passed"] == len(simulator_suite())
