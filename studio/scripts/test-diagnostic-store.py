"""New diagnostic runs cannot relabel or erase older observations."""
from copy import deepcopy
import importlib.util
from pathlib import Path
import unittest

SCRIPTS = Path(__file__).parents[2]/"scripts"
spec = importlib.util.spec_from_file_location("diagnostic_store", SCRIPTS/"engineering_diagnostic_store.py")
store = importlib.util.module_from_spec(spec)
spec.loader.exec_module(store)
spec = importlib.util.spec_from_file_location("diagnostic_builder", SCRIPTS/"build_engineering_progress.py")
builder = importlib.util.module_from_spec(spec)
spec.loader.exec_module(builder)
OLD, NEW = "a"*64, "b"*64


def observation(name, *, fingerprint=None, evidence="old-evidence", report_fingerprint=None):
    report = dict(native_accepted=False, untouched=["old raw facts"])
    if report_fingerprint is not None:
        report["source_fingerprint"] = report_fingerprint
    result = dict(id=name, kind="control", recorded_at="original-time", evidence_hash=evidence,
                  scope=store.SCOPE, report=report)
    if fingerprint is not None:
        result["source_fingerprint"] = fingerprint
    return result


class DiagnosticStoreTests(unittest.TestCase):
    def test_partial_batch_keeps_arrow_and_original_fingerprints_timestamps_and_facts(self):
        old = dict(source_fingerprint=OLD, observations=[observation("tf"), observation("arrow")])
        before = deepcopy(old)
        result = store.merge_observations(old, NEW, [observation("new")])
        self.assertEqual(old, before)
        self.assertEqual([row["id"] for row in result["observations"]], ["tf", "arrow", "new"])
        for original, updated in zip(before["observations"], result["observations"][:2]):
            self.assertEqual(updated, dict(original, source_fingerprint=OLD))
        self.assertEqual(result["observations"][2]["source_fingerprint"], NEW)
        statuses = builder.diagnostic_observations(result, NEW)
        self.assertEqual([row["source_match"] for row in statuses], [False, False, True])

    def test_replaced_run_is_archived_and_repeated_registration_is_idempotent(self):
        old = dict(source_fingerprint=OLD, observations=[observation("tf")])
        replacement = observation("tf", evidence="new-evidence")
        result = store.merge_observations(old, NEW, [replacement])
        self.assertEqual(result["historical_observations"], [dict(old["observations"][0], source_fingerprint=OLD)])
        self.assertEqual(store.merge_observations(result, NEW, [replacement]), result)

    def test_reported_legacy_fingerprint_takes_precedence_over_global_header(self):
        old = dict(source_fingerprint=NEW, observations=[observation("mps", report_fingerprint=OLD)])
        result = store.merge_observations(old, NEW, [])
        self.assertEqual(result["observations"][0]["source_fingerprint"], OLD)
        self.assertFalse(builder.diagnostic_observations(result, NEW)[0]["source_match"])

    def test_conflicting_or_missing_identity_and_duplicate_ids_are_rejected(self):
        for value in [dict(observations=[observation("lost")]),
                      dict(source_fingerprint=OLD, observations=[observation("duplicate"), observation("duplicate")]),
                      dict(source_fingerprint=OLD, observations=[observation("conflict", fingerprint=NEW, report_fingerprint=OLD)])]:
            with self.assertRaises(ValueError):
                store.merge_observations(value, NEW, [])
        for replacements in [[observation("duplicate"), observation("duplicate")],
                             [observation("wrong", fingerprint=OLD)]]:
            with self.assertRaises(ValueError):
                store.merge_observations({}, NEW, replacements)

    def test_implementation_claim_cannot_enter_the_diagnostic_store(self):
        row = observation("false-pass")
        row["report"]["native_accepted"] = True
        with self.assertRaisesRegex(ValueError, "cannot claim acceptance"):
            store.merge_observations({}, NEW, [row])

    def test_builder_does_not_trust_a_conflicting_explicit_fingerprint(self):
        row = observation("conflict", fingerprint=NEW, report_fingerprint=OLD)
        value = dict(source_fingerprint=NEW, observations=[row])
        self.assertFalse(builder.diagnostic_observations(value, NEW)[0]["source_match"])

    def test_invalid_declared_fingerprints_cannot_fall_back_to_a_new_header(self):
        for invalid in (None, "", False, "unknown"):
            row = observation("invalid", fingerprint=NEW)
            row["source_fingerprint"] = invalid
            with self.assertRaises(ValueError):
                store.merge_observations(dict(source_fingerprint=NEW, observations=[row]), NEW, [])
            if invalid != "unknown":
                value = dict(source_fingerprint=NEW, observations=[row])
                self.assertFalse(builder.diagnostic_observations(value, NEW)[0]["source_match"])


if __name__ == "__main__":
    unittest.main()
