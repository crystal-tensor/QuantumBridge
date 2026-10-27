#!/usr/bin/env python3
# Copyright 2026 QuantumBridge Contributors. Licensed under Apache-2.0.
"""D3 public metadata/signature audit, no credential or service invocation."""

from __future__ import annotations

import hashlib
import importlib.metadata as metadata
import inspect
import json
from pathlib import Path
import socket
import sys
from types import SimpleNamespace
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from quantumbridge.compat.quafu import QuafuCloudBackend, QuarkStudioTransport  # noqa: E402
from quantumbridge.finance.client_contract import CAPABILITY_STATES, response_field_matrix, trace_count_labels  # noqa: E402
from quantumbridge.finance.execution import FinanceCloudSession  # noqa: E402
from quantumbridge.finance.hardware_diagnostics import FinanceDiagnosticSession, audit_task  # noqa: E402
from quantumbridge.finance.mapping_diagnostics import ordered_mapping  # noqa: E402
from run_finance_diagnostics import BASE, fingerprint_original, write_json  # noqa: E402


SOURCES = {
    "historical_quarkstudio": "https://quarkstudio.readthedocs.io/en/latest/usage/code/transpiler/",
    "quafusqc_guide": "https://quafu-sqc.readthedocs.io/en/latest/",
    "separate_quafu_sdk_0_2_2": "https://pypi.org/project/quafu-sdk/0.2.2/",
}


def installed_contract():
    # Inspect public objects only. Never instantiate Task or read its source.
    import quark
    from quark import Task

    live_module = Path(inspect.getfile(Task)).resolve()
    distributions = {}
    for name in ("quarkstudio", "quarkcircuit", "pyquafu", "quafu-sdk"):
        try:
            dist = metadata.distribution(name)
        except metadata.PackageNotFoundError:
            distributions[name] = {"installed": False}
            continue
        owners = [str(path) for path in dist.files or [] if Path(dist.locate_file(path)).resolve() == live_module]
        distributions[name] = {"installed": True, "version": dist.version, "lists_live_Task_module": owners}
    methods = {name: str(inspect.signature(getattr(Task, name))) for name in dir(Task)
               if not name.startswith("_") and callable(getattr(Task, name))}
    result = {"python_executable": sys.executable, "python_version": sys.version, "distributions": distributions,
              "namespace_candidates": metadata.packages_distributions().get("quark", []),
              "quark_module_path": quark.__file__, "Task_module": Task.__module__, "Task_module_path": str(live_module),
              "Task_signature": str(inspect.signature(Task)), "Task_public_method_signatures": methods,
              "Task_run_help_first_line": (inspect.getdoc(Task.run) or "").splitlines()[:1],
              "gateway_class": f"{QuafuCloudBackend.__module__}.{QuafuCloudBackend.__qualname__}",
              "gateway_signatures": {name: str(inspect.signature(getattr(QuafuCloudBackend, name))) for name in ("__init__", "submit", "run", "status")},
              "call_path": ["FinanceCloudSession._raw_job", "QuafuCloudBackend.submit", "QuarkStudioTransport.submit",
                            "quark.quafu.Task.run(task, repeat=shots//1024)", "QuafuCloudJob.refresh",
                            "QuarkStudioTransport.retrieve", "quark.quafu.Task.result(task_id)", "gateway _extract_counts", "finance explicit normalization"],
              "read_source": "project gateway only; upstream implementation/test files NOT read",
              "Task_instantiated": False, "Task_service_methods_called": [], "sources": SOURCES}
    return result, Task


