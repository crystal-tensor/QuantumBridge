# This file is independently implemented for QuantumBridge SDK.
# No source code, prose, UI, or branding from IBM, Qiskit, PennyLane, or third-party projects was copied.
"""Generate local JSON seed data for the QuantumBridge Studio frontend prototype."""

from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from quantumbridge.studio.api_models import to_json_safe
from quantumbridge.studio.benchmark_service import run_benchmark_suite_by_id
from quantumbridge.studio.catalog_service import get_project_status_summary, list_ecosystem_projects
from quantumbridge.studio.execution_service import execute_workflow
from quantumbridge.studio.export_service import (
    export_result_json,
    export_result_markdown,
    export_workflow_notebook_stub,
    export_workflow_python_snippet,
)
from quantumbridge.studio.workflow_inputs import get_default_inputs
from quantumbridge.studio.workflow_registry import get_workflow, list_workflows

OUT_DIR = Path("studio/src/data")


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    projects = [item.to_dict() for item in list_ecosystem_projects()]
    workflow_summaries = [item.to_dict() for item in list_workflows()]
    details = []
    for summary in workflow_summaries:
        workflow_id = summary["workflow_id"]
        detail = get_workflow(workflow_id).to_dict()
        detail["default_inputs"] = get_default_inputs(workflow_id)
        details.append(detail)

    sample_execution = execute_workflow("aer.qasm_counts_native", {"shots": 64, "seed": 5})
    finance_execution = execute_workflow("finance.portfolio_optimization_native", {})
    benchmark_report = run_benchmark_suite_by_id("circuit_basic")

    exports = {
        "json": export_result_json(sample_execution).to_dict(),
        "markdown": export_result_markdown(sample_execution).to_dict(),
        "python": export_workflow_python_snippet("aer.qasm_counts_native", {"shots": 64, "seed": 5}).to_dict(),
        "notebook_stub": export_workflow_notebook_stub("aer.qasm_counts_native", {"shots": 64, "seed": 5}).to_dict(),
    }

    catalog_payload = {"projects": projects, "summary": get_project_status_summary(), "notices": _notices()}
    workflows_payload = {"workflows": workflow_summaries, "details": details, "notices": _notices()}
    results_payload = {
        "results": [sample_execution.to_dict(), finance_execution.to_dict()],
        "exports": exports,
        "notices": _notices(),
    }
    benchmark_payload = {"benchmark": benchmark_report.to_dict(), "notices": _notices()}

    write_json("sampleCatalog.json", catalog_payload)
    write_json("sampleWorkflows.json", workflows_payload)
    write_json("sampleResults.json", results_payload)
    write_json("sampleBenchmarkReport.json", benchmark_payload)
    write_js_seed(catalog_payload, workflows_payload, results_payload, benchmark_payload)


def write_json(name: str, payload: dict) -> None:
    path = OUT_DIR / name
    path.write_text(json.dumps(to_json_safe(payload), indent=2, sort_keys=True) + "\n", encoding="utf-8")


def write_js_seed(catalog: dict, workflows: dict, results: dict, benchmark: dict) -> None:
    payload = {
        "sampleCatalog": to_json_safe(catalog),
        "sampleWorkflows": to_json_safe(workflows),
        "sampleResults": to_json_safe(results),
        "sampleBenchmarkReport": to_json_safe(benchmark),
    }
    lines = [
        "// This file is generated from QuantumBridge-owned Stage 10C backend API outputs.",
        "// It contains local prototype seed data only: no secrets, credentials, cloud calls, or hardware access.",
    ]
    for name, value in payload.items():
        lines.append(f"export const {name} = {json.dumps(value, indent=2, sort_keys=True)};")
    (OUT_DIR / "seedData.js").write_text("\n\n".join(lines) + "\n", encoding="utf-8")


def _notices() -> list[str]:
    return [
        "QuantumBridge Studio is an independent local prototype.",
        "No official endorsement is claimed.",
        "Local-only: no cloud execution, credential reading, or hardware access.",
        "Third-party package names are used only for compatibility identification.",
        "This prototype is not production-ready.",
    ]


if __name__ == "__main__":
    main()
