import assert from "node:assert/strict";
import test from "node:test";
import { mkdtemp, writeFile, rm, symlink } from "node:fs/promises";
import { tmpdir } from "node:os";
import path from "node:path";
import { gzipSync } from "node:zlib";
import { createHash } from "node:crypto";
import { readProgressSnapshot, readProgressSnapshotBytes } from "./read-progress-snapshot.mjs";

const sha = value => createHash("sha256").update(value).digest("hex");
const value = { generated_at: "original date", source: { fingerprint: "a".repeat(64) },
  verification: [{ name: "old", cases: [{ id: "exact id", status: "failed" }], evidence_hash: "original hash" }],
  unknown: { preserved: [false, 2, "中文"] }, goal_complete: false };
async function setup(t) {
  const dir = await mkdtemp(path.join(tmpdir(), "qb-snapshot-"));
  t.after(() => rm(dir, { recursive: true, force: true }));
  const filename = path.join(dir, "manifest.json");
  const raw = Buffer.from(JSON.stringify(value, null, 4) + "\n\n");
  const compressed = gzipSync(raw);
  const file = "manifest-" + sha(compressed) + ".json.gz";
  const index = { public_snapshot_format: "quantumbridge.public-snapshot-gzip.v1", encoding: "gzip", file,
    bytes: raw.length, sha256: sha(raw), compressed_bytes: compressed.length, compressed_sha256: sha(compressed),
    snapshot_identity: { generated_at: value.generated_at, source_fingerprint: value.source.fingerprint } };
  await writeFile(filename, JSON.stringify(index));
  await writeFile(path.join(dir, file), compressed);
  return { dir, filename, raw, compressed, index };
}
test("legacy and archived snapshots restore exact bytes and failed records", async t => {
  const data = await setup(t);
  assert.deepEqual(await readProgressSnapshotBytes(data.filename), data.raw);
  assert.deepEqual(await readProgressSnapshot(data.filename), value);
  await writeFile(data.filename, data.raw);
  assert.deepEqual(await readProgressSnapshotBytes(data.filename), data.raw);
});
test("traversal, unknown versions and invalid size types are rejected", async t => {
  const data = await setup(t);
  for (const change of [{ file: "../secret.gz" }, { bytes: true }, { bytes: 4 * 1024 ** 3 + 1 },
    { compressed_bytes: 100 * 1024 ** 2 }, { public_snapshot_format: "future" }]) {
    await writeFile(data.filename, JSON.stringify({ ...data.index, ...change }));
    await assert.rejects(readProgressSnapshot(data.filename));
  }
});
test("compressed and original byte hashes are both required", async t => {
  const data = await setup(t);
  await writeFile(data.filename, JSON.stringify({ ...data.index, sha256: "b".repeat(64) }));
  await assert.rejects(readProgressSnapshot(data.filename), /original bytes/);
  await writeFile(data.filename, JSON.stringify(data.index));
  const changed = Buffer.from(data.compressed);changed[changed.length - 1] ^= 1;
  await writeFile(path.join(data.dir, data.index.file), changed);
  await assert.rejects(readProgressSnapshot(data.filename), /compressed hash/);
});
test("index cannot upgrade original source or observation date", async t => {
  const data = await setup(t);
  for (const snapshot_identity of [{ ...data.index.snapshot_identity, generated_at: "new date" },
    { ...data.index.snapshot_identity, source_fingerprint: "b".repeat(64) }]) {
    await writeFile(data.filename, JSON.stringify({ ...data.index, snapshot_identity }));
    await assert.rejects(readProgressSnapshot(data.filename), /identity differs/);
  }
});
test("undersized gzip expansion limits are enforced", async t => {
  const data = await setup(t);
  await writeFile(data.filename, JSON.stringify({ ...data.index, bytes: 1 }));
  await assert.rejects(readProgressSnapshot(data.filename));
});
test("payload symlinks are not followed", async t => {
  const data = await setup(t);const sibling = path.join(data.dir, data.index.file);
  await rm(sibling);const other = path.join(data.dir, "other.gz");
  await writeFile(other, data.compressed);await symlink(other, sibling);
  await assert.rejects(readProgressSnapshot(data.filename), /escaped/);
});
test("a browser projection cannot claim to be the complete snapshot", async t => {
  const data = await setup(t);
  const raw = Buffer.from(JSON.stringify({ ...value, deferred_evidence: {} }));
  const compressed = gzipSync(raw);
  const index = { ...data.index, bytes: raw.length, sha256: sha(raw), compressed_bytes: compressed.length,
    compressed_sha256: sha(compressed), file: "manifest-" + sha(compressed) + ".json.gz" };
  await writeFile(data.filename, JSON.stringify(index));
  await writeFile(path.join(data.dir, index.file), compressed);
  await assert.rejects(readProgressSnapshot(data.filename), /identity differs/);
});

