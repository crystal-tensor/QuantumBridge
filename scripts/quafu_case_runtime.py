#!/usr/bin/env python3
# Copyright 2026 QuantumBridge Contributors. Apache-2.0.
"""Opt-in quafu-sdk case execution. Importing this file does not read credentials.

This stdlib-only runner is also published beside the case manifest. SDK source,
credentials, raw account responses and installation directories are not exported.
"""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
import importlib.metadata
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile


SDK_VERSION = "0.2.7"


def now():
    return datetime.now(timezone.utc).isoformat()


def digest(value):
    return hashlib.sha256(json.dumps(value, ensure_ascii=False, sort_keys=True,
                                    separators=(",", ":"), allow_nan=False).encode()).hexdigest()


def save(path, value):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile(mode="w", encoding="utf-8", dir=path.parent,
                                     delete=False) as handle:
        json.dump(value, handle, ensure_ascii=False, indent=2, allow_nan=False)
        handle.write("\n")
        handle.flush()
        os.fsync(handle.fileno())
        temporary = handle.name
    os.replace(temporary, path)


def save_journal(path, journal):
    journal["integrity_sha256"] = digest({k: v for k, v in journal.items() if k != "integrity_sha256"})
    save(path, journal)


def sdk_identity():
    import quafu
    distribution = importlib.metadata.distribution("quafu-sdk")
    if distribution.version != SDK_VERSION or quafu.__version__ != SDK_VERSION:
        raise ValueError("Review and freeze the installed quafu-sdk version before execution")
    entry = Path(quafu.__file__).resolve()
    owned = {Path(distribution.locate_file(f)).resolve() for f in distribution.files or []}
    if entry not in owned:
        raise ValueError("The imported quafu module is not owned by quafu-sdk")
    return {"distribution": distribution.metadata["Name"], "version": distribution.version,
            "entry_sha256": hashlib.sha256(entry.read_bytes()).hexdigest(),
            "python": sys.version.split()[0]}


def inspect_public(client):
    devices = client.devices()
    metadata = client.metadata("Baihua")
    device = client.device("Baihua")
    calibration = device.calibration()
    # Public device/calibration data only. Do not export a Client or account data.
    return {"observed_at": now(), "sdk": sdk_identity(), "devices": devices,
            "target": "Baihua", "metadata": metadata,
            "calibration": {"id": device.calibration_id,
                            "calibrated_at": calibration.calibrated_at,
                            "basis_gates": calibration.basis_gates},
            "authenticated": False, "new_cloud_tasks": 0}


def validate_kernel(kernel, limits, *, shots=1024, max_qubits=6):
    if not limits:
        raise ValueError("Missing live backend limits; refuse submission")
    width = kernel["num_qubits"]
    if type(width) is not int or not 1 <= width <= max_qubits:
        raise ValueError("Owner qubit budget exceeded")
    if type(shots) is not int or not limits["min_shots"] <= shots <= limits["max_shots"]:
        raise ValueError("shots outside live backend limits")
    if shots % limits["shots_step"]:
        raise ValueError("shots does not match live backend step")
    if width > limits["max_qubits"]:
        raise ValueError("Backend qubit limit exceeded")
    if hashlib.sha256(kernel["openqasm"].encode()).hexdigest() != kernel["qasm_sha256"]:
        raise ValueError("Circuit hash mismatch")
    depth_limit = limits.get("max_depth")
    if depth_limit is not None and kernel["logical_depth"] > depth_limit:
        raise ValueError("Logical circuit depth exceeds backend limit")
    return {"logical_preflight": "passed", "physical_compilation": "pending_provider",
            "compiler_requested": "qiskit", "limits_sha256": digest(limits)}


