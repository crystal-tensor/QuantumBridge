"""Evidence upgrades must be source-matched and cannot result from name presence."""
import importlib.util
from pathlib import Path
import unittest
import gzip
import json
import tempfile
from unittest.mock import patch

spec = importlib.util.spec_from_file_location("engineering_builder", Path(__file__).resolve().parents[2] / "scripts/build_engineering_progress.py")
builder = importlib.util.module_from_spec(spec)
spec.loader.exec_module(builder)


class EvidenceTests(unittest.TestCase):
    def test_diagnostic_is_stale_when_its_control_code_changes_and_cannot_claim_acceptance(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            path = root/"studio/downloads/control.py"
            path.parent.mkdir(parents=True)
            path.write_text("original control")
            row = dict(kind="tf_cached_cos",source_file="studio/downloads/control.py",
                scope="diagnostic_observation_not_function_or_test_acceptance",
                report=dict(native_accepted=False,source_sha256=builder.digest(path.read_bytes())))
            value = dict(source_fingerprint="current",observations=[row])
            with patch.object(builder,"ROOT",root):
                self.assertTrue(builder.diagnostic_observations(value,"current")[0]["source_match"])
                path.write_text("changed control")
                self.assertFalse(builder.diagnostic_observations(value,"current")[0]["source_match"])
                row["report"]["native_accepted"] = True
                with self.assertRaisesRegex(ValueError,"cannot claim acceptance"):
                    builder.diagnostic_observations(value,"current")

    def test_namespace_discovery_is_not_public_function_acceptance(self):
        value = dict(profile="main", collected_at="fixture", census_complete=True,
            modules=[dict(name="fixture",family="fixture",private_path=False,test_path=False,runtime_inspected=True),
                     dict(name="fixture.other",family="fixture",private_path=False,test_path=False,runtime_inspected=False),
                     dict(name="fixture._private",family="fixture",private_path=True,test_path=False,runtime_inspected=False)],
            packages=[dict(name="fixture",candidate_modules=999,available=True)],
            unresolved=[],closure_pending=["dynamic exports"])
        with tempfile.TemporaryDirectory() as directory:
            data = Path(directory)
            source = data/"namespaces-main.json.gz"
            source.write_bytes(gzip.compress(json.dumps(value).encode()))
            with patch.object(builder,"DATA",data):
                result, = builder.namespace_audits([source])
        self.assertFalse(result["census_complete"])
        self.assertEqual(result["candidate_modules"],3)
        self.assertEqual(result["public_path_candidates"],2)
        self.assertEqual(result["public_path_runtime_inspected"],1)
        self.assertEqual(result["packages"][0]["candidate_modules"],3)

    def test_changed_benchmark_contract_cannot_keep_same_native_source_green(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            path = root / "tests/test_contract.py"
            path.parent.mkdir()
            path.write_bytes(b"assert True\n")
            rows = [["tests/test_contract.py", builder.digest(path.read_bytes())]]
            context = {"files": [rows[0][0]], "sha256": builder.digest(json.dumps(rows, separators=(",", ":")).encode())}
            with patch.object(builder, "ROOT", root):
                self.assertTrue(builder.test_context_matches(context))
                path.write_bytes(b"assert False\n")
                self.assertFalse(builder.test_context_matches(context))
    def test_runtime_exports_remain_a_separate_unverified_population(self):
        signature = {"available": True, "parameters": [{"name": "shots", "kind": "KEYWORD_ONLY",
                     "default": {"present": True, "literal": True, "value": 1024}}]}
        reference = {"profile": "fixture", "collected_at": "now", "modules": [
            {"name": "qiskit", "version": "fixture"}, {"name": "qiskit_finance", "available": False}],
            "unresolved": [], "closure_pending": ["recursive traversal"], "records": [
            {"id": "qiskit.Child.method", "canonical_id": "qiskit.Child.method", "family": "qiskit",
             "kind": "method", "file": "qiskit/base.py", "source_hash": "sha", "signature": signature,
             "owner_class": "qiskit.Child", "declared_in": "qiskit.Base", "inherited": True,
             "exposures": ["qiskit.Child.method"], "status": "implemented"}]}
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "runtime.json.gz"
            path.write_bytes(gzip.compress(json.dumps(reference).encode()))
            rows, audits = builder.runtime_census([path])
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0]["status"], "unverified")
        self.assertIsNone(rows[0]["native_mapping"])
        self.assertTrue(rows[0]["runtime_observations"][0]["inherited"])
        self.assertEqual(audits[0]["inherited_contexts"], 1)
        self.assertFalse(audits[0]["census_complete"])
        self.assertEqual(audits[0]["modules"][1]["name"], "qiskit_finance")

    def test_stale_or_incomplete_review_never_upgrades(self):
        for review in [{"id":"f","source_hash":"old","status":"implemented"}, {"id":"f","source_hash":"now","status":"implemented"}]:
            row = {"id":"f","source_hash":"now","status":"unverified"}
            builder.apply_reviews([row],[review])
            self.assertEqual(row["status"],"unverified")

    def test_complete_current_review_is_admitted(self):
        row = {"id":"f","source_hash":"now","status":"unverified"}
        review = {"id":"f","source_hash":"now","status":"implemented", "contract_complete":True,"native_independent":True,"versions_verified":True,"strict_tests_pass":True,"evidence_hash":"receipt"}
        builder.apply_reviews([row],[review])
        self.assertEqual(row["status"],"implemented")

    def test_change_in_another_core_file_invalidates_old_review(self):
        row = {"id":"f","source_hash":"now","status":"unverified"}
        review = {"id":"f","source_hash":"now","status":"partial","project_fingerprint":"old-project"}
        builder.apply_reviews([row],[review],"new-project")
        self.assertEqual(row["status"],"unverified")

    def test_abstract_refusal_is_not_automatically_missing(self):
        rows,errors,_ = builder.census(builder.ROOT/"quantumbridge/chemistry","quantumbridge.chemistry",native=True)
        self.assertFalse(errors)
        missing = {r["name"] for r in rows if r["status"] == "not_implemented"}
        self.assertEqual(missing,{"quantumbridge.chemistry.mappings.ParityMapper.map","quantumbridge.chemistry.mappings.BravyiKitaevMapper.map"})

    def test_selected_pass_is_never_complete_failure_resolution(self):
        historical = [{"name":"old-main", "failure_ids":["a", "b"]}]
        current = [{"name":"new-main", "profile":"main", "source_match":True,
                    "recorded_at":"now", "cases":[{"id":"a", "status":"passed"}, {"id":"c", "status":"failed"}]}]
        rows = {r["id"]:r for r in builder.strict_backlog(historical, current)}
        self.assertEqual(rows["a"]["status"], "selected_batch_pass_only")
        self.assertEqual(rows["b"]["status"], "reproduction_pending")
        self.assertEqual(rows["c"]["status"], "current_failure")

    def test_stale_failure_observation_cannot_be_current_verification(self):
        stale = [{"name":"stale", "profile":"main", "source_match":False,
                  "recorded_at":"old", "cases":[{"id":"a", "status":"passed"}]}]
        rows = builder.strict_backlog([{"name":"old", "failure_ids":["a"]}], stale)
        self.assertEqual(rows[0]["status"], "reproduction_pending")

    def test_input_order_does_not_hide_current_passes_for_stale_failures(self):
        current = {"name":"current", "profile":"main", "source_match":True,
                   "recorded_at":"new", "cases":[{"id":"f", "status":"passed"}]}
        stale = {"name":"stale", "profile":"main", "source_match":False,
                 "recorded_at":"old", "cases":[{"id":"f", "status":"failed"}]}
        for runs in ([current, stale], [stale, current]):
            rows = builder.strict_backlog([], runs)
            self.assertEqual(rows[0]["status"], "selected_batch_pass_only")
            self.assertEqual(len(rows[0]["observations"]), 2)

    def test_review_note_never_upgrades_a_failure_or_applies_to_a_pass(self):
        run = {"name":"now", "profile":"main", "source_match":True, "recorded_at":"now",
               "cases":[{"id":"f[bad]", "status":"failed"}, {"id":"f[good]", "status":"passed"}]}
        note = {"prefix":"f", "classification":"CONTRACT_REVIEW_REQUIRED", "diagnosis":"pending", "next":"audit"}
        rows = {r["id"]:r for r in builder.strict_backlog([{"name":"old", "failure_ids":["f[good]"]}], [run], [note])}
        self.assertEqual(rows["f[bad]"]["status"], "current_failure")
        self.assertIn("review_note", rows["f[bad]"])
        self.assertNotIn("review_note", rows["f[good]"])


if __name__ == "__main__":
    unittest.main()
