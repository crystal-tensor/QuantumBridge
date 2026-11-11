#!/usr/bin/env python3
"""Record a frozen-source JUnit batch, not function-level acceptance."""
import argparse
import ast
from datetime import datetime, timezone
import hashlib
import importlib.metadata
import json
from pathlib import Path
import platform
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]


def sha(data):
    return hashlib.sha256(data).hexdigest()


def load(path):
    return json.loads(path.read_text(encoding="utf-8"))


def native_fingerprint(manifest):
    rows = sorted([name, value] for name, value in manifest.items()
                  if name.startswith("quantumbridge/") and name.endswith(".py")
                  and not {"tests", "test", "__pycache__"}.intersection(Path(name).parts))
    return sha(json.dumps(rows, separators=(",", ":")).encode())


def protected_tests(protected, manifest, migrations_path=None):
    approved = {}
    for migration in load(migrations_path).get("migrations", []) if migrations_path else []:
        name = migration["file"]
        cases = migration.get("case_ids", [])
        prefix = str(Path(name).with_suffix("")).replace("/", ".")+"::"
        if (name in approved or name not in protected or migration.get("owner_approved") is not True
                or not migration.get("approval_summary") or not cases or len(cases) != len(set(cases))
                or any(not case.startswith(prefix) for case in cases)
                or migration.get("before_sha256") != protected[name]
                or migration.get("after_sha256") != manifest.get(name)
                or manifest.get(name) == protected[name]):
            raise ValueError("Invalid approved test migration: "+name)
        approved[name] = migration
    if any(manifest.get(name) != expected for name, expected in protected.items() if name not in approved):
        raise ValueError("An inherited protected test changed")
    return len(protected)-len(approved), list(approved.values())


def example_inputs(cases, source, manifest):
    """Audit explicit example imports in selected tests, not all dependencies."""
    modules, required = set(), set()
    for case in cases:
        parts = case["id"].split("::", 1)[0].split(".")
        while parts:
            name = "/".join(parts)+".py"
            if name in manifest:
                modules.add(name)
                break
            parts.pop()
    for name in modules:
        for node in ast.walk(ast.parse((source / name).read_bytes())):
            if isinstance(node, ast.ImportFrom) and node.module and node.module.startswith("examples."):
                required.add(node.module.replace(".", "/")+".py")
    return {"policy": "explicit_example_imports_only_not_full_dependency_audit",
            "required": {name: manifest.get(name) for name in sorted(required)},
            "missing": sorted(required-manifest.keys()), "passed": required <= manifest.keys()}


def collect(args):
    checkpoint = args.checkpoint.resolve()
    source = checkpoint / "source"
    manifest_path = checkpoint / "source-manifest.json"
    manifest = load(manifest_path)
    for name, expected in manifest.items():
        path = source / name
        if not path.is_relative_to(source) or sha(path.read_bytes()) != expected:
            raise ValueError(f"Frozen source changed: {name}")
    origin = load(args.origin)
    if Path(origin["root"]).resolve() != source or not origin.get("matching_modules"):
        raise ValueError("Native import origin is not the frozen source")
    cases = []
    for case in ET.parse(args.xml).getroot().findall(".//testcase"):
        status = "failed" if case.find("failure") is not None or case.find("error") is not None else "skipped" if case.find("skipped") is not None else "passed"
        cases.append({"id": f"{case.get('classname')}::{case.get('name')}", "status": status})
    if not cases:
        raise ValueError("Empty test batch is not verification")
    counts = {status: sum(c["status"] == status for c in cases) for status in ("passed", "failed", "skipped")}
    if origin["test_exit"] != (1 if counts["failed"] else 0):
        raise ValueError("JUnit status and terminal test exit do not agree")
    protected = load(args.protected_tests)
    unchanged, migrations = protected_tests(protected, manifest, getattr(args, "approved_migrations", None))
    versions = {}
    for name in ("numpy", "scipy", "tensorflow", "jax", "torch", "qiskit", "pennylane"):
        try:
            versions[name] = importlib.metadata.version(name)
        except importlib.metadata.PackageNotFoundError:
            versions[name] = None
    row = {"name": args.name, "profile": args.profile,
           "recorded_at": datetime.fromtimestamp(args.xml.stat().st_mtime, timezone.utc).isoformat(),
           "source_fingerprint": native_fingerprint(manifest),
           "source_manifest_sha256": sha(manifest_path.read_bytes()),
           "evidence_hash": sha(args.xml.read_bytes()),
           "origin_receipt_hash": sha(args.origin.read_bytes()),
           "matching_modules": origin["matching_modules"],
           "protected_tests": unchanged, "protected_tests_unchanged": True,
           "original_protected_test_files": len(protected), "approved_test_migrations": migrations,
           "example_input_validation": example_inputs(cases, source, manifest),
           "test_context": {"files": sorted(name for name in manifest if name.startswith("tests/")),
                "sha256": sha(json.dumps(sorted([name, value] for name, value in manifest.items()
                    if name.startswith("tests/")), separators=(",", ":")).encode())},
           "environment": {"python": platform.python_version(), **versions},
           "total": len(cases), **counts, "exit_code": origin["test_exit"],
           "scope": "selected_strict_batch_not_full_contract_or_full_suite",
           "cases": cases}
    output = args.output or ROOT / "docs/engineering/verification_runs.json"
    previous = load(output) if output.exists() else {"schema": 1, "runs": []}
    previous["runs"] = [r for r in previous["runs"] if r["name"] != row["name"]] + [row]
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(previous, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({key: row[key] for key in ("name", "profile", "source_fingerprint", "total", "passed", "failed", "skipped")}, indent=2))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--name", required=True)
    parser.add_argument("--profile", required=True)
    parser.add_argument("--checkpoint", required=True, type=Path)
    parser.add_argument("--xml", required=True, type=Path)
    parser.add_argument("--origin", required=True, type=Path)
    parser.add_argument("--protected-tests", required=True, type=Path)
    parser.add_argument("--approved-migrations", type=Path)
    parser.add_argument("--output", type=Path)
    collect(parser.parse_args())