def normalize_result(result, kernel, job_id, target, shots, sdk):
    """Preserve provider c0-rightmost counts and separately decode logical q0 first."""
    width = kernel["num_qubits"]
    counts = result.counts
    if not result.ok or result.status != "Finished" or not isinstance(counts, dict) or not counts:
        raise ValueError("Task has no successful raw counts")
    if result.bit_order != "c0_rightmost" or result.n_clbits != width:
        raise ValueError("Unreviewed bit-order or register-width contract")
    for label, value in counts.items():
        if (not isinstance(label, str) or len(label) != width or set(label) - {"0", "1"}
                or type(value) is not int or value < 0):
            raise ValueError("Invalid provider counts")
    returned = sum(counts.values())
    if returned <= 0 or returned != result.shots_returned or result.shots_requested != shots:
        raise ValueError("shots receipt does not reconcile")
    mapping = result.measurements
    if not isinstance(mapping, list) or len(mapping) != width:
        raise ValueError("Missing complete provider measurement mapping")
    by_cbit = {row["cbit"]: row for row in mapping}
    if (set(by_cbit) != set(range(width)) or
            any(by_cbit[i].get("virtual_qubit") != i for i in range(width))):
        raise ValueError("Provider virtual-qubit mapping differs from submitted identity measurement")
    physical = [row.get("physical_qubit") for row in mapping]
    if any(type(q) is not int or q < 0 for q in physical) or len(set(physical)) != width:
        raise ValueError("Missing or duplicate physical-qubit mapping")
    if not result.executed_qasm or not result.compiler or not result.task_id:
        raise ValueError("Missing executed circuit, compiler identity or task_id")
    if result.target != target or result.backend != target:
        raise ValueError("Actual backend does not match the explicit target")
    decoded = {label[::-1]: value for label, value in counts.items()}
    return {"schema": "qb-quafu-sdk-receipt-v1", "observed_at": now(), "sdk": sdk,
            "mode": "cloud_hardware" if target == "Baihua" else "cloud_simulator",
            "target": result.target, "backend": result.backend, "job_id": str(job_id),
            "task_id": str(result.task_id), "status": result.status,
            "submitted_qasm_sha256": kernel["qasm_sha256"],
            "executed_qasm": result.executed_qasm,
            "executed_qasm_sha256": hashlib.sha256(result.executed_qasm.encode()).hexdigest(),
            "compiler": result.compiler, "calibration_id": result.calibration_id,
            "measurements": mapping, "bit_order": result.bit_order,
            "counts_raw": counts, "counts_q0_first": decoded,
            "shots_requested": shots, "shots_returned": returned,
            "shot_shortfall": returned != shots,
            "probabilities_q0_first": {k: v / returned for k, v in decoded.items()},
            "raw_payload_sha256": digest(result.raw),
            "reproducibility": "Frozen inputs and receipts; hardware noise is not a deterministic seed"}


