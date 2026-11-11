#!/usr/bin/env python3
"""Bounded installed-module/export traversal, never Native acceptance."""
import argparse
from collections import deque
from contextlib import contextmanager
from datetime import datetime, timezone
import gzip
import hashlib
import importlib.abc
import importlib.metadata
import json
from pathlib import Path, PurePosixPath
import sys

from census_runtime_api import CensusLimitError, RuntimeCensus, deny_python_network


def load(path):
    raw = path.read_bytes()
    return json.loads(gzip.decompress(raw) if path.suffix == ".gz" else raw)


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def valid_module(name):
    return isinstance(name, str) and all(part.isidentifier() for part in name.split("."))


def test_module(name):
    return any(part in {"test", "tests", "__main__"} for part in name.split(".")[1:])


def make_plan(namespace, family, seeds=()):
    if not valid_module(family) or "." in family:
        raise ValueError("A traversal requires one reference package family")
    package, = [row for row in namespace["packages"] if row["name"] == family]
    candidates = [row for row in namespace["modules"] if row["family"] == family]
    if len({row["name"] for row in candidates}) != len(candidates):
        raise ValueError("Duplicate namespace module identity")
    scheduled, deferred = [], []
    for row in candidates:
        name = row["name"]
        if not valid_module(name) or name.split(".")[0] != family:
            raise ValueError("Namespace escaped its reference package")
        if row["private_path"] or row["test_path"] or test_module(name):
            deferred.append(dict(name=name, reason="private_or_test_path_requires_public_reexport_review"))
        else:
            scheduled.append(name)
    extras = []
    for seed in seeds:
        if not valid_module(seed["name"]):
            raise ValueError("Invalid explicit reference seed")
        if seed["name"].split(".")[0] != family:
            extras.append(dict(name=seed["name"], version=seed.get("version")))
        else:
            scheduled.append(seed["name"])
    return dict(schema=1, profile=namespace["profile"], family=family, version=package.get("version"),
        package_available=package["available"], scheduled_modules=sorted(set([family, *scheduled])),
        deferred_modules=deferred, explicit_seeds=extras,
        namespace_files=[dict(module=row["name"], **file) for row in candidates for file in row["files"]],
        census_complete=False, scope="installed_public_path_candidates_and_reexport_closure_not_full_api_acceptance")


def installed_version(family):
    try:
        return importlib.metadata.version(family.replace("_", "-"))
    except importlib.metadata.PackageNotFoundError:
        return None


def verify_files(plan, distribution=importlib.metadata.distribution):
    try:
        package = distribution(plan["family"].replace("_", "-"))
    except importlib.metadata.PackageNotFoundError:
        if plan["package_available"] or plan["namespace_files"]:
            raise ValueError("Reference package disappeared after namespace planning")
        return
    if package.version != plan["version"]:
        raise ValueError("Reference package version changed after namespace planning")
    for row in plan["namespace_files"]:
        relative = PurePosixPath(row["file"])
        if relative.is_absolute() or ".." in relative.parts or relative.parts[0] != plan["family"]:
            raise ValueError("Invalid reference namespace file")
        source = Path(package.locate_file(row["file"]))
        if not source.is_file() or digest(source) != row["sha256"]:
            raise ValueError("Reference namespace bytes changed after planning")


def verify_loaded_family(plan, distribution=importlib.metadata.distribution):
    module = sys.modules.get(plan["family"])
    if module is None:
        return dict(available=False, import_identity_verified=False)
    package = distribution(plan["family"].replace("_", "-"))
    actual = vars(module).get("__version__")
    filename = vars(module).get("__file__")
    roots = [row for row in plan["namespace_files"] if row["module"] == plan["family"]]
    matches = [row for row in roots if filename and Path(filename).resolve() == Path(package.locate_file(row["file"])).resolve()
               and digest(Path(filename)) == row["sha256"]]
    if actual != plan["version"] or not matches:
        raise ValueError("Loaded SDK identity differs from the planned distribution")
    return dict(available=True, import_identity_verified=True, version=actual,
        root_file=matches[0]["file"], root_sha256=matches[0]["sha256"])


