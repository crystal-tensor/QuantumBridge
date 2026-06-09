from quantumbridge.studio.benchmark_service import get_benchmark_report, list_benchmark_suites, run_benchmark_suite


def test_benchmark_service_runs_basic_suite_and_reports():
    suites = list_benchmark_suites()
    assert "circuit_basic" in suites
    report = run_benchmark_suite("circuit_basic")
    assert report.suite_id == "circuit_basic"
    assert report.report_json
    assert "not official Benchpress output" in report.report_markdown
    assert get_benchmark_report("markdown", suite_id="circuit_basic")
