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


def verification_rows(value):
    """Restore pooled test contexts without mutating private or public evidence."""
    contexts = value.get("test_contexts", {})
    result = []
    for original in value.get("runs", []):
        row = dict(original)
        context = row.get("test_context")
        if context and "files_ref" in context:
            full = contexts[context["files_ref"]]
            if (full["sha256"] != context["sha256"] or len(full["files"]) != context["file_count"]
                    or "files" in context):
                raise ValueError("Public test-context reference differs")
            row["test_context"] = full
        result.append(row)
    return result


def verification_projection(value):
    """Pool repeated context lists and hash private pytest parameter identities."""
    runs, contexts, redacted = [], {}, 0
    forbidden = ("/Users/", "site-packages/", "QUAFU_TOKEN")
    for original in verification_rows(value):
        row = dict(original)
        cases = []
        for original_case in row.get("cases", []):
            case = dict(original_case)
            identity = case["id"]
            if any(part in identity for part in forbidden):
                hashed = digest(identity.encode())
                prefix = identity.partition("[")[0]
                if any(part in prefix for part in forbidden):
                    prefix = "redacted-test"
                case.update(id=prefix+"[private-parameter-sha256="+hashed+"]",
                    original_id_sha256=hashed, parameter_identity_redacted=True)
            redacted += bool(case.get("parameter_identity_redacted"))
            cases.append(case)
        row["cases"] = cases
        context = row.get("test_context")
        if context:
            key = context["sha256"]
            if key in contexts and contexts[key] != context:
                raise ValueError("Different test contexts share an identity")
            contexts[key] = context
            row["test_context"] = dict(sha256=key, files_ref=key, file_count=len(context["files"]))
        runs.append(row)
    result = dict(runs=runs, test_contexts=contexts,
        public_projection=dict(redacted_parameter_ids=redacted,
            original_status_counts_and_evidence_hashes_preserved=True, private_ledger_modified=False))
    if any(part in json.dumps(result, ensure_ascii=False) for part in forbidden):
        raise ValueError("Unexpected private field in public verification projection")
    return result


def runtime_projection(rows):
    """Intern equal JSON signature metadata, never callable or behavior identity."""
    signatures, result = {}, []
    for row in rows:
        observations = []
        for original in row["runtime_observations"]:
            observation = dict(original)
            signature = observation.pop("signature", None)
            if signature is not None:
                key = digest(json.dumps(signature, sort_keys=True, separators=(",", ":")).encode())
                signatures[key] = signature
                observation["signature_ref"] = key
            observations.append(observation)
        result.append(dict(row, runtime_observations=observations))
    return dict(schema=2, encoding="signature-pool-v1", rows=result, signatures=signatures)


def runtime_browser_assets(rows, destination):
    """Keep every searchable field; fetch exact observation metadata by hash bucket."""
    buckets, index = {}, []
    for row in rows:
        bucket = digest(row["id"].encode())[:2]
        buckets.setdefault(bucket, []).append(dict(id=row["id"], runtime_observations=row["runtime_observations"]))
        index.append(dict((key, value) for key, value in row.items() if key != "runtime_observations"))
        index[-1]["detail_bucket"] = bucket
    def write(name, value):
        body = json.dumps(value, ensure_ascii=False, separators=(",", ":")).encode()
        compressed = gzip.compress(body, mtime=0)
        (destination / name).write_bytes(compressed)
        return dict(file=name, sha256=digest(compressed))
    details = {key: dict(write("runtime-details-"+key+".json.gz", runtime_projection(items)), count=len(items))
               for key, items in sorted(buckets.items())}
    return dict(write("runtime-browser.json.gz", index), details=details)


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


def apply_reviews(records, reviews, project_fingerprint=None):
    """Only exact, current source evidence can upgrade the conservative baseline."""
    by_id = {row["id"]: row for row in records}
    for review in reviews:
        row = by_id.get(review.get("id"))
        if row is None or review.get("source_hash") != row["source_hash"]:
            continue
        if project_fingerprint is not None and review.get("project_fingerprint") != project_fingerprint:
            continue
        required = ("contract_complete", "native_independent", "versions_verified", "strict_tests_pass", "evidence_hash")
        if review.get("status") == "implemented" and not all(review.get(k) for k in required):
            continue
        if review.get("status") in {"implemented", "partial", "not_implemented", "unverified"}:
            row["status"] = review["status"]
            row["reason"] = "reviewed_contract"
            row["review"] = review


