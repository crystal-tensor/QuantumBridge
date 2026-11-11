#!/usr/bin/env python3
"""Record isolated dependency experiments, never Native acceptance."""
import argparse
import json
from pathlib import Path
import platform
import xml.etree.ElementTree as ET

from record_engineering_verification import ROOT, load, native_fingerprint, sha

SDK = {"main": ("2.4.1", "0.44.1"), "alternate": ("2.6.0", "0.42.3")}
ORDERS = {
    "arrow_only": ["pyarrow"], "qiskit_arrow": ["qiskit", "pyarrow"],
    "arrow_qiskit": ["pyarrow", "qiskit"], "tf_arrow": ["tensorflow", "pyarrow"],
    "tf_qiskit_arrow": ["tensorflow", "qiskit", "pyarrow"],
    "tf_qiskit_arrow_system_pool": ["tensorflow", "qiskit", "pyarrow"],
}
SCRIPT = "studio/downloads/arrow_qiskit_import_probe.py"


def import_matrix(checkpoint, prefix, arrow, source_hash):
    rows = load(checkpoint/(prefix+"import-controls.json"))["rows"]
    expected = {(profile, case) for profile in SDK for case in ORDERS}
    if len(rows) != len(expected) or {(r["profile"], r["case"]) for r in rows} != expected:
        raise ValueError("Incomplete or duplicate import-control population")
    for row in rows:
        observed = row["observations"]
        versions = {"qiskit":SDK[row["profile"]][0], "pennylane":SDK[row["profile"]][1],
                    "pyarrow":arrow, "tensorflow":"2.21.0"}
        expected_pool = "system" if row["case"].endswith("_system_pool") else None
        if (row["native_accepted"] is not False or observed["native_accepted"] is not False
                or observed["quantumbridge_imported"] is not False or row["terminal"] is not True
                or type(row["process_exit"]) is not int or row["process_exit"] not in (0, -11)
                or observed["arrow_pool_setting"] != expected_pool
                or row["probe_source_sha256"] != source_hash
                or [r["requested"] for r in observed["modules"]] != ORDERS[row["case"]]
                or any(r["version"] != versions[r["requested"]] for r in observed["modules"])):
            raise ValueError("Import diagnostic identity, exit or acceptance claim differs")
        for suffix, key in (("stdout","stdout_sha256"),("stderr","stderr_sha256")):
            path=checkpoint/(prefix+row["profile"]+"-"+row["case"]+"."+suffix)
            if sha(path.read_bytes()) != row[key]:
                raise ValueError("Import-control raw receipt changed")
        if json.loads((checkpoint/(prefix+row["profile"]+"-"+row["case"]+".stdout")).read_text().splitlines()[-1]) != observed:
            raise ValueError("Import-control output does not match its report")
    return rows


def public_candidates(checkpoint, frozen):
    manifest = load(frozen/"source-manifest.json")
    source = frozen/"source"
    for name, expected in manifest.items():
        path = (source/name).resolve()
        if not path.is_relative_to(source) or sha(path.read_bytes()) != expected:
            raise ValueError("Frozen candidate source changed")
    rows = load(checkpoint/"candidate-public-results.json")["rows"]
    if len(rows) != 2 or {r["profile"] for r in rows} != set(SDK):
        raise ValueError("Both candidate public profiles are required")
    for row in rows:
        name = "candidate-public-"+row["profile"]
        terminal = load(checkpoint/(name+".json"))
        origin = load(checkpoint/(name+"-origin.json"))
        dependency = load(checkpoint/(name+"-dependencies.json"))
        xml = checkpoint/(name+".xml")
        cases = ET.parse(xml).getroot().findall(".//testcase")
        old = ET.parse(frozen/("public-"+row["profile"]+".xml")).getroot().findall(".//testcase")
        key = lambda c: c.get("classname")+"::"+c.get("name")
        failed = lambda cases: {key(c) for c in cases if c.find("failure") is not None or c.find("error") is not None}
        actual = dependency["actual_imported_versions"]
        expected_sdk = SDK[row["profile"]]
        baseline = next(r["environment"] for r in load(ROOT/"docs/engineering/verification_runs.json")["runs"]
                        if r["name"] == "mps-memory-contract-strict-"+row["profile"])
        if (row["native_accepted"] is not False or terminal["exit"] != 1 or terminal["terminal"] is not True
                or row["exit"] != terminal["exit"] or origin["test_exit"] != terminal["exit"]
                or dependency["test_exit"] != terminal["exit"] or dependency["allocator_override"] is not False
                or dependency["baseline_environments_modified"] is not False or dependency["native_accepted"] is not False
                or (actual["qiskit"],actual["pennylane"]) != expected_sdk or actual["pyarrow"] != "25.0.1"
                or actual["tensorflow"] != "2.21.0"
                or any(dependency["environment"].get(name) != version for name,version in baseline.items())
                or dependency["environment"]["pyarrow"] != actual["pyarrow"]
                or Path(origin["root"]).resolve() != source or not origin["matching_modules"]
                or len(cases) != 512 or len(failed(cases)) != 19
                or any(c.find("skipped") is not None for c in cases)
                or {key(c) for c in cases} != {key(c) for c in old} or failed(cases) != failed(old)
                or row["junit_sha256"] != sha(xml.read_bytes())
                or row["origin_sha256"] != sha((checkpoint/(name+"-origin.json")).read_bytes())
                or row["dependency_receipt_sha256"] != sha((checkpoint/(name+"-dependencies.json")).read_bytes())):
            raise ValueError("Candidate public math, dependencies or terminal identity differs")
    return [dict(profile=r["profile"], total=512, passed=493, failed=19, skipped=0,
        process_exit=r["exit"], recorded_at=r["recorded_at"], junit_sha256=r["junit_sha256"],
        dependency_receipt_sha256=r["dependency_receipt_sha256"],
        environment=load(checkpoint/("candidate-public-"+r["profile"]+"-dependencies.json"))["environment"],
        original_case_population_and_failure_ids_unchanged=True, native_accepted=False) for r in rows], native_fingerprint(manifest)


