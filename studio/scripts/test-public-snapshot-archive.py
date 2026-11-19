"""Transport preserves complete failed records, unknown fields and byte identity."""
import gzip
import hashlib
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

spec=importlib.util.spec_from_file_location('snapshot_archive',Path(__file__).resolve().parents[2]/'scripts/public_snapshot_archive.py')
archive=importlib.util.module_from_spec(spec)
spec.loader.exec_module(archive)


class SnapshotTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.path=Path(self.temp.name)/'manifest.json'
        self.value=dict(schema=1,generated_at='2026-11-13T12:44:02Z',source=dict(fingerprint='a'*64,dirty=True),
            verification=[dict(name='old failure',recorded_at='original',cases=[dict(id='original-case',status='failed')])],
            unknown=dict(keep=[False,3,'中文']),goal_complete=False)

    def stored(self):
        archive.dump(self.path,self.value,raw_threshold=1)
        return json.loads(self.path.read_bytes())

    def mutate(self,change):
        index=json.loads(self.path.read_bytes())
        change(index)
        self.path.write_text(json.dumps(index))

    def test_small_legacy_shape_and_gzip_download_match(self):
        archive.dump(self.path,self.value)
        raw=self.path.read_bytes()
        self.assertNotIn('public_snapshot_format',json.loads(raw))
        self.assertEqual(gzip.decompress(self.path.with_name('manifest.json.gz').read_bytes()),raw)
        self.assertEqual(archive.load(self.path),self.value)

    def test_archive_keeps_every_original_field_and_identity(self):
        index=self.stored()
        self.assertLess(self.path.stat().st_size,1024)
        self.assertEqual(index['snapshot_identity']['generated_at'],self.value['generated_at'])
        self.assertEqual(archive.load(self.path),self.value)
        self.assertEqual(hashlib.sha256(archive.read_bytes(self.path)).hexdigest(),index['sha256'])

    def test_existing_whitespace_and_unknown_fields_are_byte_exact(self):
        raw=json.dumps(self.value,ensure_ascii=False,indent=4).encode()+b'\n\n'
        self.path.write_bytes(raw)
        archive.write_bytes(self.path,archive.read_bytes(self.path),raw_threshold=1)
        self.assertEqual(archive.read_bytes(self.path),raw)

    def test_new_snapshot_retains_prior_immutable_complete_payload(self):
        old=self.stored()
        before=(self.path.parent/old['file']).read_bytes()
        self.value['generated_at']='2026-11-14T00:44:02Z'
        self.value['verification'].append(dict(name='new',status='passed'))
        new=archive.dump(self.path,self.value,raw_threshold=1)
        self.assertNotEqual(new['file'],old['file'])
        self.assertEqual((self.path.parent/old['file']).read_bytes(),before)
        self.assertEqual(json.loads(gzip.decompress(before))['verification'][0]['cases'][0]['status'],'failed')
        self.assertEqual(archive.load(self.path),self.value)

    def test_corrupt_payload_is_rejected(self):
        index=self.stored()
        path=self.path.parent/index['file']
        body=path.read_bytes()
        path.write_bytes(body[:-1]+bytes([body[-1]^1]))
        with self.assertRaisesRegex(ValueError,'compressed hash'):archive.load(self.path)

    def test_original_hash_and_time_cannot_be_forged(self):
        for change,pattern in ((lambda v:v.update(sha256='b'*64),'original bytes'),
                (lambda v:v['snapshot_identity'].update(generated_at='new time'),'identity differs')):
            with self.subTest(pattern=pattern):
                self.stored();self.mutate(change)
                with self.assertRaisesRegex(ValueError,pattern):archive.load(self.path)

    def test_traversal_unknown_versions_and_invalid_bounds_are_rejected(self):
        for fields in ({'file':'../private.gz'},{'bytes':True},{'bytes':archive.MAX_ORIGINAL_BYTES+1},
                {'compressed_bytes':archive.MAX_COMPRESSED_BYTES+1},{'public_snapshot_format':'future'}):
            with self.subTest(fields=fields):
                self.stored();self.mutate(lambda value:value.update(fields))
                with self.assertRaises(ValueError):archive.load(self.path)

    def test_undersized_descriptor_bounds_gzip_expansion(self):
        self.stored();self.mutate(lambda value:value.update(bytes=1))
        with self.assertRaisesRegex(ValueError,'original bytes'):archive.load(self.path)

    def test_symlink_payload_is_rejected(self):
        index=self.stored();payload=self.path.parent/index['file'];saved=self.path.parent/'outside.gz'
        payload.rename(saved);payload.symlink_to(saved)
        with self.assertRaisesRegex(ValueError,'escaped'):archive.load(self.path)

    def test_browser_projection_cannot_claim_complete_snapshot(self):
        with self.assertRaises(ValueError):archive.dump(self.path,dict(self.value,deferred_evidence={}),raw_threshold=1)

    def test_rewriting_same_payload_is_deterministic(self):
        index=self.stored();before=self.path.read_bytes();raw=archive.read_bytes(self.path)
        self.assertEqual(archive.write_bytes(self.path,raw,raw_threshold=1),index)
        self.assertEqual(self.path.read_bytes(),before)

    def view(self):
        self.stored()
        raw=archive.read_bytes(self.path)
        archive.write_bytes(self.path,raw,raw_threshold=1,reuse_views=True)
        return raw,json.loads(self.path.read_bytes())

    def wrapped(self):
        raw,index=self.view()
        with patch.object(archive,'RAW_INDEX_THRESHOLD',1):
            wrapper=archive.compact_index(self.path)
        return raw,index,wrapper

    def test_compressed_index_keeps_exact_raw_download_failure_and_unknown_fields(self):
        raw,index=self.view()
        download=self.path.with_name('manifest.json.gz').read_bytes()
        inner=self.path.read_bytes()
        with patch.object(archive,'RAW_INDEX_THRESHOLD',1):wrapper=archive.compact_index(self.path)
        self.assertEqual(wrapper['public_snapshot_format'],archive.INDEX_FORMAT)
        self.assertEqual(archive.read_bytes(self.path),raw)
        self.assertEqual(self.path.with_name('manifest.json.gz').read_bytes(),download)
        self.assertEqual(gzip.decompress((self.path.parent/wrapper['file']).read_bytes()),inner)
        self.assertEqual(archive.load(self.path),self.value)
        self.assertEqual(wrapper['snapshot_identity'],index['snapshot_identity'])

    def test_writer_continues_incrementally_from_a_compressed_index(self):
        self.wrapped()
        files={path.name:path.read_bytes() for path in self.path.parent.glob('*-index-*.json.gz')}
        self.value['verification'].append(dict(name='later failure',status='failed'))
        with patch.object(archive,'RAW_INDEX_THRESHOLD',1):
            result=archive.dump(self.path,self.value,raw_threshold=1,reuse_views=True)
        self.assertEqual(result['public_snapshot_format'],archive.INDEX_FORMAT)
        self.assertEqual(archive.load(self.path),self.value)
        self.assertTrue(all((self.path.parent/name).read_bytes()==body for name,body in files.items()))

    def test_compressed_index_rejects_forged_bounds_hashes_identity_and_paths(self):
        _,_,original=self.wrapped()
        changes=[{'file':'../outside.gz'},{'index_bytes':True},{'index_bytes':archive._views.MAX_INDEX+1},
            {'index_compressed_bytes':True},{'index_compressed_bytes':archive._views.MAX_INDEX+1},
            {'index_sha256':'b'*64},{'index_bytes':1},{'sha256':'b'*64},
            {'snapshot_identity':dict(original['snapshot_identity'],generated_at='forged')},
            {'snapshot_identity':dict(original['snapshot_identity'],source_fingerprint='b'*64)},
            {'download':dict(original['download'],sha256='b'*64)},
            {'extra':'x'*4096}]
        for change in changes:
            with self.subTest(change=list(change)):
                self.path.write_text(json.dumps(dict(original,**change)))
                with self.assertRaises((ValueError,OSError,EOFError)):archive.read_bytes(self.path)

    def test_compressed_index_symlink_and_payload_tampering_are_rejected(self):
        _,_,wrapper=self.wrapped()
        target=self.path.parent/wrapper['file'];body=target.read_bytes()
        target.write_bytes(body[:-1]+bytes([body[-1]^1]))
        with self.assertRaisesRegex(ValueError,'hash differs'):archive.read_bytes(self.path)
        target.write_bytes(body);saved=target.with_name('other.gz');target.rename(saved);target.symlink_to(saved)
        with self.assertRaisesRegex(ValueError,'escaped'):archive.read_bytes(self.path)


if __name__=='__main__':unittest.main()
