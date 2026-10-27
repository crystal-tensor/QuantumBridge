#!/usr/bin/env python3
# Copyright 2026 QuantumBridge Contributors. Licensed under Apache-2.0.
"""Explicit bounded Quafu finance run. Credentials never appear in arguments."""

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

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--prompt-token", action="store_true")
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--execute", action="store_true", help="Submit within the owner's 20-task budget")
    mode.add_argument("--inspect-existing", action="store_true", help="Read original task metadata; never submits")
    parser.add_argument("--backend", default="Dongling")
    parser.add_argument("--timeout", type=float, default=300)
    args = parser.parse_args()
    token = getpass.getpass("Quafu credential (hidden input): ") if args.prompt_token else (
        os.environ.get("QUAFU_TOKEN") or os.environ.get("QUAFU_API_TOKEN"))
    if not token:
        print(json.dumps({"status": "NO_CREDENTIAL", "submitted_tasks": 0}))
        return 2
    sink = io.StringIO()
    try:
        from quantumbridge.compat.quafu import QuafuCloudBackend, QuarkStudioTransport
        from quantumbridge.finance import FinanceCloudSession, build_finance_cases
        from quantumbridge.finance.acceptance import analyze_case_evidence
        from quantumbridge.finance.execution import circuit_artifact

        with contextlib.redirect_stdout(sink), contextlib.redirect_stderr(sink):
            transport = QuarkStudioTransport(token=token)
            status = transport.status()
        if args.inspect_existing:
            from types import SimpleNamespace

            journal = ROOT / "output/finance-hardware/session.json"
            data = json.loads(journal.read_text(encoding="utf-8"))
            validated = FinanceCloudSession(SimpleNamespace(name=data["backend"]), journal=journal)
            folder = journal.parent / "provider_metadata"
            folder.mkdir(parents=True, exist_ok=True)
            allowed = {"count", "counts", "corrected", "chip", "circuit", "transpiled", "qlisp",
                       "tid", "error", "status", "created", "finished", "mapping", "layout", "options"}
            for key, saved in validated.data["jobs"].items():
                task_id = saved["job"]["job_id"]
                with contextlib.redirect_stdout(sink), contextlib.redirect_stderr(sink):
                    payload = transport.retrieve(task_id)
                safe = {field: value for field, value in payload.items() if field in allowed}
                encoded = json.dumps(safe, ensure_ascii=False, indent=2, default=str).replace(token, "[REDACTED]")
                destination = folder / f"{task_id}.json"
                if destination.exists() and json.loads(destination.read_text()) != json.loads(encoded):
                    raise ValueError("existing provider metadata changed; preserve evidence before investigation")
                if not destination.exists():
                    destination.write_text(encoded, encoding="utf-8")
                print(json.dumps({"experiment": key, "task_id": task_id, "provider_fields": sorted(payload),
                                  "counts_match_original": payload.get("count", payload.get("counts")) == saved.get("raw_counts"),
                                  "compiled_available": bool(payload.get("transpiled")),
                                  "provider_source_sha256": hashlib.sha256(str(payload.get("circuit", "")).encode()).hexdigest(),
                                  "new_tasks": 0}), flush=True)
            return 0
        if not args.execute:
            safe = json.dumps(status, ensure_ascii=False, default=str).replace(token, "[REDACTED]")
            safe = re.sub(r"[A-Za-z0-9/{}`.\[\]:_-]{65,}", "[REDACTED]", safe)
            print(json.dumps({"status": "AUTHENTICATED_READONLY", "queues": safe[:2000], "submitted_tasks": 0}, ensure_ascii=False))
            return 0
        cases = build_finance_cases()
        session = FinanceCloudSession(QuafuCloudBackend(args.backend, transport=transport),
                                      journal=ROOT / "output/finance-hardware/session.json")
        plan = {key: {name: circuit_artifact(circuit)["sha256"] for name, circuit in case.experiments.items()}
                for key, case in cases.items()}
        plan_path = session.journal.with_name("plan.json")
        plan_path.parent.mkdir(parents=True, exist_ok=True)
        if plan_path.exists() and json.loads(plan_path.read_text()) != plan:
            raise ValueError("frozen finance circuit plan changed")
        if not plan_path.exists():
            plan_path.write_text(json.dumps(plan, indent=2), encoding="utf-8")
        print(json.dumps({"preflight": session.preflight(list(cases.values())), "backend": args.backend}), flush=True)
        for key, case in cases.items():
            with contextlib.redirect_stdout(sink), contextlib.redirect_stderr(sink):
                results = session.run(case, timeout=args.timeout)
            evidence = {"case": key, "hardware_status": "completed", "hardware_results": results,
                        "hardware_analysis": case.analyze(results), "acceptance": analyze_case_evidence(case, results)}
            destination = ROOT / "output/jupyter-notebook/finance" / f"{key}_hardware_evidence.json"
            destination.parent.mkdir(parents=True, exist_ok=True)
            destination.write_text(json.dumps(evidence, ensure_ascii=False, indent=2, allow_nan=False), encoding="utf-8")
            print(json.dumps({"case": key, "task_ids": [r["task_id"] for r in results.values()],
                              "hardware_status": evidence["acceptance"]["hardware_status"]}), flush=True)
        return 0
    except Exception as exc:
        message = str(exc).replace(token, "[REDACTED]")
        message = re.sub(r"[A-Za-z0-9/{}`.\[\]:_-]{65,}", "[REDACTED]", message)
        print(json.dumps({"status": "STOPPED", "error_type": type(exc).__name__,
                          "message": message[:500], "automatic_resubmission": False}, ensure_ascii=False), flush=True)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
