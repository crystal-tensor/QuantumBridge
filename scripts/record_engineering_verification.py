#!/usr/bin/env python3
"""Record a frozen-source JUnit batch, not function-level acceptance."""
import argparse
import ast
from datetime import datetime, timezone
import hashlib
import importlib.metadata
import importlib.util
import json
import os
from pathlib import Path
import platform
import sys
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
ENVIRONMENT_PACKAGES = ("numpy", "scipy", "tensorflow", "jax", "torch", "qiskit", "pennylane")
RUNTIME_CONTROL_KEYS = ("TF_NUM_INTEROP_THREADS", "TF_NUM_INTRAOP_THREADS", "OMP_NUM_THREADS",
                        "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "JAX_ENABLE_X64",
                        "PYTEST_DISABLE_PLUGIN_AUTOLOAD")
INTERPRETER_FLAG_KEYS = ("isolated", "no_user_site", "ignore_environment", "safe_path")

_archive_spec = importlib.util.spec_from_file_location("qb_verification_archive",
    Path(__file__).with_name("verification_archive.py"))
_archive = importlib.util.module_from_spec(_archive_spec)
_archive_spec.loader.exec_module(_archive)


def sha(data):
    return hashlib.sha256(data).hexdigest()


def load(path):
    return _archive.load(path)


def _runtime_control_value(name, value):
    if value is None:
        return None
    if name == "JAX_ENABLE_X64" and value.lower() in {"true", "false"}:
        return value.lower()
    parts = value.split(",") if name == "OMP_NUM_THREADS" else [value]
    if 1 <= len(parts) <= 16 and all(part.isascii() and part.isdecimal() and len(part) <= 9 for part in parts):
        return value
    return "unparsed"


def _capture_environment():
    versions = {}
    for name in ENVIRONMENT_PACKAGES:
        try:
            versions[name] = importlib.metadata.version(name)
        except importlib.metadata.PackageNotFoundError:
            versions[name] = None
    return {"environment": {"python": platform.python_version(), **versions},
            "runtime": {"executable": sys.executable, "prefix": sys.prefix,
                        "base_prefix": sys.base_prefix, "implementation": sys.implementation.name},
            "runtime_controls": {name: _runtime_control_value(name, os.environ.get(name))
                                 for name in RUNTIME_CONTROL_KEYS},
            "interpreter_flags": {name: None if getattr(sys.flags, name, None) is None
                                  else bool(getattr(sys.flags, name)) for name in INTERPRETER_FLAG_KEYS}}


def pytest_sessionstart(session):
    """Opt-in pytest plugin: capture metadata inside the actual test worker."""
    output = os.environ.get("QB_ENVIRONMENT_RECEIPT")
    if not output:
        return
    run_id = os.environ.get("QB_ENVIRONMENT_RUN_ID", "")
    profile = os.environ.get("QB_ENGINEERING_PROFILE", "")
    if not run_id or not profile or not session.config.option.xmlpath:
        raise ValueError("Worker environment capture needs a run ID, profile and JUnit output")
    output = Path(output)
    if output.exists():
        raise ValueError("Worker environment receipt already exists")
    root = Path(os.environ["QB_EXPECTED_NATIVE_ROOT"]).resolve()
    manifest = Path(os.environ["QB_EXPECTED_NATIVE_MANIFEST"])
    session.config._qb_worker_environment = {"output": output,
        "junit": Path(session.config.option.xmlpath), "schema": 2,
        "profile": profile, "run_id": run_id, "pid": os.getpid(), "root": str(root),
        "source_manifest_sha256": sha(manifest.read_bytes()),
        "capture_script_sha256": sha(Path(__file__).read_bytes()),
        "started_at": datetime.now(timezone.utc).isoformat(), "start": _capture_environment()}


def pytest_sessionfinish(session, exitstatus):
    state = getattr(session.config, "_qb_worker_environment", None)
    if state is not None:
        state.update(test_exit=int(exitstatus), end=_capture_environment(),
                     finished_at=datetime.now(timezone.utc).isoformat())


def pytest_unconfigure(config):
    state = getattr(config, "_qb_worker_environment", None)
    if state is None:
        return
    # JUnit's session-finish hook has completed before unconfigure runs.
    output, junit = state["output"], state["junit"]
    receipt = {key: value for key, value in state.items() if key not in {"output", "junit"}}
    receipt["complete"] = "test_exit" in state and junit.is_file()
    receipt["junit_sha256"] = sha(junit.read_bytes()) if junit.is_file() else None
    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open("x", encoding="utf-8") as destination:
        json.dump(receipt, destination, indent=2)
        destination.write("\n")