def main(contract):
    dest = BASE / "diagnostics/d3"
    old = json.loads((BASE / "diagnostics/d2/d2_readonly_audit.json").read_text())
    watched = old["file_hashes"]
    before_finance = fingerprint_original()
    for name, digest in watched.items():
        if hashlib.sha256((ROOT / name).read_bytes()).hexdigest() != digest:
            raise ValueError("historical evidence changed since D2")
    original = FinanceCloudSession(SimpleNamespace(name="Dongling"), journal=BASE / "session.json")
    diagnostics = FinanceDiagnosticSession(SimpleNamespace(name="Dongling"), original_journal=original.journal,
                                           journal=BASE / "diagnostics/diagnostic_task_ledger.json")
    traces, fields = {}, {}
    hints = {"bit_order": "separate quafu-sdk documentation declares c0_rightmost; not a current response fact",
             "measurements": "separate API describes measurement records", "compiler": "separate API describes compiler metadata",
             "calibration_id": "separate API describes run calibration ID", "executed_qasm": "separate API describes executed source"}
    for session, folder in ((original, BASE), (diagnostics, BASE / "diagnostics")):
        for key, saved in session.data["jobs"].items():
            task_id = saved["job"]["job_id"]
            payload = json.loads((folder / "provider_metadata" / f"{task_id}.json").read_text())
            audit = audit_task(saved, payload)
            normalized = BASE / "normalized_counts" / f"{task_id}.json"
            normalized_counts = json.loads(normalized.read_text())["counts"] if normalized.exists() else None
            trace = trace_count_labels(payload, saved["artifact"]["num_qubits"], ordered_physical_mapping=ordered_mapping(audit),
                                       financial_counts=normalized_counts,
                                       decoder_order=original.data["bit_order"] if normalized_counts is not None else None)
            if payload["count"] != saved["raw_counts"]:
                raise ValueError("client response and ledger counts differ")
            trace.update(task_id=task_id, experiment=key, backend=saved["job"]["backend_name"],
                         source_sha256=saved["artifact"]["sha256"])
            traces[key] = trace
            fields[key] = response_field_matrix(payload, documentation=hints)
    if len(traces) != 13 or len({trace["task_id"] for trace in traces.values()}) != 13:
        raise ValueError("expected thirteen unique receipts")
    capabilities = {
        "read_existing_task": {"status": "VERIFIED_READ_ONLY", "evidence": "thirteen previously saved Task.result responses; no new API call in D3"},
        "result_metadata": {"status": "VERIFIED_READ_ONLY", "evidence": "actual response fields audited per receipt"},
        "raw_bit_order": {"status": "ABSENT", "evidence": "no bit_order declaration in any of thirteen responses; decoder assumption unverified"},
        "physical_measurement_mapping": {"status": "VERIFIED_READ_ONLY", "evidence": "native QASM/QLISP terminal measurement maps, not raw-count order"},
        "compiler_version": {"status": "ABSENT", "evidence": "no historical compiler version in receipts; package version is not compiler version"},
        "calibration_id": {"status": "ABSENT", "evidence": "no historical calibration ID in receipts"},
        "compile_only": {"status": "UNSUPPORTED", "scope": "current project adapter", "platform_status": "DOCUMENTED_UNVERIFIED",
                         "evidence": "no compile-only public Task method found; compile=False still belongs to run, not a no-task operation"},
        "physical_layout_selection": {"status": "DOCUMENTED_UNVERIFIED", "adapter_status": "UNSUPPORTED",
                                      "evidence": "historical options.target_qubits example is not an installed-adapter argument or server placement guarantee"},
        "dry_run": {"status": "UNSUPPORTED", "scope": "current project adapter", "platform_status": "DOCUMENTED_UNVERIFIED",
                    "evidence": "no documented zero-side-effect method verified; no trial call permitted"},
        "target_availability": {"status": "DOCUMENTED_UNVERIFIED", "evidence": "public Task.status/backend signatures exist; no current device/layout query in D3"},
        "compile_false_task_run": {"status": "REQUIRES_PAID_EXECUTION", "evidence": "execution pathway creates a task; may consume quota/cost, actual charge unmeasured"},
    }
    assert all(row["status"] in CAPABILITY_STATES for row in capabilities.values())
    write_json(dest / "installed_client_contract.json", contract)
    write_json(dest / "public_api_capability_matrix.json", capabilities)
    write_json(dest / "historical_response_field_matrix.json", fields)
    write_json(dest / "raw_label_provenance.json", traces)
    write_json(dest / "layout_pinning_capability.json", {"status": "DOCUMENTED_UNVERIFIED", "decision": "PHYSICAL_LAYOUT_PINNING_NOT_VERIFIED",
               "documented_parameter": "options.target_qubits", "adapter_accepts_parameter": False,
               "server_guarantee_observed": False, "target_backend": "Dongling", "sources": SOURCES})
    write_json(dest / "compile_only_capability.json", {"status": "UNSUPPORTED", "scope": "current project adapter",
               "platform_status": "DOCUMENTED_UNVERIFIED", "public_Task_methods": sorted(contract["Task_public_method_signatures"]),
               "trial_execution": False, "compile_false_means_free": False})
    write_json(dest / "next_experiment_approval_proposal.json", {"decision": "NO_NEW_SUBMISSION_RECOMMENDED", "execute": False,
               "additional_tasks_requested_now": 0, "remaining_budget": 7, "owner_approval_required_for_future_plan": True,
               "supplier_questions_not_sent": ["Dongling raw-count label serialization order and registers",
                   "whether Task.result transforms server labels", "historical compiled mapping semantics",
                   "fixed physical layout guarantee and whether it is ordered or set-only",
                   "pre-execution compile-only API with explicit zero-task/zero-charge guarantee", "historical calibration ID availability"],
               "conditional_minimal_plan": "only after layout/label contracts are verified, review the D2 two-pattern plan with actual QASM and owner approval"})
    if before_finance != fingerprint_original() or any(hashlib.sha256((ROOT / name).read_bytes()).hexdigest() != digest for name, digest in watched.items()):
        raise ValueError("D3 modified original or diagnostic evidence")
    write_json(dest / "d3_no_submit_audit.json", {"task_ids": [row["task_id"] for row in traces.values()], "file_hashes": watched,
               "total_tasks": 13, "new_submissions": 0, "remaining_tasks": 7, "all_unchanged": True,
               "socket_connections_disabled": True, "Task_run_disabled": True, "gateway_submit_disabled": True,
               "Task_instantiated": False, "credentials_read": False, "raw_bit_order": "UNKNOWN/AMBIGUOUS",
               "financial_acceptance": "INCONCLUSIVE", "decision": "NO_NEW_SUBMISSION_RECOMMENDED"})
    print(json.dumps({"audited_tasks": 13, "finance_transforms_reversed_and_reversible": sum(row["saved_normalized_counts"] is not None for row in traces.values()),
                      "client_provider": "quarkstudio", "version": contract["distributions"]["quarkstudio"]["version"],
                      "new_submissions": 0, "decision": "NO_NEW_SUBMISSION_RECOMMENDED"}))


if __name__ == "__main__":
    with patch.object(socket.socket, "connect", side_effect=RuntimeError("D3 forbids service connections")), \
            patch.object(socket.socket, "connect_ex", side_effect=RuntimeError("D3 forbids service connections")):
        contract, Task = installed_contract()
        with patch.object(Task, "run", side_effect=RuntimeError("D3 forbids Task.run")), \
                patch.object(QuafuCloudBackend, "submit", side_effect=RuntimeError("D3 forbids submission")), \
                patch.object(QuarkStudioTransport, "__init__", side_effect=RuntimeError("D3 forbids credentialed transport creation")):
            main(contract)
