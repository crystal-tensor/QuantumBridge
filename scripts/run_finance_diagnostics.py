#!/usr/bin/env python3
# Copyright 2026 QuantumBridge Contributors. Licensed under Apache-2.0.
"""D1 audit plus four explicit diagnostics, sharing the original 20-task budget."""

from __future__ import annotations

import argparse
import contextlib
import getpass
import hashlib
import io
import json
import os
from pathlib import Path
import re
import sys
from types import SimpleNamespace

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from quantumbridge.finance.execution import FinanceCloudSession  # noqa: E402
from quantumbridge.finance.hardware_diagnostics import (  # noqa: E402
    FinanceDiagnosticSession, audit_task, diagnostic_circuits, zero_one_metrics,
)

BASE = ROOT / "output/finance-hardware"
DEST = BASE / "diagnostics"


def write_json(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(json.dumps(data, ensure_ascii=False, indent=2, allow_nan=False), encoding="utf-8")
    temporary.replace(path)


def fingerprint_original():
    files = [BASE / name for name in ("session.json", "plan.json", "task_ledger.json", "finance_metrics.json", "hardware_vs_ideal.json")]
    for name in ("raw_counts", "normalized_counts"):
        files.extend(sorted((BASE / name).glob("*.json")))
    files.extend(sorted((ROOT / "output/jupyter-notebook/finance").glob("*_hardware_evidence.json")))
    return {str(path.relative_to(ROOT)): hashlib.sha256(path.read_bytes()).hexdigest() for path in files}


def readonly_audit():
    session = FinanceCloudSession(SimpleNamespace(name="Dongling"), journal=BASE / "session.json")
    audits = {}
    for key, saved in session.data["jobs"].items():
        payload = json.loads((BASE / "provider_metadata" / f'{saved["job"]["job_id"]}.json').read_text())
        audits[key] = audit_task(saved, payload)
    write_json(DEST / "compiled_circuit_manifest.json", audits)
    write_json(DEST / "readonly_task_metadata.json", {key: audit["fields"] for key, audit in audits.items()})
    if len(audits) != 9 or any(audit["compiled_vs_submitted_tvd"] > 1e-8 or audit["qlisp_vs_compiled_tvd"] != 0
                               or not audit["qlisp_measurement_map_matches"] for audit in audits.values()):
        raise ValueError("original read-only audit not complete/equivalent; no diagnostic submission")
    return audits


def check_charging_notice(payload):
    if re.search(r"charge|payment|billing|purchase|收费|付费|充值", json.dumps(payload, ensure_ascii=False), re.I):
        raise RuntimeError("charging notice encountered; stop and ask owner")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--execute", action="store_true", help="Authorize only the four D1 probes in the existing total budget")
    parser.add_argument("--prompt-token", action="store_true")
    parser.add_argument("--timeout", type=float, default=300)
    args = parser.parse_args()
    token, sink = "", io.StringIO()
    original = fingerprint_original()
    try:
        audits = readonly_audit()
        print(json.dumps({"original_tasks_audited": len(audits), "max_compilation_tvd": max(
            audit["compiled_vs_submitted_tvd"] for audit in audits.values()), "new_tasks": 0}), flush=True)
        if not args.execute:
            return 0
        token = getpass.getpass("Quafu credential (hidden input): ") if args.prompt_token else os.environ.get("QUAFU_TOKEN", "")
        if not token:
            raise ValueError("credential required for explicit diagnostic execution")
        from quantumbridge.compat.quafu import QuafuCloudBackend, QuarkStudioTransport

        with contextlib.redirect_stdout(sink), contextlib.redirect_stderr(sink):
            transport = QuarkStudioTransport(token=token)
            status = transport.status()
        check_charging_notice(status)
        session = FinanceDiagnosticSession(QuafuCloudBackend("Dongling", transport=transport),
                                          original_journal=BASE / "session.json", journal=DEST / "diagnostic_task_ledger.json")
        metrics, probes = {}, {}
        for key, circuit in diagnostic_circuits().items():
            with contextlib.redirect_stdout(sink), contextlib.redirect_stderr(sink):
                saved = session.run_one(key, timeout=args.timeout)
                payload = transport.retrieve(saved["job"]["job_id"])
            check_charging_notice(payload)
            allowed = {"count", "counts", "corrected", "chip", "circuit", "transpiled", "qlisp", "tid", "error", "status", "created", "finished", "mapping", "layout", "options"}
            safe = {field: value for field, value in payload.items() if field in allowed}
            encoded = json.dumps(safe, ensure_ascii=False).replace(token, "[REDACTED]")
            write_json(DEST / "provider_metadata" / f'{saved["job"]["job_id"]}.json', json.loads(encoded))
            probes[key] = audit_task(saved, safe)
            if probes[key]["compiled_vs_submitted_tvd"] > 1e-8:
                raise ValueError("diagnostic compiler changed ideal prepared state; stop new tasks")
            metric = zero_one_metrics(saved["raw_counts"], circuit.num_qubits, int(key.endswith("one")))
            metric["task_id"] = saved["job"]["job_id"]
            metrics[key] = metric
            write_json(DEST / "zero_one_raw_counts" / f'{saved["job"]["job_id"]}.json', saved["raw_counts"])
            write_json(DEST / "zero_one_metrics.json", metrics)
            write_json(DEST / "diagnostic_compiled_manifest.json", probes)
            print(json.dumps({"probe": key, "task_id": metric["task_id"], "status": saved["job"]["status"],
                              "shots": metric["shots"], "success_probability": metric["success_probability"],
                              "physical_measurement_map": probes[key]["native_compiled"]["physical_measurement_map"],
                              "total_tasks": len(session.original.data["jobs"]) + len(session.data["jobs"])}), flush=True)
        write_json(DEST / "mapping_hypotheses.json", {
            "candidate_count_label_orders": ["identity", "reverse"], "zero_one_status": "AMBIGUOUS",
            "reason": "all-zero/all-one likelihoods are identical under every permutation; compiler maps do not declare raw counts string order",
            "original_calibration": "2-bit provisional q0-last only; not proof for arbitrary physical layouts",
            "automatic_one_hot_submission": False})
        write_json(DEST / "diagnosis_decisions.json", {
            "hardware_execution": "COMPLETED_4_DIAGNOSTICS", "financial_acceptance": "INCONCLUSIVE",
            "total_tasks": len(session.original.data["jobs"]) + len(session.data["jobs"]),
            "remaining_tasks": 20 - len(session.original.data["jobs"]) - len(session.data["jobs"]),
            "one_hot": "NOT_SUBMITTED; reserve budget pending review of actual maps and zero/one quality",
            "readout_mitigation": "NOT_APPLIED", "noise_cause": "NOT_IDENTIFIED",
            "original_artifacts_unchanged": fingerprint_original() == original})
        return 0
    except Exception as exc:
        message = str(exc).replace(token, "[REDACTED]") if token else str(exc)
        print(json.dumps({"status": "STOPPED", "error_type": type(exc).__name__, "message": message[:450],
                          "automatic_resubmission": False}), flush=True)
        return 1
    finally:
        unchanged = fingerprint_original() == original
        write_json(DEST / "original_evidence_integrity.json", {"before": original, "unchanged": unchanged})
        if not unchanged:
            raise RuntimeError("immutable original evidence changed during diagnostics")


if __name__ == "__main__":
    raise SystemExit(main())
