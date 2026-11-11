#!/usr/bin/env python3
"""Build a public, evidence-conservative engineering census. No hardware calls."""
import argparse
import ast
from collections import Counter
from datetime import datetime, timezone
import gzip
import hashlib
import importlib.metadata
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "studio/src/progress/data"
PACKAGES = ["qiskit", "pennylane", "qiskit_aer", "qiskit_algorithms",
            "qiskit_nature", "qiskit_finance", "qiskit_optimization",
            "qiskit_machine_learning", "qiskit_dynamics", "qiskit_experiments",
            "qiskit_ibm_runtime", "qiskit_metal", "qiskit_addon_sqd",
            "qiskit_addon_aqc_tensor", "qiskit_addon_mpf", "qiskit_addon_obp"]
GATES = {"GlobalPhaseGate", "U1Gate", "CU1Gate", "RZXGate", "CSXGate", "ECRGate"}
REVIEWED_MISSING = {"quantumbridge.chemistry.mappings.ParityMapper.map",
                    "quantumbridge.chemistry.mappings.BravyiKitaevMapper.map",
                    "quantumbridge.visualization.mpl_drawer.draw_mpl"}


def digest(data):
    return hashlib.sha256(data).hexdigest()


def load_json(path):
    return json.loads(path.read_text(encoding="utf-8"))


