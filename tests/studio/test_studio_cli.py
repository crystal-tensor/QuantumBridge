import json
import subprocess
import sys


def run_cli(*args: str) -> dict:
    completed = subprocess.run(
        [sys.executable, "-m", "quantumbridge.studio", *args],
        check=True,
        capture_output=True,
        text=True,
    )
    return json.loads(completed.stdout)


def test_studio_cli_list_workflows():
    payload = run_cli("list-workflows")

    assert payload["success"] is True
    assert payload["workflow_count"] >= 36
    assert any(item["workflow_id"] == "aer.statevector_native" for item in payload["workflows"])


def test_studio_cli_execute_workflow():
    payload = run_cli("execute", "--workflow", "aer.statevector_native")

    assert payload["success"] is True
    assert payload["execution"]["workflow_id"] == "aer.statevector_native"
    assert payload["execution"]["status"] == "succeeded"
    assert payload["execution"]["provenance"]["cloud_access"] is False


def test_studio_cli_benchmark_basic_alias():
    payload = run_cli("benchmark", "--suite", "basic")

    assert payload["success"] is True
    assert payload["benchmark"]["suite_id"] == "circuit_basic"
    assert payload["benchmark"]["report_json"]


def test_studio_cli_export_json():
    payload = run_cli("export", "--workflow", "aer.statevector_native", "--format", "json")

    assert payload["success"] is True
    assert payload["export"]["export_type"] == "json"
    assert "aer.statevector_native" in payload["export"]["content"]


def test_studio_cli_generate_seed(tmp_path):
    payload = run_cli("generate-seed", "--output-dir", str(tmp_path))

    assert payload["success"] is True
    assert any(path.endswith("sampleWorkflowDetails.json") for path in payload["written_files"])
    assert (tmp_path / "seedData.js").exists()
