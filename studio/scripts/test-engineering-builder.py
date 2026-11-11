"""Evidence upgrades must be source-matched and cannot result from name presence."""
import importlib.util
from pathlib import Path
import unittest
import gzip
import json
import tempfile

spec = importlib.util.spec_from_file_location("engineering_builder", Path(__file__).resolve().parents[2] / "scripts/build_engineering_progress.py")
builder = importlib.util.module_from_spec(spec)
spec.loader.exec_module(builder)


class EvidenceTests(unittest.TestCase):
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
