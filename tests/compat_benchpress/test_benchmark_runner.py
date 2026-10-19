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


def test_suite_skips_missing_optional_dependencies_without_masking_failures():
    optional_case = create_benchmark_case(
        "optional",
        "unit",
        runner=lambda: {"passed": True},
        metadata={"required_dependencies": ["quantumbridge_dependency_that_does_not_exist"]},
    )
    optional_suite = run_benchmark_suite([optional_case], suite_name="optional_suite")
    assert optional_suite.passed
    assert optional_suite.metrics == {
        "total": 1,
        "passed": 0,
        "failed": 0,
        "skipped": 1,
        "unsupported": 0,
    }

    failing_case = create_benchmark_case("required failure", "unit", runner=lambda: {"passed": False})
    failing_suite = run_benchmark_suite([failing_case], suite_name="required_suite")
    assert failing_suite.passed is False
    assert failing_suite.metrics["failed"] == 1
