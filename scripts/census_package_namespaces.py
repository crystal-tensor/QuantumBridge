#!/usr/bin/env python3
"""Inventory installed namespace candidates without importing an SDK module."""
import argparse
from collections import Counter
from datetime import datetime, timezone
import gzip
import hashlib
import importlib.machinery
import importlib.metadata
import json
from pathlib import Path, PurePosixPath

PACKAGES = ("qiskit", "pennylane", "qiskit_aer", "qiskit_algorithms", "qiskit_nature",
            "qiskit_finance", "qiskit_optimization", "qiskit_machine_learning",
            "qiskit_dynamics", "qiskit_experiments", "qiskit_ibm_runtime", "qiskit_metal",
            "qiskit_addon_sqd", "qiskit_addon_aqc_tensor", "qiskit_addon_mpf", "qiskit_addon_obp")


def module_file(name, family):
    path = PurePosixPath(str(name))
    if path.is_absolute() or any(part in {"..", "."} for part in path.parts):
        return None
    if not path.parts or path.parts[0] != family:
        return None
    suffixes = [(".py", "python"), (".pyi", "typing_stub")]
    suffixes += [(suffix, "extension") for suffix in sorted(importlib.machinery.EXTENSION_SUFFIXES, key=len, reverse=True)]
    for suffix, kind in suffixes:
        if path.name.endswith(suffix):
            stem = path.name[:-len(suffix)]
            parts = (*path.parts[:-1], *(() if stem == "__init__" else (stem,)))
            if not all(part.isidentifier() for part in parts):
                return None
            return ".".join(parts), kind
    return None


def file_digest(path):
    value = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024*1024), b""):
            value.update(block)
    return value.hexdigest()


def inventory(profile, observed, packages=PACKAGES, distribution=importlib.metadata.distribution):
    modules, package_rows, unresolved = {}, [], []
    for family in packages:
        try:
            installed = distribution(family.replace("_", "-"))
        except importlib.metadata.PackageNotFoundError:
            package_rows.append(dict(name=family, version=None, available=False, still_in_scope=True))
            continue
        before = len(modules)
        files = installed.files
        if files is None:
            unresolved.append(dict(package=family, kind="distribution_file_list_unavailable"))
        for entry in files or ():
            matched = module_file(entry, family)
            if matched is None:
                continue
            module, kind = matched
            path = Path(installed.locate_file(entry))
            if not path.is_file():
                unresolved.append(dict(package=family, module=module, kind="declared_file_missing"))
                continue
            row = modules.setdefault(module, dict(name=module, family=family, files=[],
                private_path=any(part.startswith("_") for part in module.split(".")[1:]),
                test_path=any(part in {"test", "tests"} for part in module.split(".")[1:]),
                runtime_inspected=module in observed, contract_reviewed=False))
            row["files"].append(dict(file=str(entry), kind=kind, sha256=file_digest(path)))
        count = len(modules)-before
        if not count:
            unresolved.append(dict(package=family, kind="no_package_module_files_observed"))
        package_rows.append(dict(name=family, version=installed.version, available=True,
                                 candidate_modules=count, still_in_scope=True))
    rows = sorted(modules.values(), key=lambda row: row["name"])
    public = [row for row in rows if not row["private_path"] and not row["test_path"]]
    return dict(schema=1, profile=profile, collected_at=datetime.now(timezone.utc).isoformat(),
        scope="installed_distribution_module_candidates_not_closed_public_api",
        census_complete=False, sdk_modules_imported=False,
        policy="Distribution metadata and file hashes only. Private/test paths remain candidates, not automatically excluded; runtime exports may expose them. No SDK implementation copied or Native mapping inferred.",
        packages=package_rows, modules=rows, unresolved=unresolved,
        summary=dict(candidate_modules=len(rows), public_path_candidates=len(public),
            public_path_runtime_inspected=sum(row["runtime_inspected"] for row in public),
            file_kinds=dict(Counter(file["kind"] for row in rows for file in row["files"]))),
        closure_pending=["public export reachability for each module", "dynamic or generated modules",
            "private implementation re-exports", "entry-point plugins", "uninstalled optional packages",
            "complete per-function contracts and Native mappings"])


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--profile", required=True)
    parser.add_argument("--runtime", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    raw = args.runtime.read_bytes()
    runtime = json.loads(gzip.decompress(raw) if args.runtime.suffix == ".gz" else raw)
    if runtime["profile"] != args.profile:
        raise ValueError("Namespace and runtime reference profiles differ")
    observed = {row["name"] for row in runtime["modules"] if row.get("available")}
    result = inventory(args.profile, observed)
    body = (json.dumps(result, ensure_ascii=False, indent=2)+"\n").encode()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_bytes(gzip.compress(body, mtime=0) if args.output.suffix == ".gz" else body)
    print(json.dumps(dict(profile=args.profile, **result["summary"], census_complete=False), indent=2))
