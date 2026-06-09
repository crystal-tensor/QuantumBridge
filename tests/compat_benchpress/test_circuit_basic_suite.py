from quantumbridge.compat.benchpress import circuit_basic_suite, run_benchmark_suite


def test_circuit_basic_suite_runs():
    result = run_benchmark_suite(circuit_basic_suite(), suite_name="circuit_basic")
    assert result.passed
    assert result.metrics["passed"] >= 3