def run_manifest(client, manifest, journal_path, *, max_tasks, shots=1024,
                 max_qubits=6, target="Baihua", timeout=5, execute=False,
                 on_result=None):
    import fcntl
    identity = sdk_identity()
    manifest_hash = digest(manifest)
    journal_path = Path(journal_path)
    journal_path.parent.mkdir(parents=True, exist_ok=True)
    with journal_path.with_suffix(".lock").open("a") as lock:
        fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        journal = json.loads(journal_path.read_text()) if journal_path.exists() else {
            "schema": "qb-quafu-sdk-batch-v1", "created_at": now(),
            "manifest_sha256": manifest_hash, "target": target, "shots": shots,
            "max_tasks": max_tasks, "max_qubits": max_qubits, "sdk": identity, "jobs": {}}
        if journal_path.exists() and journal.get("integrity_sha256") != digest(
                {k: v for k, v in journal.items() if k != "integrity_sha256"}):
            raise ValueError("Journal integrity check failed; do not resubmit")
        expected = (manifest_hash, target, shots, max_tasks, max_qubits, identity)
        actual = tuple(journal[k] for k in ("manifest_sha256", "target", "shots", "max_tasks", "max_qubits", "sdk"))
        if actual != expected:
            raise ValueError("Journal/configuration changed; preserve the original batch")
        kernels = manifest["kernels"]
        if type(max_tasks) is not int or max_tasks < len(kernels):
            raise ValueError("Complete case plan exceeds approved task count; no partial submission")
        metadata = client.metadata(target)
        limits = metadata.get("limits")
        preflight = {key: validate_kernel(k, limits, shots=shots, max_qubits=max_qubits)
                     for key, k in kernels.items()}
        if execute:
            device = next((d for d in client.devices() if d["name"] == target), None)
            if not device or device["kind"] != "real" or device["status"] != "online":
                raise ValueError("Explicit hardware target is not online; no automatic fallback")
            quota = client.stats()["quota"]["real"]
            needed = len(set(kernels) - set(journal["jobs"]))
            available = quota.get("remaining", 0)
            if type(available) is not int or available < 0 or quota.get("degraded"):
                raise ValueError("Invalid/degraded quota; refuse extra submissions")
        else:
            available = 0
        for key, kernel in kernels.items():
            entry = journal["jobs"].get(key)
            if entry is None:
                if not execute:
                    continue
                if available <= 0:
                    # Preserve completed and pending jobs. No lower-priority or
                    # unapproved extra usage, and no implicit next-day resubmit.
                    journal["stop_reason"] = "normal_quota_exhausted"
                    save_journal(journal_path, journal)
                    break
                entry = {"state": "submission_intent", "created_at": now(), "preflight": preflight[key]}
                journal["jobs"][key] = entry
                save_journal(journal_path, journal)
                # A crash or unknown acceptance leaves the durable intent unresolved.
                # Never automatically resubmit an intent without a returned Job id.
                try:
                    job = client.submit(kernel["openqasm"], target=target, shots=shots,
                                        compiler="qiskit", name=f"QB-{key[:16]}")
                except Exception as exc:
                    entry.update(state="submission_unresolved", error_type=type(exc).__name__)
                    save_journal(journal_path, journal)
                    raise RuntimeError("Submission stopped; reconcile unresolved intent before retry") from None
                entry.update(state="submitted", job_id=str(job.id), submitted_at=now())
                available -= 1
                save_journal(journal_path, journal)
            if entry.get("receipt"):
                continue
            if not entry.get("job_id"):
                raise ValueError("Unresolved submission intent; manual provider reconciliation required")
            try:
                result = client.job(entry["job_id"]).result(timeout=timeout)
                entry["receipt"] = normalize_result(result, kernel, entry["job_id"], target, shots, identity)
                entry["state"] = "verified_result"
            except Exception as exc:
                entry.update(state="awaiting_or_failed", last_query_at=now(), error_type=type(exc).__name__)
                save_journal(journal_path, journal)
                # Timeouts keep the job alive. All other errors stop this batch.
                if type(exc).__name__ != "Timeout":
                    raise RuntimeError(f"Cloud query stopped ({type(exc).__name__}); journal retained") from None
            save_journal(journal_path, journal)
            if entry.get("receipt") and on_result is not None:
                on_result(journal_path)
        return journal


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--inspect-public", type=Path)
    parser.add_argument("--manifest", type=Path)
    parser.add_argument("--journal", type=Path)
    parser.add_argument("--max-tasks", type=int)
    parser.add_argument("--execute", action="store_true")
    parser.add_argument("--timeout", type=float, default=5)
    parser.add_argument("--ca-bundle")
    parser.add_argument("--refresh-pages", type=Path,
                        help="Repository root; rebuild case docs after each verified receipt")
    parser.add_argument("--documentation-python", default="python3")
    args = parser.parse_args()
    import quafu
    client = quafu.Client(ca_bundle=args.ca_bundle)
    if args.inspect_public:
        snapshot = inspect_public(client)
        save(args.inspect_public, snapshot)
        print(json.dumps({"snapshot_sha256": digest(snapshot), "sdk": snapshot["sdk"], "new_cloud_tasks": 0}))
        return
    if not args.manifest or not args.journal or not args.max_tasks:
        parser.error("--manifest, --journal and --max-tasks are required")
    saved = Path(os.environ.get("QUAFU_CONFIG_DIR", Path.home() / ".quafu-sdk")) / "credentials.json"
    if not os.environ.get("QUAFU_API_KEY") and not saved.exists():
        raise RuntimeError("No new-SDK credentials configured; no browser login is initiated")
    def refresh(journal_path):
        subprocess.run([args.documentation_python,
                        str(args.refresh_pages / "scripts/update_quafu_case_notebooks.py"),
                        "--journal", str(journal_path.resolve())], cwd=args.refresh_pages, check=True)
    result = run_manifest(client, json.loads(args.manifest.read_text()), args.journal,
                          max_tasks=args.max_tasks, timeout=args.timeout, execute=args.execute,
                          on_result=refresh if args.refresh_pages else None)
    print(json.dumps({"tasks": len(result["jobs"]), "verified": sum(bool(v.get("receipt")) for v in result["jobs"].values())}))


if __name__ == "__main__":
    main()