def worker_environment(args, source, manifest_path, origin, terminal):
    path = getattr(args, "environment_receipt", None)
    if path is None:
        return {}, {"provided": False, "verified": False, "source": "missing_test_worker_receipt"}
    receipt = load(path)
    if type(receipt) is not dict or type(receipt.get("start")) is not dict:
        raise ValueError("Malformed test-worker environment receipt")
    environment = receipt["start"].get("environment")
    runtime = receipt["start"].get("runtime")
    capture_hash = load(manifest_path).get("scripts/record_engineering_verification.py")
    if (type(receipt.get("schema")) is not int or receipt["schema"] not in {1, 2} or receipt.get("complete") is not True
            or receipt.get("profile") != args.profile
            or type(receipt.get("run_id")) is not str or not receipt["run_id"]
            or type(receipt.get("pid")) is not int or receipt["pid"] < 1
            or receipt.get("root") != str(source)
            or receipt.get("source_manifest_sha256") != sha(manifest_path.read_bytes())
            or type(capture_hash) is not str or len(capture_hash) != 64
            or receipt.get("capture_script_sha256") != capture_hash
            or receipt.get("junit_sha256") != sha(args.xml.read_bytes())
            or type(receipt.get("test_exit")) is not int or receipt["test_exit"] != origin["test_exit"]
            or receipt.get("start") != receipt.get("end")
            or type(environment) is not dict or set(environment) != {"python", *ENVIRONMENT_PACKAGES}
            or any(value is not None and (type(value) is not str or not value or len(value) > 128)
                   for value in environment.values()) or environment.get("python") is None
            or type(runtime) is not dict or set(runtime) != {"executable", "prefix", "base_prefix", "implementation"}
            or any(type(value) is not str or not value for value in runtime.values())
            or type(terminal) is not dict or type(terminal.get("pid")) is not int or terminal["pid"] != receipt["pid"]
            or terminal.get("environment_run_id") != receipt["run_id"]
            or terminal.get("environment_receipt_sha256") != sha(path.read_bytes())):
        raise ValueError("Test-worker environment does not match the terminal source/JUnit receipt")
    controls, flags = None, None
    if receipt["schema"] == 2:
        controls, flags = receipt["start"].get("runtime_controls"), receipt["start"].get("interpreter_flags")
        if (type(controls) is not dict or set(controls) != set(RUNTIME_CONTROL_KEYS)
                or any(value is not None and (type(value) is not str
                    or value != _runtime_control_value(name, value)) for name, value in controls.items())
                or type(flags) is not dict or set(flags) != set(INTERPRETER_FLAG_KEYS)
                or any(value is not None and type(value) is not bool for value in flags.values())):
            raise ValueError("Test-worker runtime controls or interpreter flags are invalid")
    return environment, {"provided": True, "verified": True,
        "source": "installed_distribution_metadata_captured_in_test_worker",
        "receipt_hash": sha(path.read_bytes()), "capture_script_sha256": receipt["capture_script_sha256"],
        "worker_pid": receipt["pid"], "runtime_sha256": sha(json.dumps(runtime, sort_keys=True).encode()),
        "implementation": runtime["implementation"], "stable_during_test": True,
        "runtime_controls_provided": controls is not None,
        "runtime_controls": controls, "interpreter_flags": flags,
        "runtime_controls_complete": controls is not None and "unparsed" not in controls.values(),
        "runtime_controls_scope": "requested_process_settings_not_observed_framework_pool_sizes"}


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
    terminal_path = getattr(args, "terminal", None)
    process, terminal = {"provided": False}, None
    if terminal_path:
        terminal = load(terminal_path)
        if (terminal.get("terminal") is not True or terminal.get("timed_out", False) is not False
                or type(terminal.get("exit")) is not int
                or terminal["exit"] != origin["test_exit"]):
            raise ValueError("Process terminal exit and JUnit status do not agree")
        process = {"provided": True, "exit": terminal["exit"], "receipt_hash": sha(terminal_path.read_bytes())}
    protected = load(args.protected_tests)
    unchanged, migrations = protected_tests(protected, manifest, getattr(args, "approved_migrations", None))
    environment, environment_validation = worker_environment(args, source, manifest_path, origin, terminal)
    row = {"name": args.name, "profile": args.profile,
           "recorded_at": datetime.fromtimestamp(args.xml.stat().st_mtime, timezone.utc).isoformat(),
           "source_fingerprint": native_fingerprint(manifest),
           "source_manifest_sha256": sha(manifest_path.read_bytes()),
           "evidence_hash": sha(args.xml.read_bytes()),
           "origin_receipt_hash": sha(args.origin.read_bytes()),
           "process_terminal_validation": process,
           "matching_modules": origin["matching_modules"],
           "protected_tests": unchanged, "protected_tests_unchanged": True,
           "original_protected_test_files": len(protected), "approved_test_migrations": migrations,
           "example_input_validation": example_inputs(cases, source, manifest),
           "test_context": {"files": sorted(name for name in manifest if name.startswith("tests/")),
                "sha256": sha(json.dumps(sorted([name, value] for name, value in manifest.items()
                    if name.startswith("tests/")), separators=(",", ":")).encode())},
           "environment": environment, "environment_validation": environment_validation,
           "total": len(cases), **counts, "exit_code": origin["test_exit"],
           "scope": "selected_strict_batch_not_full_contract_or_full_suite",
           "cases": cases}
    output = args.output or ROOT / "docs/engineering/verification_runs.json"
    previous = load(output) if output.exists() else {"schema": 1, "runs": []}
    previous["runs"] = [r for r in previous["runs"] if r["name"] != row["name"]] + [row]
    _archive.save(output, previous)
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
    parser.add_argument("--terminal", type=Path, help="Subprocess terminal receipt; rejects abnormal process exits despite a complete JUnit file")
    parser.add_argument("--environment-receipt", type=Path,
                        help="Metadata captured by this module's pytest plugin inside the test worker; absent means unknown, never the recorder's environment")
    parser.add_argument("--output", type=Path)
    collect(parser.parse_args())
