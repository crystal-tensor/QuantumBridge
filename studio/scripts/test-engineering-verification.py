"""The public verification recorder must reject stale or incomplete receipts."""
from contextlib import redirect_stdout
import importlib.util
import io
import json
from pathlib import Path
import tempfile
from types import SimpleNamespace
import unittest

spec = importlib.util.spec_from_file_location("verification", Path(__file__).resolve().parents[2] / "scripts/record_engineering_verification.py")
recorder = importlib.util.module_from_spec(spec)
spec.loader.exec_module(recorder)


class RecorderTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        source = self.root / "source"
        (source / "quantumbridge").mkdir(parents=True)
        (source / "tests").mkdir()
        self.body = b"def value(): return 1\n"
        (source / "quantumbridge/unit.py").write_bytes(self.body)
        (source / "tests/test_unit.py").write_bytes(b"assert True\n")
        self.manifest = {"quantumbridge/unit.py": recorder.sha(self.body),
                         "tests/test_unit.py": recorder.sha(b"assert True\n")}
        self.write("source-manifest.json", self.manifest)
        self.write("protected.json", {"tests/test_unit.py": self.manifest["tests/test_unit.py"]})
        self.write("origin.json", {"root": str(source), "matching_modules": 1, "test_exit": 1})
        (self.root / "run.xml").write_text('<testsuite><testcase classname="tests.test_unit" name="test_value"><failure message="unit fixture"/></testcase></testsuite>')
        self.args = SimpleNamespace(checkpoint=self.root, origin=self.root / "origin.json",
            xml=self.root / "run.xml", protected_tests=self.root / "protected.json",
            name="fixture", profile="fixture", output=self.root / "public.json")

    def write(self, name, value):
        (self.root / name).write_text(json.dumps(value))

    def test_records_selected_failure_without_private_paths_or_acceptance(self):
        with redirect_stdout(io.StringIO()):
            recorder.collect(self.args)
        text = self.args.output.read_text()
        run = json.loads(text)["runs"][0]
        self.assertEqual((run["passed"], run["failed"], run["skipped"]), (0, 1, 0))
        self.assertEqual(run["scope"], "selected_strict_batch_not_full_contract_or_full_suite")
        self.assertNotIn(str(self.root), text)

    def test_modified_frozen_source_is_rejected(self):
        (self.root / "source/quantumbridge/unit.py").write_bytes(b"changed")
        with self.assertRaisesRegex(ValueError, "Frozen source changed"):
            recorder.collect(self.args)

    def test_wrong_import_origin_is_rejected(self):
        self.write("origin.json", {"root": str(self.root / "other"), "matching_modules": 1, "test_exit": 1})
        with self.assertRaisesRegex(ValueError, "import origin"):
            recorder.collect(self.args)

    def test_changed_old_test_cannot_be_reclassified_as_unchanged(self):
        self.write("protected.json", {"tests/test_unit.py": "old-hash"})
        with self.assertRaisesRegex(ValueError, "protected test changed"):
            recorder.collect(self.args)

    def test_terminal_exit_must_match_junit(self):
        self.write("origin.json", {"root": str(self.root / "source"), "matching_modules": 1, "test_exit": 0})
        with self.assertRaisesRegex(ValueError, "terminal test exit"):
            recorder.collect(self.args)

    def migration(self, **changes):
        old = recorder.sha(b"previous fixture assertion")
        self.write("protected.json", {"tests/test_unit.py": old})
        migration = dict(file="tests/test_unit.py", before_sha256=old,
            after_sha256=self.manifest["tests/test_unit.py"], owner_approved=True,
            approval_summary="Owner approved only the fixture contract migration.",
            case_ids=["tests.test_unit::test_value"])
        migration.update(changes)
        self.write("migrations.json", {"migrations": [migration]})
        self.args.approved_migrations = self.root / "migrations.json"

    def test_approved_migration_is_not_counted_as_an_unchanged_old_test(self):
        self.migration()
        with redirect_stdout(io.StringIO()):
            recorder.collect(self.args)
        run = json.loads(self.args.output.read_text())["runs"][0]
        self.assertEqual(run["protected_tests"], 0)
        self.assertEqual(run["original_protected_test_files"], 1)
        self.assertEqual(len(run["approved_test_migrations"]), 1)
        self.assertTrue(run["protected_tests_unchanged"])

    def test_migration_cannot_cover_a_different_hash_or_case_module(self):
        for changes in ({"after_sha256": "wrong"}, {"before_sha256": "wrong"},
                        {"owner_approved": False}, {"case_ids": []},
                        {"case_ids": ["tests.unrelated::test_value"]}):
            with self.subTest(changes=changes):
                self.migration(**changes)
                with self.assertRaisesRegex(ValueError, "Invalid approved test migration"):
                    recorder.collect(self.args)

    def test_missing_example_is_not_certified_as_a_complete_snapshot(self):
        (self.root / "source/tests/test_unit.py").write_text("from examples.native_demo import main\n")
        self.manifest["tests/test_unit.py"] = recorder.sha((self.root / "source/tests/test_unit.py").read_bytes())
        self.write("source-manifest.json", self.manifest)
        self.write("protected.json", {"tests/test_unit.py": self.manifest["tests/test_unit.py"]})
        with redirect_stdout(io.StringIO()):
            recorder.collect(self.args)
        validation = json.loads(self.args.output.read_text())["runs"][0]["example_input_validation"]
        self.assertFalse(validation["passed"])
        self.assertEqual(validation["missing"], ["examples/native_demo.py"])


if __name__ == "__main__":
    unittest.main()