def dump(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def census(base, package, native=False):
    records, errors, hashes = [], [], []
    paths = sorted(base.rglob("*.py"))
    for path in paths:
        parts = path.relative_to(base).parts
        if any(x in {"tests", "test", "__pycache__"} for x in parts):
            continue
        if not native and any(x.startswith("_") and x != "__init__.py" for x in parts):
            continue
        raw = path.read_bytes()
        filename = str(Path(package).joinpath(*parts))
        file_hash = digest(raw)
        hashes.append([filename, file_hash])
        try:
            tree = ast.parse(raw, filename=filename)
        except (SyntaxError, UnicodeError) as exc:
            errors.append({"file": filename, "error": type(exc).__name__})
            continue
        module = ".".join([package, *parts[:-1], *([] if path.stem == "__init__" else [path.stem])])

        def walk(nodes, parents=(), in_class=False):
            for node in nodes:
                if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
                    continue
                if not native and node.name.startswith("_") and node.name not in {"__init__", "__call__", "__matmul__", "__mul__", "__add__", "__pow__", "__getitem__"}:
                    continue
                name = ".".join([module, *parents, node.name])
                kind = "class" if isinstance(node, ast.ClassDef) else "method" if in_class else "function"
                signature = ""
                if kind != "class":
                    # Signatures only, never copy third-party implementation or docstrings.
                    signature = ast.unparse(node.args)
                body = [n for n in node.body if not (isinstance(n, ast.Expr) and isinstance(n.value, ast.Constant) and isinstance(n.value.value, str))]
                def explicit_stub(statement):
                    if isinstance(statement, ast.Pass):
                        return True
                    if not isinstance(statement, ast.Raise):
                        return False
                    value = statement.exc.func if isinstance(statement.exc, ast.Call) else statement.exc
                    return isinstance(value, ast.Name) and value.id == "NotImplementedError"
                stub = kind != "class" and bool(body) and all(explicit_stub(n) for n in body)
                status = "not_implemented" if native and stub and name in REVIEWED_MISSING else "unverified"
                reason = "explicit_stub" if status == "not_implemented" else "contract_review_pending"
                if native and (node.name in GATES or parents and parents[0] in GATES) and module == "quantumbridge.core.standard_gates":
                    status, reason = "partial", "six_gate_batch_strict_failures"
                records.append({"id": name, "name": name, "family": package,
                                "module": module, "kind": kind, "signature": signature,
                                "file": filename, "line": node.lineno, "source_hash": file_hash,
                                "status": status, "reason": reason, "hardware": "unverified",
                                "origin": "native" if native else "reference_declaration"})
                # Nested local helpers are included in Native, but are not public reference API.
                if kind == "class" or native:
                    walk(node.body, (*parents, node.name), kind == "class")
        walk(tree.body)
    return records, errors, hashes


def reference(profile, output):
    result = {"profile": profile, "generated_at": datetime.now(timezone.utc).isoformat(), "packages": [], "records": [], "errors": []}
    for package in PACKAGES:
        try:
            spec = importlib.util.find_spec(package)
            if spec is None or not spec.submodule_search_locations:
                raise ModuleNotFoundError(package)
            base = Path(next(iter(spec.submodule_search_locations)))
            version = importlib.metadata.version(package.replace("_", "-"))
            records, errors, _ = census(base, package)
            result["packages"].append({"name": package, "version": version, "available": True})
            for record in records:
                record["profiles"] = [f"{profile}: {version}"]
            result["records"].extend(records)
            result["errors"].extend(errors)
        except (ModuleNotFoundError, importlib.metadata.PackageNotFoundError, ValueError):
            result["packages"].append({"name": package, "version": None, "available": False})
    dump(output, result)


def hardware():
    receipts = []
    direction = {"allocation": "portfolio", "risk": "risk", "derivatives": "pricing", "constraints": "financial-constraints", "correlation": "market-models"}
    for path in sorted((ROOT / "output/jupyter-notebook/finance").glob("*_hardware_evidence.json")):
        value = load_json(path)
        for method, result in value.get("hardware_results", {}).items():
            if not isinstance(result, dict) or not result.get("task_id"):
                continue
            artifact = result.get("artifact", {})
            counts = result.get("counts", {})
            analysis = value.get("acceptance", {})
            receipts.append({"case": value.get("case"), "direction": direction.get(value.get("case")),
                             "domain": "finance", "method": method,
                             "task_id": str(result["task_id"]), "backend": result.get("backend"),
                             "shots": result.get("shots"), "qubits": artifact.get("num_qubits"),
                             "count_sum": sum(counts.values()), "artifact_hash": artifact.get("sha256"),
                             "receipt_hash": digest(path.read_bytes()), "file": str(path.relative_to(ROOT)),
                             "execution": result.get("execution_mode"),
                             "acceptance": analysis.get("hardware_status", "UNVERIFIED"),
                             "note": "Existing receipt; not independent hardware certification or function-level acceptance."})
    return receipts


def historical_tests(directory):
    runs = []
    if not directory or not directory.exists():
        return runs
    for label in ["focused-main", "focused-alternate", "public-main", "public-alternate", "sdkfree-wheel", "regression-main", "regression-alternate", "additional-main", "additional-alternate"]:
        xml = directory / f"{label}.xml"
        meta = directory / f"{label}.json"
        if not xml.exists() or not meta.exists():
            continue
        root = ET.parse(xml).getroot()
        cases = root.findall(".//testcase")
        failures = [case for case in cases if case.find("failure") is not None or case.find("error") is not None]
        skipped = sum(case.find("skipped") is not None for case in cases)
        runs.append({"name": label, "total": len(cases), "passed": len(cases)-len(failures)-skipped,
                     "failed": len(failures), "skipped": skipped,
                     "exit_code": load_json(meta).get("exit"), "evidence_hash": digest(xml.read_bytes()),
                     "recorded_at": datetime.fromtimestamp(xml.stat().st_mtime, timezone.utc).isoformat(),
                     "source_match": False, "freshness": "historical_not_current_source",
                     "failure_ids": [f"{c.get('classname')}::{c.get('name')}" for c in failures]})
    return runs


def apply_reviews(records, reviews):
    """Only exact, current source evidence can upgrade the conservative baseline."""
    by_id = {row["id"]: row for row in records}
    for review in reviews:
        row = by_id.get(review.get("id"))
        if row is None or review.get("source_hash") != row["source_hash"]:
            continue
        required = ("contract_complete", "native_independent", "versions_verified", "strict_tests_pass", "evidence_hash")
        if review.get("status") == "implemented" and not all(review.get(k) for k in required):
            continue
        if review.get("status") in {"implemented", "partial", "not_implemented", "unverified"}:
            row["status"] = review["status"]
            row["reason"] = "reviewed_contract"
            row["review"] = review


def build(args):
    DATA.mkdir(parents=True, exist_ok=True)
    previous = load_json(DATA / "manifest.json") if (DATA / "manifest.json").exists() else None
    native, errors, hashes = census(ROOT / "quantumbridge", "quantumbridge", native=True)
    merged, profiles = {}, []
    references = args.reference or sorted((Path.home() / ".cache/quantumbridge/progress").glob("reference-*.json"))
    if not references and previous:
        profiles = previous["profiles"]
        old_targets = json.loads(gzip.decompress((DATA / "target.json.gz").read_bytes()))
        merged = {row["id"]: row for row in old_targets}
    for path in references:
        ref = load_json(path)
        profiles.append({"name": ref["profile"], "collected_at": ref.get("generated_at") or datetime.fromtimestamp(path.stat().st_mtime, timezone.utc).isoformat(), "packages": ref["packages"], "parse_errors": ref["errors"]})
        for row in ref["records"]:
            # Same function across profiles is one target row, retaining all observed signatures.
            if row["id"] in merged:
                merged[row["id"]]["profiles"].extend(row["profiles"])
                if row["signature"] not in merged[row["id"]]["signatures"]:
                    merged[row["id"]]["signatures"].append(row["signature"])
            else:
                row["signatures"] = [row["signature"]]
                merged[row["id"]] = row
    # Runtime inventories add public re-exports / extension classes missed by source declarations.
    for path in sorted((ROOT / "docs/compat/inventory").glob("*.json")):
        inventory = load_json(path)
        for row in inventory.get("records", []) if isinstance(inventory, dict) else inventory:
            if not isinstance(row, dict):
                continue
            module, name = row.get("module"), row.get("name")
            if not module or not name or not row.get("callable"):
                continue
            key = f"{module}.{name}"
            if key not in merged:
                merged[key] = {"id": key, "name": key, "family": module.split(".")[0], "module": module,
                               "kind": row.get("object_type", "callable"), "signature": "", "signatures": [],
                               "status": "unverified", "reason": "historical_export_inventory",
                               "hardware": "unverified", "origin": "historical_export", "profiles": []}
    target = sorted(merged.values(), key=lambda row: row["id"])
    for row in target:
        gate = row["name"].split(".")[-1]
        if row["kind"] == "class" and row["name"].startswith("qiskit.circuit.library.") and gate in GATES:
            row.update(status="partial", reason="six_gate_batch_strict_failures",
                       native_mapping=f"quantumbridge.core.standard_gates.{gate}")
    seen = Counter()
    for row in native:
        seen[row["id"]] += 1
        if seen[row["id"]] > 1:
            row["id"] += f"@{row['line']}"
    review_path = ROOT / "docs/engineering/function_reviews.json"
    reviews = load_json(review_path) if review_path.exists() else []
    apply_reviews(native, reviews)
    apply_reviews(target, reviews)
    head = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip()
    fingerprint = digest(json.dumps(hashes, separators=(",", ":")).encode())
    dirty = bool(subprocess.check_output(["git", "status", "--porcelain", "--", "quantumbridge"], cwd=ROOT))
    now = datetime.now(timezone.utc).isoformat()
    datasets = []
    for name, rows in [("native", native), ("target", target)]:
        body = json.dumps(rows, ensure_ascii=False, separators=(",", ":")).encode()
        compressed = gzip.compress(body, mtime=0)
        filename = f"{name}.json.gz"
        (DATA / filename).write_bytes(compressed)
        datasets.append({"id": name, "file": filename, "sha256": digest(compressed), "count": len(rows),
                         "status_counts": dict(Counter(row["status"] for row in rows))})
    history = load_json(DATA / "history.json") if (DATA / "history.json").exists() else []
    if previous and (not history or history[-1]["generated_at"] != previous["generated_at"]):
        history.append({"generated_at": previous["generated_at"], "fingerprint": previous["source"]["fingerprint"], "datasets": previous["datasets"]})
    dump(DATA / "history.json", history[-180:])
    manifest = {"schema": 1, "generated_at": now, "refresh_hours": 12,
                "deadline": "2027-05-11T23:59:59+08:00", "start": "2026-11-11T00:00:00+08:00",
                "source": {"head": head, "dirty": dirty, "fingerprint": fingerprint, "python_files": len(hashes), "parse_errors": errors},
                "datasets": datasets, "profiles": profiles, "census_complete": False,
                "census_limits": ["Public source declarations and historical exports are candidates, not a closed API denominator.",
                                  "Inherited methods, dynamic exports, plugins, C-extension signatures and optional packages need contract review.",
                                  "Native helpers and target public APIs are separate populations; never add their counts as a completion percentage.",
                                  "Historical test runs do not certify the current dirty working tree; function acceptance is not yet reviewed."],
                "tests": historical_tests(args.evidence_dir) if args.evidence_dir else (previous or {}).get("tests", []), "hardware": hardware(),
                "core_execution": "paused_pending_new_goal", "publication": "workspace_snapshot_not_a_release",
                "status_policy": {"implemented": "Complete reviewed contract, independent Native execution and strict version-matched tests for this source hash.",
                                  "partial": "Explicitly scoped implementation with known functional gaps or strict failures.",
                                  "not_implemented": "Reviewed missing implementation or explicit source stub; not inferred from a name mismatch.",
                                  "unverified": "Unreviewed mapping, absent evidence or stale source/test identity."}}
    dump(DATA / "manifest.json", manifest)
    print(json.dumps({"generated_at": now, "datasets": datasets, "hardware_receipts": len(manifest["hardware"]), "historical_test_runs": len(manifest["tests"])}, indent=2))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--enumerate-reference", type=Path)
    parser.add_argument("--profile", default="main")
    parser.add_argument("--reference", type=Path, action="append", default=[])
    parser.add_argument("--evidence-dir", type=Path)
    args = parser.parse_args()
    if args.enumerate_reference:
        reference(args.profile, args.enumerate_reference)
    else:
        build(args)