def record(checkpoint, frozen):
    source_hash = sha((ROOT/SCRIPT).read_bytes())
    baseline = import_matrix(checkpoint, "", "24.0.0", source_hash)
    candidate = import_matrix(checkpoint, "candidate25-", "25.0.1", source_hash)
    expected_crashes = {("alternate",name) for name in
        ("qiskit_arrow","arrow_qiskit","tf_qiskit_arrow","tf_qiskit_arrow_system_pool")}
    if ({(r["profile"],r["case"]) for r in baseline if r["process_exit"] != 0} != expected_crashes
            or any(r["process_exit"] != 0 for r in candidate)):
        raise ValueError("Observed coexistence contrast differs; do not reuse the old conclusion")
    public, fingerprint = public_candidates(checkpoint, frozen)
    download = load(checkpoint/"candidate-download.json")
    if (download["version"] != "25.0.1" or Path(download["filename"]).name != download["filename"]
            or not download["url"].startswith("https://files.pythonhosted.org/")
            or download["official_digest_matched"] is not True or download["tls_verification_disabled"] is not False
            or sha((checkpoint/download["filename"]).read_bytes()) != download["sha256"]):
        raise ValueError("Candidate download trust receipt differs")
    report = dict(native_accepted=False, source_sha256=source_hash,
        observed_host=dict(system=platform.system(),machine=platform.machine()),
        review_state="EXPERIMENTALLY_VERIFIED_NOT_PROMOTED_TO_REFERENCE_BASELINE",
        baseline_environments_modified=False, sdk_target_versions_changed=False,
        scope="Import-only coexistence and unchanged selected public cases, not function acceptance or a full suite",
        summary="Qiskit2.6/PyArrow24 crashes without QuantumBridge, in both import orders. System pool does not prevent it. Isolated PyArrow25.0.1 controls and both 512-case public selections exit normally, retaining all 19 existing assertion failures. Original profiles and crash receipts remain unchanged.",
        baseline_imports=baseline, candidate_imports=candidate, candidate_public=public,
        wheel={k:download[k] for k in ("version","filename","url","sha256","size","official_digest_matched","tls_verification_disabled")},
        primary_sources=["https://github.com/apache/arrow/issues/50428", "https://arrow.apache.org/release/25.0.1.html"])
    paths=[checkpoint/"import-controls.json", checkpoint/"candidate25-import-controls.json", checkpoint/"candidate-public-results.json"]
    evidence_hash=sha(b"".join(p.read_bytes() for p in paths))
    observation=dict(id="arrow_coexistence_dependency_review", kind="arrow_coexistence_review", profile="main_and_alternate",
        recorded_at=max(r["recorded_at"] for r in public), evidence_hash=evidence_hash,
        source_file=SCRIPT, report=report, scope="diagnostic_observation_not_function_or_test_acceptance")
    output=ROOT/"docs/engineering/diagnostic_observations.json"
    value=load(output)
    if value["source_fingerprint"] != fingerprint:
        raise ValueError("Do not relabel prior diagnostics with another Native fingerprint")
    value["observations"]=[r for r in value["observations"] if r["id"] != observation["id"]]+[observation]
    output.write_text(json.dumps(value,indent=2)+"\n")
    print(json.dumps(dict(observations=len(value["observations"]),source_fingerprint=fingerprint,
        review_state=report["review_state"],native_accepted=False)))


if __name__ == "__main__":
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--checkpoint",required=True,type=Path)
    parser.add_argument("--frozen",required=True,type=Path)
    args=parser.parse_args()
    record(args.checkpoint.resolve(),args.frozen.resolve())