class IsolatedSDKImport(ModuleNotFoundError):
    pass


@contextmanager
def isolate_family(family):
    other = {"qiskit", "pennylane"}-{family}
    if any(name.split(".")[0] in other for name in sys.modules):
        raise ValueError("A reference worker already imported another core SDK")
    class Guard(importlib.abc.MetaPathFinder):
        def __init__(self):
            self.blocked = set()
        def find_spec(self, fullname, path=None, target=None):
            if fullname.split(".")[0] in other:
                self.blocked.add(fullname)
                raise IsolatedSDKImport("Cross-SDK imports require a separate coexistence review", name=fullname)
    guard = Guard()
    sys.meta_path.insert(0, guard)
    try:
        yield guard
    finally:
        sys.meta_path.remove(guard)


def namespace_mutations(census):
    mutations = []
    for row in census.modules:
        module = sys.modules.get(row["name"])
        if not row.get("available") or module is None or "public_dictionary_names" not in row:
            continue
        before = set(row["public_dictionary_names"])
        after = {name for name in vars(module) if not name.startswith("_")}
        if before != after:
            mutations.append(dict(module=row["name"], added_public_names=sorted(after-before),
                removed_public_names=sorted(before-after), requires_export_rescan=True))
    return mutations


def collect(plan, *, max_modules=4096, max_records=250000, max_export_rescans=2, census_factory=RuntimeCensus):
    if type(max_modules) is not int or max_modules < 1:
        raise ValueError("max_modules must be a positive integer")
    if type(max_export_rescans) is not int or max_export_rescans < 0:
        raise ValueError("max_export_rescans must be a nonnegative integer")
    census = census_factory(plan["profile"], max_records=max_records)
    family = plan["family"]
    queue = deque(plan["scheduled_modules"]+[row["name"] for row in plan["explicit_seeds"]])
    pending = set(queue)
    visited, edges, outside, deferred_tests = set(), [], [], []
    extra_versions = {row["name"]: row["version"] for row in plan["explicit_seeds"]}
    state, incomplete = "ALL_SCHEDULED_MODULES_ATTEMPTED", None
    rescans, history = 0, []
    with deny_python_network(), isolate_family(family) as guard:
        while True:
            while queue:
                if queue[0] not in visited and len(visited) >= max_modules:
                    state = "MODULE_LIMIT_REACHED"
                    break
                name = queue.popleft()
                pending.remove(name)
                visited.add(name)
                census.modules[:] = [row for row in census.modules if row["name"] != name]
                if name in extra_versions and installed_version(name.split(".")[0]) != extra_versions[name]:
                    census.modules.append(dict(name=name, version=installed_version(name.split(".")[0]),
                        available=False, still_in_scope=True, error="UnreviewedReferenceVersion"))
                    continue
                try:
                    census.module(name)
                except CensusLimitError:
                    incomplete, state = name, "RECORD_LIMIT_REACHED"
                    census.modules.append(dict(name=name, version=plan["version"], available=name in sys.modules,
                        still_in_scope=True, enumeration_complete=False, error="CensusLimitError"))
                    break
                row = census.modules[-1]
                for child in row.get("submodule_exports", []):
                    target = child["module"]
                    edge = dict(source=name, exposure=child["exposure"], target=target)
                    if not valid_module(target) or target.split(".")[0] != family:
                        if edge not in outside:
                            outside.append(edge)
                    elif test_module(target):
                        entry = dict(**edge, reason="public_test_or_main_export_requires_side_effect_review")
                        if entry not in deferred_tests:
                            deferred_tests.append(entry)
                    else:
                        if edge not in edges:
                            edges.append(edge)
                        if target not in visited and target not in pending:
                            queue.append(target)
                            pending.add(target)
            if state != "ALL_SCHEDULED_MODULES_ATTEMPTED":
                break
            mutations = namespace_mutations(census)
            if not mutations:
                break
            if rescans >= max_export_rescans:
                state = "EXPORT_RESCAN_LIMIT_REACHED"
                break
            rescans += 1
            history.extend(dict(rescan=rescans, **row) for row in mutations)
            queue.extend(row["module"] for row in mutations)
            pending.update(queue)
        result = census.result()
        if any(name.split(".")[0] in {"qiskit", "pennylane"}-{family} for name in sys.modules):
            raise ValueError("Core SDK import isolation was bypassed")
        mutations = namespace_mutations(census)
        result["traversal"] = dict(state=state, family=family, reference_version=plan["version"],
            scheduled_modules=plan["scheduled_modules"], explicit_seeds=plan["explicit_seeds"],
            attempted_modules=sorted(visited), pending_modules=list(queue), incomplete_module=incomplete,
            deferred_modules=[row for row in plan["deferred_modules"] if row["name"] not in visited],
            public_reexport_edges=edges, external_module_exports=outside, deferred_test_exports=deferred_tests,
            blocked_cross_sdk_imports=sorted(guard.blocked), max_modules=max_modules, max_records=max_records,
            limits_bound_metadata_cardinality_not_import_rss=True, import_initialization_side_effects_verified_absent=False,
            public_function_denominator_closed=False, coexistence_verified=False,
            conditional_exports_require_original_environment_review=True)
        result["traversal"]["namespace_mutations_after_collection"] = mutations
        result["traversal"].update(export_rescan_passes_completed=rescans,
            max_export_rescans=max_export_rescans, namespace_mutation_history=history,
            records_are_a_union_of_observed_import_states=True)
        if family in {"qiskit", "pennylane"}:
            result["traversal"]["loaded_sdk_identity"] = verify_loaded_family(plan)
    result["scope"] = "recursive_module_export_metadata_not_complete_public_function_acceptance"
    return result


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    planning = commands.add_parser("plan")
    planning.add_argument("--namespaces", required=True, type=Path)
    planning.add_argument("--runtime", required=True, type=Path)
    planning.add_argument("--family", choices=("qiskit", "pennylane"), required=True)
    planning.add_argument("--output", required=True, type=Path)
    worker = commands.add_parser("collect")
    worker.add_argument("--plan", required=True, type=Path)
    worker.add_argument("--output", required=True, type=Path)
    worker.add_argument("--max-modules", type=int, default=4096)
    worker.add_argument("--max-records", type=int, default=250000)
    worker.add_argument("--max-export-rescans", type=int, default=2)
    args = parser.parse_args()
    if args.command == "plan":
        namespace, reference = load(args.namespaces), load(args.runtime)
        if namespace["profile"] != reference["profile"]:
            raise ValueError("Namespace and reference profiles differ")
        seeds = [row for row in reference["modules"] if row["name"].split(".")[0].startswith(args.family)]
        result = make_plan(namespace, args.family, seeds)
        result["namespace_input_sha256"] = digest(args.namespaces)
    else:
        plan = load(args.plan)
        verify_files(plan)
        result = collect(plan, max_modules=args.max_modules, max_records=args.max_records,
            max_export_rescans=args.max_export_rescans)
        verify_files(plan)
        result["traversal"]["plan_sha256"] = digest(args.plan)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    body = (json.dumps(result, ensure_ascii=False, indent=2)+"\n").encode()
    args.output.write_bytes(gzip.compress(body, mtime=0) if args.output.suffix == ".gz" else body)
    print(json.dumps(dict(profile=result["profile"], modules=len(result.get("modules", [])),
        records=len(result.get("records", [])), census_complete=False,
        traversal=result.get("traversal", {}).get("state"))))
