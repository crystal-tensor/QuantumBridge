import assert from "node:assert/strict";
import test from "node:test";
import { mkdtemp, writeFile, readFile, rm, symlink } from "node:fs/promises";
import { tmpdir } from "node:os";
import path from "node:path";
import { gzipSync } from "node:zlib";
import { createHash } from "node:crypto";
import { readProgressSnapshotBytes } from "./read-progress-snapshot.mjs";
import { readJSONByteViews } from "./read-json-byte-views.mjs";

const sha = value => createHash("sha256").update(value).digest("hex");
async function setup(t, value) {
  const directory = await mkdtemp(path.join(tmpdir(), "qb-byte-views-"));
  t.after(() => rm(directory, { recursive: true, force: true }));
  value ??= { generated_at: "original date", source: { fingerprint: "a".repeat(64) },
    observations: [{ id: "same id", exit: 1, status: "failed" }, { id: "same id", exit: 0, status: "passed" }],
    unknown: [false, null, "中文", { "escaped\"key": "\n\t" }] };
  const raw = Buffer.from(" \n" + JSON.stringify(value, null, 4) + "\n\n");
  const split = Math.floor(raw.length / 2);
  const sources = [];
  for (const bytes of [raw.subarray(0, split), raw.subarray(split)]) {
    const compressed = gzipSync(bytes);
    const file = "json-piece-" + sha(compressed) + ".bin.gz";
    await writeFile(path.join(directory, file), compressed);
    sources.push({ file, bytes: bytes.length, sha256: sha(bytes),
      compressed_bytes: compressed.length, compressed_sha256: sha(compressed) });
  }
  const index = { public_snapshot_format: "quantumbridge.public-snapshot-byte-views.v2",
    byte_view_format: "quantumbridge.json-byte-views.v2", encoding: "gzip-byte-spans", kind: "full_snapshot",
    bytes: raw.length, sha256: sha(raw), sources, pieces: [[0, 0, split], [1, 0, raw.length - split]],
    snapshot_identity: { generated_at: value.generated_at, source_fingerprint: value.source.fingerprint } };
  const filename = path.join(directory, "manifest.json");
  await writeFile(filename, JSON.stringify(index));
  return { directory, filename, raw, index };
}

test("byte views restore exact original bytes, dates and duplicate failure IDs", async t => {
  const data = await setup(t);
  assert.deepEqual(await readProgressSnapshotBytes(data.filename), data.raw);
  const value = JSON.parse(await readProgressSnapshotBytes(data.filename));
  assert.equal(value.observations[0].id, value.observations[1].id);
  assert.deepEqual(value.observations.map(row => row.exit), [1, 0]);
});

test("bounds, unknown formats and source identity aliases refuse before IO", async t => {
  const { index } = await setup(t);
  const mutations = [value => { value.byte_view_format = "future"; }, value => { value.bytes = true; },
    value => { value.bytes = 4 * 1024 ** 3 + 1; }, value => { value.sources[0].file = "../secret.gz"; },
    value => { value.sources[0].file = []; }, value => { value.sources.push({ ...value.sources[0] }); },
    value => { value.sources[0].compressed_bytes = 100 * 1024 ** 2; },
    value => { value.sources[0].bytes = true; }, value => { value.sources[0].compressed_sha256 = "0".repeat(64); },
    value => { value.pieces[0][0] = true; }, value => { value.pieces[0][1] = -1; },
    value => { value.pieces[0][2] = 0; }, value => { value.pieces[0][2] += 1; },
    value => { value.pieces = []; }];
  for (const mutate of mutations) {
    const changed = structuredClone(index);
    mutate(changed);
    await assert.rejects(readJSONByteViews(changed, () => { assert.fail("Invalid descriptor triggered IO"); }));
  }
});

test("both source hash layers and original complete hash are enforced", async t => {
  const data = await setup(t);
  for (const mutate of [value => { value.sources[0].sha256 = "0".repeat(64); },
    value => { value.sha256 = "0".repeat(64); }, value => { value.pieces.reverse(); }]) {
    const changed = structuredClone(data.index);
    mutate(changed);
    await writeFile(data.filename, JSON.stringify(changed));
    await assert.rejects(readProgressSnapshotBytes(data.filename), /hash differ/);
  }
  await writeFile(data.filename, JSON.stringify(data.index));
  const source = path.join(data.directory, data.index.sources[0].file);
  const compressed = await readFile(source);
  compressed[compressed.length - 1] ^= 1;
  await writeFile(source, compressed);
  await assert.rejects(readProgressSnapshotBytes(data.filename), /compressed bytes\/hash differ/);
});

test("neither an index nor a projection can stand in for the complete payload", async t => {
  for (const fields of [{ byte_view_format: "quantumbridge.json-byte-views.v2" },
    { deferred_evidence: {} }, { public_snapshot_format: "other" }]) {
    const data = await setup(t, { generated_at: "original date", source: { fingerprint: "a".repeat(64) }, ...fields });
    await assert.rejects(readProgressSnapshotBytes(data.filename));
  }
});

test("source and observation time cannot be refreshed by the index", async t => {
  const data = await setup(t);
  for (const fields of [{ generated_at: "new time" }, { source_fingerprint: "b".repeat(64) }]) {
    await writeFile(data.filename, JSON.stringify({ ...data.index,
      snapshot_identity: { ...data.index.snapshot_identity, ...fields } }));
    await assert.rejects(readProgressSnapshotBytes(data.filename), /identity differs/);
  }
});

test("truncated, missing and symlink pieces refuse", async t => {
  const data = await setup(t);
  const filename = path.join(data.directory, data.index.sources[0].file);
  const body = await readFile(filename);
  await writeFile(filename, body.subarray(0, body.length - 1));
  await assert.rejects(readProgressSnapshotBytes(data.filename), /size differs/);
  await rm(filename);
  await assert.rejects(readProgressSnapshotBytes(data.filename), /ENOENT/);
  const other = path.join(data.directory, "outside.gz");
  await writeFile(other, body);
  await symlink(other, filename);
  await assert.rejects(readProgressSnapshotBytes(data.filename), /escaped/);
});

test("expansion cannot exceed a declared source or total bound", async t => {
  const data = await setup(t);
  const changed = structuredClone(data.index);
  changed.sources[0].bytes = 1;
  changed.pieces = [[0, 0, 1], [1, 0, changed.sources[1].bytes]];
  changed.bytes = 1 + changed.sources[1].bytes;
  await writeFile(data.filename, JSON.stringify(changed));
  await assert.rejects(readProgressSnapshotBytes(data.filename));
});

test("generic JSON views cannot be mislabeled as full public snapshots", async t => {
  const data = await setup(t);
  const changed = { ...data.index, kind: "json_document", snapshot_identity: null };
  await writeFile(data.filename, JSON.stringify(changed));
  await assert.rejects(readProgressSnapshotBytes(data.filename), /Invalid snapshot byte views/);
  delete changed.public_snapshot_format;
  await writeFile(data.filename, JSON.stringify(changed));
  await assert.rejects(readProgressSnapshotBytes(data.filename), /explicit full/);
});
