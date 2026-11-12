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
    def test_browser_manifest_transport_preserves_every_field_without_restamping(self):
        original = dict(schema=1, generated_at="2026-11-12T20:50:00Z",
            source=dict(fingerprint="a"*64, dirty=True), census_complete=False,
            future_metadata=dict(untouched=["中文", False, 1]))
        original.update({name: [] for name in builder.DEFERRED_MANIFEST_FIELDS})
        original["verification"] = [dict(cases=[dict(id="case", status="failed")], evidence_hash="proof")]
        original["strict_backlog"] = [dict(id="case", status="current_failure")]
        original["test_contexts"] = dict(proof=dict(files=["tests/test_contract.py"]))
        before = json.dumps(original)
        with tempfile.TemporaryDirectory() as directory:
            destination = Path(directory)
            bootstrap = builder.browser_manifest_assets(original, destination)
            encoded = (destination/"manifest-browser.json.gz").read_bytes()
            self.assertEqual(json.loads(gzip.decompress(encoded)), bootstrap)
            descriptor = bootstrap["deferred_evidence"]
            self.assertEqual(descriptor["fields"], list(builder.DEFERRED_MANIFEST_FIELDS))
            evidence = (destination/descriptor["file"]).read_bytes()
            self.assertEqual(len(evidence), descriptor["bytes"])
            self.assertEqual(builder.digest(evidence), descriptor["sha256"])
            payload = json.loads(gzip.decompress(evidence))
            self.assertEqual(payload["generated_at"], original["generated_at"])
            self.assertEqual(payload["source_fingerprint"], original["source"]["fingerprint"])
            restored = dict(bootstrap, **payload["fields"])
            del restored["deferred_evidence"], restored["strict_backlog_count"]
            self.assertEqual(restored, original)
            self.assertEqual(bootstrap["strict_backlog_count"], 1)
            builder.browser_manifest_assets(original, destination)
            self.assertEqual((destination/"manifest-browser.json.gz").read_bytes(), encoded)
            self.assertEqual((destination/descriptor["file"]).read_bytes(), evidence)
            with self.assertRaises(ValueError):
                builder.browser_manifest_assets(bootstrap, destination)
        self.assertEqual(json.dumps(original), before)

    def test_browser_manifest_cannot_silently_omit_evidence_fields(self):
        with tempfile.TemporaryDirectory() as directory:
            with self.assertRaises(KeyError):
                builder.browser_manifest_assets(dict(generated_at="original", source=dict(fingerprint="a"*64)), Path(directory))

    def test_browser_buckets_keep_search_fields_and_exact_observations(self):
        rows = [dict(id=name, name=name, signature="point", exposures=["public."+name],
            runtime_observations=[dict(profile="main", signature=dict(available=True), lookup_plane=plane)])
            for name, plane in (("one", "instance"), ("two", "metaclass"))]
        before = json.dumps(rows)
        with tempfile.TemporaryDirectory() as directory:
            destination = Path(directory)
            descriptor = builder.runtime_browser_assets(rows, destination)
            def read(item):
                data = (destination/item["file"]).read_bytes()
                self.assertEqual(builder.digest(data), item["sha256"])
                return json.loads(gzip.decompress(data))
            index = read(descriptor)
            for original, row in zip(rows, index):
                bucket = row.pop("detail_bucket")
                self.assertEqual(row, {key: value for key, value in original.items() if key != "runtime_observations"})
                detail = read(descriptor["details"][bucket])
                full = next(item for item in detail["rows"] if item["id"] == original["id"])
                observation = dict(full["runtime_observations"][0])
                observation["signature"] = detail["signatures"][observation.pop("signature_ref")]
                self.assertEqual(observation, original["runtime_observations"][0])
        self.assertEqual(json.dumps(rows), before)

    def test_runtime_signature_pool_preserves_every_observation_without_merging_contexts(self):
        signature = dict(available=True, parameters=[dict(name="point", kind="POSITIONAL_ONLY")])
        rows = [dict(id=name, exposures=[name], runtime_observations=[dict(profile="main", signature=signature,
            lookup_plane=plane)]) for name, plane in (("owner.one", "instance"), ("owner.two", "metaclass"))]
        before = json.dumps(rows)
        projected = builder.runtime_projection(rows)
        self.assertEqual(json.dumps(rows), before)
        self.assertEqual(len(projected["rows"]), 2)
        self.assertEqual(len(projected["signatures"]), 1)
        for original, row in zip(rows, projected["rows"]):
            observation = dict(row["runtime_observations"][0])
            observation["signature"] = projected["signatures"][observation.pop("signature_ref")]
            self.assertEqual(observation, original["runtime_observations"][0])
            self.assertEqual(row["exposures"], original["exposures"])

    def test_public_projection_pools_contexts_and_preserves_private_evidence(self):
        context = dict(files=["tests/test_contract.py"], sha256="same")
        value = dict(runs=[dict(name=name, test_context=context, passed=1, evidence_hash="junit",
            cases=[dict(id="tests.test_contract::test_path[/Users/private/item]", status="passed")])
            for name in ("one", "two")])
        original = json.dumps(value)
        projected = builder.verification_projection(value)
        self.assertEqual(json.dumps(value), original)
        self.assertEqual(len(projected["test_contexts"]), 1)
        self.assertEqual(projected["public_projection"]["redacted_parameter_ids"], 2)
        restored = builder.verification_rows(projected)
        for row in restored:
            self.assertEqual(row["test_context"], context)
            self.assertEqual(row["passed"], 1)
            self.assertEqual(row["evidence_hash"], "junit")
            self.assertEqual(row["cases"][0]["status"], "passed")
            self.assertTrue(row["cases"][0]["parameter_identity_redacted"])
        self.assertEqual(restored[0]["cases"][0]["id"], restored[1]["cases"][0]["id"])
        self.assertNotIn("/Users/", json.dumps(projected))
        self.assertEqual(builder.verification_projection(projected), projected)

    def test_public_projection_refuses_unknown_private_fields_and_context_collisions(self):
        with self.assertRaisesRegex(ValueError, "Unexpected private field"):
            builder.verification_projection(dict(runs=[dict(note="/Users/private/item", cases=[])]))
        with self.assertRaisesRegex(ValueError, "share an identity"):
            builder.verification_projection(dict(runs=[dict(cases=[], test_context=dict(sha256="same", files=files))
                for files in (["a"], ["b"])]))
        with self.assertRaisesRegex(ValueError, "reference differs"):
            builder.verification_rows(dict(runs=[dict(test_context=dict(sha256="same", files_ref="same", file_count=2))],
                test_contexts=dict(same=dict(sha256="same", files=["a"]))))

    def test_historical_diagnosis_keeps_original_source_and_cannot_be_current_review(self):
        run = dict(name="now", profile="main", source_match=True, recorded_at="now",
            cases=[dict(id="f[bad]", status="failed"), dict(id="f[good]", status="passed")])
        note = dict(prefix="f", classification="OPEN", diagnosis="old diagnosis", next="recheck")
        rows = {row["id"]: row for row in builder.strict_backlog(
            [dict(name="old", failure_ids=["f[bad]", "f[good]"])], [run],
            historical_notes=[note], historical_source_fingerprint="old-source")}
        self.assertEqual(rows["f[bad]"]["status"], "current_failure")
        self.assertNotIn("review_note", rows["f[bad]"])
        self.assertEqual(rows["f[bad]"]["historical_review_note"]["source_fingerprint"], "old-source")
        self.assertFalse(rows["f[bad]"]["historical_review_note"]["source_match"])
        self.assertNotIn("historical_review_note", rows["f[good]"])
        current = dict(note, diagnosis="new diagnosis")
        row, = builder.strict_backlog([], [dict(run, cases=[run["cases"][0]])], [current],
            historical_notes=[note], historical_source_fingerprint="old-source")
        self.assertEqual(row["review_note"]["diagnosis"], "new diagnosis")
        self.assertNotIn("historical_review_note", row)

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

    def test_real_process_exit_receipt_is_required_for_current_verification(self):
        self.assertFalse(builder.process_terminal_matches({"exit_code":1}))
        good = {"provided":True, "exit":1, "receipt_hash":"a"*64}
        self.assertTrue(builder.process_terminal_matches({"exit_code":1,"process_terminal_validation":good}))
        for process in (None, {}, {**good,"exit":-11}, {**good,"exit":True},
                        {**good,"provided":False}, {**good,"receipt_hash":None},
                        {**good,"receipt_hash":"g"*64}):
            with self.subTest(process=process):
                self.assertFalse(builder.process_terminal_matches({"exit_code":1,"process_terminal_validation":process}))
        self.assertFalse(builder.process_terminal_matches({"exit_code":0,"process_terminal_validation":good}))

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