def strict_backlog(historical, verification, notes=(), *, historical_notes=(), historical_source_fingerprint=None):
    rows = {}
    for run in historical:
        for case in run["failure_ids"]:
            rows.setdefault(case, {"id": case, "historical_batches": [], "observations": []})["historical_batches"].append(run["name"])
    # Discover failures before attaching observations: re-recording a batch
    # must not hide passes stored earlier in the input list.
    for run in verification:
        for case in run["cases"]:
            if case["status"] == "failed":
                rows.setdefault(case["id"], {"id": case["id"], "historical_batches": [], "observations": []})
    for run in verification:
        for case in run["cases"]:
            if case["id"] in rows:
                row = rows[case["id"]]
                row["observations"].append({"batch": run["name"], "profile": run["profile"],
                    "status": case["status"], "source_match": run["source_match"],
                    "recorded_at": run["recorded_at"]})
    for row in rows.values():
        current = [o for o in row["observations"] if o["source_match"]]
        row["status"] = "current_failure" if any(o["status"] == "failed" for o in current) else "selected_batch_pass_only" if current and all(o["status"] == "passed" for o in current) else "reproduction_pending"
        if row["status"] == "current_failure":
            for note in notes:
                if row["id"].startswith(note["prefix"]):
                    row["review_note"] = {key: note[key] for key in ("classification", "diagnosis", "next", "diagnosis_zh", "next_zh") if key in note}
            if "review_note" not in row and historical_source_fingerprint:
                for note in historical_notes:
                    if row["id"].startswith(note["prefix"]):
                        row["historical_review_note"] = {
                            **{key: note[key] for key in ("classification", "diagnosis", "next", "diagnosis_zh", "next_zh") if key in note},
                            "source_fingerprint": historical_source_fingerprint,
                            "source_match": False,
                        }
    return sorted(rows.values(), key=lambda row: row["id"])


