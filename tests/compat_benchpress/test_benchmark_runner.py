from quantumbridge.compat.benchpress import create_benchmark_case, run_benchmark_case, run_benchmark_suite


def test_benchmark_runner_executes_case_and_suite():
    case = create_benchmark_case(
        "smoke",
        "unit",
        runner=lambda seed=None: {"passed": True, "metrics": {"seed": seed}, "output_summary": {"ok": True}},
    )
    result = run_benchmark_case(case, seed=11)
    assert result.passed
    assert result.metrics["seed"] == 11
    suite = run_benchmark_suite([case], suite_name="unit_suite")
    assert suite.passed
    assert suite.metrics["total"] == 1
