"""The real producer must use the existing lossless migration-table transport."""
from copy import deepcopy
import gzip
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest

spec=importlib.util.spec_from_file_location("migration_pool_builder",
    Path(__file__).resolve().parents[2]/"scripts/build_engineering_progress.py")
builder=importlib.util.module_from_spec(spec)
spec.loader.exec_module(builder)


class ProducerTests(unittest.TestCase):
    def test_private_goal_paths_are_redacted_with_hashes_without_changing_other_evidence(self):
        original=dict(recorded_at="old date",source_fingerprint="a"*64,status="failed",
            nested=[dict(checkpoint="/Users/person/private/checkpoint",
                origin="Imported from /Users/person/library/site-packages/pkg/entry.py; actual hash retained.",
                evidence_hash="b"*64)])
        before=deepcopy(original)
        value,policy=builder.public_goal_execution(original)
        self.assertEqual(original,before)
        self.assertEqual(value["recorded_at"],"old date")
        self.assertEqual(value["source_fingerprint"],"a"*64)
        self.assertEqual(value["status"],"failed")
        self.assertEqual(value["nested"][0]["evidence_hash"],"b"*64)
        self.assertNotIn("/Users/",json.dumps(value))
        self.assertNotIn("site-packages/",json.dumps(value))
        self.assertEqual(len(policy["path_redactions"]),2)
        self.assertEqual(policy["path_redactions"][0]["original_value_sha256"],
            builder.digest(original["nested"][0]["checkpoint"].encode()))
        self.assertFalse(policy["private_source_modified"])
        key="/Users/private/key"
        public,policy=builder.public_goal_execution({key:dict(status="failed",sha256="c"*64)})
        identity=builder.digest(key.encode())
        self.assertEqual(public,{"private-path-sha256:"+identity:dict(status="failed",sha256="c"*64)})
        self.assertEqual(policy["path_redactions"][0]["original_key_sha256"],identity)
        with self.assertRaises(ValueError):
            builder.public_goal_execution({key:1,"private-path-sha256:"+identity:2})

    def fixture(self):
        value=dict(generated_at="original date",source=dict(fingerprint="a"*64),
            unknown=dict(retained=[False,None,"中文"]),goal_complete=False)
        value.update({name:[] for name in builder.DEFERRED_MANIFEST_FIELDS})
        table=[dict(file="tests/original.py",case_ids=[f"original::{i}" for i in range(40)],
            owner_approved=True,unknown=dict(kept=False))]
        value["verification"]=[dict(name=f"worker-{i}",profile="main" if i%2 else "alternate",
            status="failed",process_exit=-11,recorded_at="unchanged time",source_fingerprint=str(i),
            evidence_hash=f"{i:064x}",approved_test_migrations=deepcopy(table)) for i in range(50)]
        value["strict_backlog"]=[dict(id="original failure",status="current_failure")]
        return value

    def test_producer_uses_pool_and_both_public_read_paths_restore_every_record(self):
        original=self.fixture();before=deepcopy(original)
        with tempfile.TemporaryDirectory() as directory:
            destination=Path(directory)
            wire=builder.write_manifest_snapshot(original,destination,reuse_views=False)
            self.assertEqual(original,before)
            self.assertEqual(len(wire[builder._migration.FIELD]["contexts"]),1)
            self.assertTrue(all(builder._migration.REFERENCE in row for row in wire["verification"]))
            self.assertLess(len(json.dumps(wire)),len(json.dumps(original)))
            self.assertEqual(builder.load_json(destination/"manifest.json"),original)
            boot=json.loads(gzip.decompress((destination/"manifest-browser.json.gz").read_bytes()))
            self.assertNotIn(builder._migration.FIELD,boot)
            self.assertEqual(boot["deferred_evidence"]["fields"],
                list(builder.DEFERRED_MANIFEST_FIELDS)+[builder._migration.FIELD])
            projection=json.loads(gzip.decompress((destination/boot["deferred_evidence"]["file"]).read_bytes()))
            self.assertEqual(projection["fields"],boot["deferred_evidence"]["fields"])
            self.assertEqual(boot["generated_at"],"original date")
            self.assertEqual(projection["generated_at"],"original date")
            downloaded=json.loads(gzip.decompress((destination/"manifest.json.gz").read_bytes()))
            self.assertEqual(builder._migration.restore(downloaded),original)
            restored=builder._migration.restore(downloaded)
            restored["verification"][0]["approved_test_migrations"][0]["file"]="mutated"
            self.assertEqual(restored["verification"][1]["approved_test_migrations"][0]["file"],"tests/original.py")

    def test_incremental_rewrite_keeps_prior_payload_and_failed_worker_identity(self):
        first=self.fixture()
        with tempfile.TemporaryDirectory() as directory:
            destination=Path(directory)
            builder.write_manifest_snapshot(first,destination,reuse_views=False)
            saved={p.name:p.read_bytes() for p in destination.glob("manifest-*.json.gz")
                if len(p.stem.removesuffix(".json").removeprefix("manifest-"))==64}
            second=deepcopy(first);second["generated_at"]="new collection only"
            second["verification"].append(dict(name="new worker",failed=1,recorded_at="new evidence"))
            builder.write_manifest_snapshot(second,destination,reuse_views=False)
            self.assertTrue(all((destination/name).read_bytes()==body for name,body in saved.items()))
            restored=builder.load_json(destination/"manifest.json")
            self.assertEqual(restored,second)
            self.assertEqual(restored["verification"][:50],first["verification"])

    def test_ambiguous_reference_is_rejected_before_snapshot_write(self):
        original=self.fixture();original["verification"][0][builder._migration.REFERENCE]="b"*64
        with tempfile.TemporaryDirectory() as directory:
            with self.assertRaises(ValueError):
                builder.write_manifest_snapshot(original,Path(directory))
            self.assertEqual(list(Path(directory).iterdir()),[])


if __name__=="__main__":unittest.main()