def runtime_census(paths):
    """Keep runtime/MRO discoveries separate from the unclosed AST register."""
    merged, audits = {}, []
    for path in paths:
        raw = path.read_bytes()
        reference = json.loads(gzip.decompress(raw) if path.suffix == ".gz" else raw)
        records = reference["records"]
        collection_receipts = reference.get("collection_receipts", [])
        if reference.get("scope") == "isolated_sdk_metadata_union_not_coexistence_or_acceptance":
            if not collection_receipts or any(receipt.get("terminal") is not True
                    or type(receipt.get("exit")) is not int or receipt["exit"] != 0
                    for receipt in collection_receipts):
                raise ValueError("Isolated runtime census lacks normal terminal receipts")
        audits.append({"profile": reference["profile"], "collected_at": reference["collected_at"],
            "artifact_hash": digest(raw), "modules": reference["modules"],
            "environment": reference.get("environment", {}),
            "scope": reference.get("scope"), "coexistence_verified": False,
            "collection_receipts": collection_receipts,
            "traversal_audits": reference.get("traversal_audits", []),
            "descriptor_reclassifications": reference.get("descriptor_reclassifications", []),
            "class_protocol_audits": reference.get("class_protocol_audits", []),
            "object_identity_groups": reference.get("object_identity_groups", []),
            "object_identity_audits": reference.get("object_identity_audits", []),
            "object_identity_policy": reference.get("object_identity_policy"),
            "class_graph": reference.get("class_graph"),
            "class_graph_audits": reference.get("class_graph_audits", []),
            "records": len(records), "inherited_contexts": sum(bool(r.get("inherited")) for r in records),
            "signature_reviews_pending": sum(not r["signature"]["available"] for r in records),
            "unresolved": reference["unresolved"], "closure_pending": reference["closure_pending"],
            "census_complete": False})
        versions_by_family = {}
        for module in reference["modules"]:
            if module.get("version"):
                versions_by_family.setdefault(module["name"].split(".")[0], set()).add(module["version"])
        for observed in records:
            key = observed["id"]
            row = merged.setdefault(key, {"id": key, "name": key, "family": observed["family"],
                "module": observed.get("owner_class") or observed["exposures"][0].rsplit(".", 1)[0],
                "kind": observed["kind"], "file": observed["file"], "source_hash": observed["source_hash"],
                "signature": "", "signatures": [], "profiles": [], "exposures": [], "runtime_observations": [],
                "status": "unverified", "reason": "contract_review_pending",
                "hardware": "unverified", "origin": "runtime_public_mro", "native_mapping": None})
            versions = sorted(versions_by_family.get(observed["family"], ()))
            row["profiles"].append(reference["profile"]+": "+" / ".join(versions))
            row["exposures"] = sorted(set(row["exposures"]) | set(observed["exposures"]))
            row["runtime_observations"].append({"profile": reference["profile"],
                **{k: observed[k] for k in ("canonical_id", "signature", "file", "source_hash",
                    "inherited", "declared_in", "canonical_identity_review_required", "collection_isolation",
                    "accessor", "source_hash_scope", "declaration_module", "declared_in_reference_namespace",
                    "lookup_plane", "metaclass", "metaclass_mro", "implicit_class_protocol", "descriptor_type",
                    "descriptor_protocol", "descriptor_semantics_review_required", "wrapped_accessor_binding",
                    "signature_semantics", "object_identity_group", "class_identity", "owner_class_identity",
                    "declaring_class_identity", "metaclass_identity", "mro_identities", "direct_base_identities",
                    "metaclass_mro_identities") if k in observed}})
            sig = observed["signature"]
            parameters = sig.get("parameters", [])
            names = []
            for parameter in parameters:
                prefix = "**" if parameter["kind"] == "VAR_KEYWORD" else "*" if parameter["kind"] == "VAR_POSITIONAL" else ""
                name = prefix+parameter["name"]
                if parameter["default"].get("present"):
                    default = parameter["default"]
                    # Values are already reduced to JSON primitives, never SDK
                    # objects whose repr could execute or expose host state.
                    name += "="+repr(default["value"]) if default.get("literal") else "=<review>"
                names.append(name)
            text = ", ".join(names) if sig["available"] else "<signature review pending>"
            row["signature"] = row["signature"] or text
            row["signatures"].append(reference["profile"]+": ("+text+")")
    return sorted(merged.values(), key=lambda row: row["id"]), audits


def test_context_matches(context, cache=None):
    if context is None:
        return True
    cache = {} if cache is None else cache
    rows = []
    for name in context["files"]:
        path = (ROOT / name).resolve()
        if not path.is_relative_to((ROOT / "tests").resolve()) or not path.is_file():
            return False
        if name not in cache:
            cache[name] = digest(path.read_bytes())
        rows.append([name, cache[name]])
    return digest(json.dumps(sorted(rows), separators=(",", ":")).encode()) == context["sha256"]


def namespace_audits(paths):
    audits = []
    for path in paths:
        raw = path.read_bytes()
        value = json.loads(gzip.decompress(raw))
        profile = value["profile"]
        if profile not in {"main", "alternate"} or path.name != "namespaces-"+profile+".json.gz":
            raise ValueError("Unexpected namespace profile")
        modules = value["modules"]
        public = [row for row in modules if not row["private_path"] and not row["test_path"]]
        filename = path.name
        (DATA / filename).write_bytes(raw)
        audits.append(dict(profile=profile, collected_at=value["collected_at"], file=filename,
            artifact_hash=digest(raw), census_complete=False,
            candidate_modules=len(modules), public_path_candidates=len(public),
            public_path_runtime_inspected=sum(bool(row["runtime_inspected"]) for row in public),
            packages=[{**row, "candidate_modules":sum(m["family"] == row["name"] for m in modules)}
                      for row in value["packages"]],
            unresolved=value["unresolved"], closure_pending=value["closure_pending"]))
    return audits


