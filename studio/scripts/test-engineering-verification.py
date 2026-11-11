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


if __name__ == "__main__":
    unittest.main()
