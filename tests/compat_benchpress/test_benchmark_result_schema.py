from pathlib import Path

from quantumbridge.compat.benchpress import create_benchmark_case, run_benchmark_case
from quantumbridge.compat.benchpress.reporting import (
    write_benchmark_report_json,
    write_benchmark_report_markdown,
)
from quantumbridge.schema.benchmark_results import BenchmarkCaseResult


def test_benchmark_result_schema_and_reports(tmp_path: Path):
    case = create_benchmark_case("schema", "unit", runner=lambda: {"passed": True})
    result = run_benchmark_case(case)
    payload = result.to_dict()
    restored = BenchmarkCaseResult.from_dict(payload)
    assert restored.validate()
    assert restored.to_json()
    json_path = write_benchmark_report_json(restored, tmp_path / "report.json")
    md_path = write_benchmark_report_markdown(restored, tmp_path / "report.md")
    assert json_path.read_text(encoding="utf-8")
    assert "not official Benchpress" in md_path.read_text(encoding="utf-8")