def diagnostic_observations(value, fingerprint):
    observations = []
    for row in value.get("observations", []):
        if (row["report"]["native_accepted"] is not False
                or row["scope"] != "diagnostic_observation_not_function_or_test_acceptance"):
            raise ValueError("A diagnostic cannot claim acceptance")
        explicit = row.get("source_fingerprint")
        reported = row["report"].get("source_fingerprint")
        identity = explicit or reported or value.get("source_fingerprint")
        conflict = bool(explicit and reported and explicit != reported)
        conflict = conflict or ("source_fingerprint" in row and not isinstance(explicit, str))
        conflict = conflict or ("source_fingerprint" in row and not explicit)
        conflict = conflict or ("source_fingerprint" in row["report"] and not isinstance(reported, str))
        conflict = conflict or ("source_fingerprint" in row["report"] and not reported)
        current = identity == fingerprint and not conflict
        if row.get("source_file"):
            path = (ROOT / row["source_file"]).resolve()
            current = (current and path.is_relative_to((ROOT / "studio/downloads").resolve())
                       and path.is_file() and digest(path.read_bytes()) == row["report"]["source_sha256"])
        elif row["kind"] == "mps_binding_retention":
            current = current and row["report"]["source_fingerprint"] == fingerprint
        observations.append({**row, "source_fingerprint": identity, "source_match": current})
    return observations


def process_terminal_matches(run):
    process = run.get("process_terminal_validation", {})
    if not isinstance(process, dict):
        return False
    evidence = process.get("receipt_hash", "")
    return (process.get("provided") is True and type(process.get("exit")) is int
            and type(run.get("exit_code")) is int and process["exit"] in (0, 1)
            and process["exit"] == run["exit_code"] and isinstance(evidence, str)
            and len(evidence) == 64 and all(c in "0123456789abcdef" for c in evidence))


