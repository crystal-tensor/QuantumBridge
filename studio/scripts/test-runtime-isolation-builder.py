"""The observer preserves isolated collection provenance without acceptance."""
import gzip
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest

spec = importlib.util.spec_from_file_location(
    "isolation_builder", Path(__file__).parents[2]/"scripts/build_engineering_progress.py"
)
builder = importlib.util.module_from_spec(spec)
spec.loader.exec_module(builder)


class IsolationBuilderTests(unittest.TestCase):
    def test_recursive_gaps_accessors_and_external_declarations_survive_without_acceptance(self):
        value = self.reference()
        value["environment"] = dict(distribution_versions=dict(tensorflow="fixture-version"))
        value["traversal_audits"] = [dict(isolation="fixture", state="MODULE_LIMIT_REACHED",
            pending_modules=["fixture.pending"], namespace_mutations_after_collection=[dict(module="fixture")],
            public_function_denominator_closed=False)]
        value["records"][0].update(accessor="set", kind="property_setter", source_hash_scope="ancestor_module_file",
            declaration_module="external", declared_in_reference_namespace=False)
        rows, audits = self.collect(value)
        self.assertEqual(audits[0]["traversal_audits"], value["traversal_audits"])
        self.assertEqual(audits[0]["environment"], value["environment"])
        observation = rows[0]["runtime_observations"][0]
        self.assertEqual(observation["accessor"], "set")
        self.assertEqual(observation["source_hash_scope"], "ancestor_module_file")
        self.assertFalse(observation["declared_in_reference_namespace"])
        self.assertEqual(rows[0]["status"], "unverified")

    def reference(self):
        return dict(profile="fixture", collected_at="now", modules=[],
            scope="isolated_sdk_metadata_union_not_coexistence_or_acceptance", coexistence_verified=True,
            collection_receipts=[dict(isolation="fixture", terminal=True, exit=0, receipt_sha256="a"*64)],
            unresolved=[], closure_pending=["contracts"], records=[dict(id="fixture.method",
                canonical_id="fixture.method", family="fixture", kind="method", file=None, source_hash=None,
                signature=dict(available=False), exposures=["fixture.method"], collection_isolation="fixture",
                status="implemented")])

    def collect(self, value):
        with tempfile.TemporaryDirectory() as directory:
            source = Path(directory)/"runtime.json.gz"
            source.write_bytes(gzip.compress(json.dumps(value).encode()))
            return builder.runtime_census([source])

    def test_isolated_metadata_never_certifies_coexistence_or_native_implementation(self):
        rows, audits = self.collect(self.reference())
        self.assertFalse(audits[0]["coexistence_verified"])
        self.assertEqual(audits[0]["collection_receipts"][0]["exit"], 0)
        self.assertEqual(rows[0]["runtime_observations"][0]["collection_isolation"], "fixture")
        self.assertEqual(rows[0]["status"], "unverified")
        self.assertIsNone(rows[0]["native_mapping"])

    def test_abnormal_missing_and_boolean_terminal_codes_are_rejected(self):
        for exit_code in (-11, 1, False):
            value = self.reference()
            value["collection_receipts"][0]["exit"] = exit_code
            with self.assertRaisesRegex(ValueError, "normal terminal"):
                self.collect(value)
        value = self.reference()
        value["collection_receipts"] = []
        with self.assertRaisesRegex(ValueError, "normal terminal"):
            self.collect(value)


if __name__ == "__main__":
    unittest.main()
