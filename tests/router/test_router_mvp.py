from __future__ import annotations

import json

from quantumbridge.router import RouterSLA, route_workload, run_router_benchmark, run_router_demo
from quantumbridge.router.quafu_tasks import quafu_tasks_to_backend_states, summarize_quafu_tasks_response
from quantumbridge.router.workloads import bell_circuit, qaoa_small_circuit


def test_route_workload_returns_evidence_trace() -> None:
    decision = route_workload(qaoa_small_circuit(), sla=RouterSLA(min_fidelity=0.82, max_wait=900), workload_id="test-qaoa")
    payload = decision.to_dict()
    assert payload["selected_backend"]
    assert payload["pred_fidelity"] > 0
    assert payload["estimated_wait"] > 0
    assert payload["decision_trace"]
    assert payload["qos_metrics"]["estimator"]["scatter"]
    assert payload["provenance"]["cloud_access"] is False
    assert payload["provenance"]["token_access"] is False
    assert payload["provenance"]["hardware_access"] is False


def test_router_benchmark_hits_wait_reduction_target() -> None:
    report = run_router_benchmark(job_count=100, seed=7)
    payload = report.to_dict()
    assert payload["improvement"]["wait_reduction_vs_round_robin"] >= 0.20
    assert payload["improvement"]["success_target_met"] is True
    assert payload["router_summary"]["job_count"] == 100


def test_router_demo_writes_artifacts(tmp_path) -> None:
    payload = run_router_demo(output_dir=tmp_path, job_count=20, seed=3)
    written = {path.rsplit("/", 1)[-1] for path in payload["written_files"]}
    assert "index.html" in written
    assert "benchmark_report.json" in written
    assert "poc_report_template.md" in written
    report = json.loads((tmp_path / "benchmark_report.json").read_text(encoding="utf-8"))
    assert report["job_count"] == 20


def test_qasm_route_boundary() -> None:
    qasm = "OPENQASM 2.0; qreg q[2]; creg c[2]; h q[0]; cx q[0],q[1]; measure q -> c;"
    decision = route_workload(qasm, workload_id="qasm-bell")
    assert decision.workload_features["source_type"] == "qasm"
    assert decision.uqci_bundle["target"] == "qos_uqci"


def test_quafu_tasks_evidence_builds_queue_snapshot() -> None:
    payload = {
        "total": 5,
        "items": [
            {"taskId": "a", "taskName": "bell", "chipName": "Baihua", "status": "Pending", "submitTime": "2026-06-13-10-00-00"},
            {"taskId": "b", "taskName": "qaoa", "chipName": "Baihua", "status": "Submitted", "submitTime": "2026-06-13-10-02-00"},
            {"taskId": "c", "taskName": "ghz", "chipName": "Dongling", "status": "Finished", "submitTime": "2026-06-13-09-45-00"},
            {"taskId": "d", "taskName": "vqe", "chipName": "Yunmeng", "status": "Transpiled", "submitTime": "2026-06-13-10-05-00"},
            {"taskId": "e", "taskName": "bell", "chipName": "Yunmeng", "status": "Failed", "submitTime": "2026-06-13-09-20-00"},
        ],
    }
    evidence = summarize_quafu_tasks_response(payload).to_dict()
    assert evidence["rows_seen"] == 5
    assert evidence["total_reported"] == 5
    assert "multi_chip_task_history" in evidence["evidence_codes"]
    assert "active_queue_visible" in evidence["evidence_codes"]
    assert evidence["queue_imbalance_ratio"] >= 1
    backends = quafu_tasks_to_backend_states(payload)
    assert {backend.backend_id for backend in backends} == {"quafu_baihua", "quafu_dongling", "quafu_yunmeng"}
    decision = route_workload(bell_circuit(), backends=backends, sla=RouterSLA(allow_mock=False), workload_id="quafu-task-test")
    assert decision.selected_backend.startswith("quafu_")