def build(args):
    DATA.mkdir(parents=True, exist_ok=True)
    execution_path = ROOT / "docs/engineering/goal_execution.json"
    execution = load_json(execution_path) if execution_path.exists() else {}
    scope_path = ROOT / "docs/engineering/acceptance_scope.json"
    scope = load_json(scope_path) if scope_path.exists() else {}
    previous = load_json(DATA / "manifest.json") if (DATA / "manifest.json").exists() else None
    native, errors, hashes = census(ROOT / "quantumbridge", "quantumbridge", native=True)
    fingerprint = digest(json.dumps(hashes, separators=(",", ":")).encode())
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
    runtime, runtime_audits = runtime_census(sorted((ROOT / "docs/engineering").glob("runtime-api-*.json.gz")))
    for audit in runtime_audits:
        groups = audit.pop("object_identity_groups", None)
        if groups is not None:
            filename = "identity-groups-"+audit["profile"]+".json.gz"
            body = json.dumps(dict(profile=audit["profile"], collected_at=audit["collected_at"],
                groups=groups, policy=audit.get("object_identity_policy"),
                native_functions_accepted=0), separators=(",", ":")).encode()
            compressed = gzip.compress(body, mtime=0)
            (DATA / filename).write_bytes(compressed)
            audit["object_identity_group_count"] = len(groups)
            audit["object_identity_groups_artifact"] = dict(file=filename, sha256=digest(compressed))
    namespaces = namespace_audits(sorted((ROOT / "docs/engineering").glob("namespaces-*.json.gz")))
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
    apply_reviews(native, reviews, fingerprint)
    apply_reviews(target, reviews, fingerprint)
    head = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip()
    dirty = bool(subprocess.check_output(["git", "status", "--porcelain", "--", "quantumbridge"], cwd=ROOT))
    now = datetime.now(timezone.utc).isoformat()
    tests = historical_tests(args.evidence_dir) if args.evidence_dir else (previous or {}).get("tests", [])
    verification_path = ROOT / "docs/engineering/verification_runs.json"
    verification = verification_rows(load_json(verification_path)) if verification_path.exists() else []
    test_hashes = {}
    for run in verification:
        run["test_context_match"] = test_context_matches(run.get("test_context"), test_hashes)
        run["process_terminal_match"] = process_terminal_matches(run)
        run["source_match"] = (run.get("source_fingerprint") == fingerprint
                               and run.get("example_input_validation", {}).get("passed", True)
                               and run["test_context_match"] and run["process_terminal_match"])
        run["freshness"] = "current_selected_source_batch" if run["source_match"] else "different_source_not_current_verification"
    failure_review_path = ROOT / "docs/engineering/failure_reviews.json"
    failure_review = load_json(failure_review_path) if failure_review_path.exists() else {}
    review_current = failure_review.get("source_fingerprint") == fingerprint
    projected = verification_projection(dict(runs=verification))
    backlog = strict_backlog(tests, projected["runs"],
        failure_review.get("notes", []) if review_current else [],
        historical_notes=[] if review_current else failure_review.get("notes", []),
        historical_source_fingerprint=None if review_current else failure_review.get("source_fingerprint"))
    diagnostic_path = ROOT / "docs/engineering/diagnostic_observations.json"
    diagnostics = diagnostic_observations(load_json(diagnostic_path), fingerprint) if diagnostic_path.exists() else []
    datasets = []
    for name, rows in [("native", native), ("target", target), ("runtime", runtime)]:
        payload = runtime_projection(rows) if name == "runtime" else rows
        body = json.dumps(payload, ensure_ascii=False, separators=(",", ":")).encode()
        compressed = gzip.compress(body, mtime=0)
        filename = f"{name}.json.gz"
        (DATA / filename).write_bytes(compressed)
        datasets.append({"id": name, "file": filename, "sha256": digest(compressed), "count": len(rows),
                         "status_counts": dict(Counter(row["status"] for row in rows))})
        if name == "runtime":
            datasets[-1]["browser"] = runtime_browser_assets(rows, DATA)
    history = load_json(DATA / "history.json") if (DATA / "history.json").exists() else []
    if previous and (not history or history[-1]["generated_at"] != previous["generated_at"]):
        history.append({"generated_at": previous["generated_at"], "fingerprint": previous["source"]["fingerprint"], "datasets": previous["datasets"]})
    dump(DATA / "history.json", history[-180:])
    manifest = {"schema": 1, "generated_at": now, "refresh_hours": 12,
                "deadline": "2027-05-11T23:59:59+08:00", "start": "2026-11-11T00:00:00+08:00",
                "source": {"head": head, "dirty": dirty, "fingerprint": fingerprint, "python_files": len(hashes), "parse_errors": errors},
                "datasets": datasets, "profiles": profiles, "runtime_census": runtime_audits,
                "namespace_census": namespaces, "census_complete": False,
                "census_limits": ["Public source declarations and historical exports are candidates, not a closed API denominator.",
                                  "Inherited methods, dynamic exports, plugins, C-extension signatures and optional packages need contract review.",
                                  "Native helpers and target public APIs are separate populations; never add their counts as a completion percentage.",
                                  "Historical test runs do not certify the current dirty working tree; function acceptance is not yet reviewed."],
                "tests": tests, "verification": projected["runs"],
                "test_contexts": projected["test_contexts"],
                "verification_projection": projected["public_projection"], "strict_backlog": backlog,
                "diagnostic_observations": diagnostics,
                "hardware": hardware(), "acceptance_scope": scope,
                "core_execution": execution.get("status", "paused_pending_new_goal"),
                "goal_execution": execution, "publication": "workspace_snapshot_not_a_release",
                "status_policy": {"implemented": "Complete reviewed contract, independent Native execution and strict version-matched tests for this source hash.",
                                  "partial": "Explicitly scoped implementation with known functional gaps or strict failures.",
                                  "not_implemented": "Reviewed missing implementation or explicit source stub; not inferred from a name mismatch.",
                                  "unverified": "Unreviewed mapping, absent evidence or stale source/test identity."}}
    dump(DATA / "manifest.json", manifest)
    (DATA / "manifest.json.gz").write_bytes(gzip.compress((DATA / "manifest.json").read_bytes(), mtime=0))
    print(json.dumps({"generated_at": now, "datasets": datasets, "hardware_receipts": len(manifest["hardware"]), "historical_test_runs": len(manifest["tests"])}, indent=2))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--enumerate-reference", type=Path)
    parser.add_argument("--profile", default="main")
    parser.add_argument("--reference", type=Path, action="append", default=[])
    parser.add_argument("--evidence-dir", type=Path)
    parser.add_argument("--project-verification", type=Path)
    args = parser.parse_args()
    if args.project_verification:
        source = ROOT / "docs/engineering/verification_runs.json"
        result = verification_projection(load_json(source))
        result["public_projection"]["private_ledger_sha256"] = digest(source.read_bytes())
        dump(args.project_verification, result)
    elif args.enumerate_reference:
        reference(args.profile, args.enumerate_reference)
    else:
        build(args)