async function wrapped(t) {
  const data=await setup(t);
  const inner={byte_view_format:"quantumbridge.json-byte-views.v2",encoding:"gzip-byte-spans",
    kind:"full_snapshot",bytes:data.raw.length,sha256:sha(data.raw),snapshot_identity:data.index.snapshot_identity,
    sources:[{file:data.index.file,bytes:data.raw.length,sha256:sha(data.raw),
      compressed_bytes:data.compressed.length,compressed_sha256:sha(data.compressed)}],
    pieces:[[0,0,data.raw.length]],public_snapshot_format:"quantumbridge.public-snapshot-byte-views.v2",
    download:{file:"manifest.json.gz",bytes:data.compressed.length,sha256:sha(data.compressed)}};
  const body=Buffer.from(JSON.stringify(inner)+"\n"),compressed=gzipSync(body);
  const wrapper={public_snapshot_format:"quantumbridge.public-snapshot-index-gzip.v3",encoding:"gzip-index",
    file:"manifest-index-"+sha(compressed)+".json.gz",index_bytes:body.length,index_sha256:sha(body),
    index_compressed_bytes:compressed.length,index_compressed_sha256:sha(compressed),
    bytes:inner.bytes,sha256:inner.sha256,snapshot_identity:inner.snapshot_identity,download:inner.download};
  await writeFile(path.join(data.dir,wrapper.file),compressed);
  await writeFile(path.join(data.dir,"manifest.json.gz"),data.compressed);
  await writeFile(data.filename,JSON.stringify(wrapper));
  return {...data,inner,wrapper,indexBody:body,indexCompressed:compressed};
}

test("compressed indexes preserve every original byte, unknown field and failed case",async t=>{
  const data=await wrapped(t);
  assert.deepEqual(await readProgressSnapshotBytes(data.filename),data.raw);
  assert.deepEqual(await readProgressSnapshot(data.filename),value);
});

test("compressed indexes cannot alter bounds, paths, hashes, source or dates",async t=>{
  const data=await wrapped(t);
  for(const change of [{file:"../outside.gz"},{index_bytes:true},{index_compressed_bytes:true},
    {index_bytes:16*1024**2+1},{index_compressed_bytes:16*1024**2+1},{index_bytes:1},
    {index_sha256:"b".repeat(64)},{sha256:"b".repeat(64)},
    {snapshot_identity:{...data.wrapper.snapshot_identity,generated_at:"forged"}},
    {snapshot_identity:{...data.wrapper.snapshot_identity,source_fingerprint:"b".repeat(64)}},
    {download:{...data.wrapper.download,sha256:"b".repeat(64)}},{extra:"x".repeat(4096)}]){
    await writeFile(data.filename,JSON.stringify({...data.wrapper,...change}));
    await assert.rejects(readProgressSnapshotBytes(data.filename));
  }
});

test("compressed index payloads must match both hashes and cannot be symlinks",async t=>{
  const data=await wrapped(t),target=path.join(data.dir,data.wrapper.file);
  const bad=Buffer.from(data.indexCompressed);bad[bad.length-1]^=1;
  await writeFile(target,bad);
  await assert.rejects(readProgressSnapshotBytes(data.filename),/hash differs/);
  await rm(target);const other=path.join(data.dir,"other-index.gz");
  await writeFile(other,data.indexCompressed);await symlink(other,target);
  await assert.rejects(readProgressSnapshotBytes(data.filename),/escaped/);
});

test("a compressed index cannot recursively wrap another index",async t=>{
  const data=await wrapped(t);
  const body=Buffer.from(JSON.stringify(data.wrapper)),compressed=gzipSync(body);
  const wrapper={...data.wrapper,index_bytes:body.length,index_sha256:sha(body),
    index_compressed_bytes:compressed.length,index_compressed_sha256:sha(compressed),
    file:"manifest-index-"+sha(compressed)+".json.gz"};
  await writeFile(path.join(data.dir,wrapper.file),compressed);
  await writeFile(data.filename,JSON.stringify(wrapper));
  await assert.rejects(readProgressSnapshotBytes(data.filename),/identity differs/);
});
