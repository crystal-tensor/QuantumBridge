import assert from "node:assert/strict";
import test from "node:test";
import { createHash } from "node:crypto";
import { gzipSync } from "node:zlib";
import { verifiedEvidence } from "../src/progress/transport.js";
import { restoreManifest, deferredManifestFields } from "../src/progress/model.js";

const sha = value => createHash("sha256").update(value).digest("hex");
const value = { generated_at: "2026-11-17T00:00:00Z", source: { fingerprint: "a".repeat(64) },
  verification: [{ id: "original failed id", status: "failed", exit: -11, date: "original" }],
  test_contexts: { original: ["unchanged"] }, runtime_census: [], goal_execution: { goal_complete: false },
  strict_backlog: [{ id: "still failed" }], diagnostic_observations: [{ accepted: false }], tests: [],
  unknown: { keep: ["中文", false, 2] } };
function fixture(change = () => {}, raw = Buffer.from(JSON.stringify(value, null, 2))) {
  const compressed = gzipSync(raw);
  const index = { schema: 2, encoding: "deferred-manifest-snapshot-v2", generated_at: value.generated_at,
    source_fingerprint: value.source.fingerprint, fields: deferredManifestFields.slice(),
    snapshot: { file: "manifest.json.gz", bytes: compressed.length, sha256: sha(compressed),
      original_bytes: raw.length, original_sha256: sha(raw) } };
  change(index);
  const body = gzipSync(JSON.stringify(index));
  const descriptor = { file: "manifest-evidence.json.gz", bytes: body.length, sha256: sha(body), fields: index.fields };
  const calls = [];
  const options = { fetcher: async (url, request) => {
    calls.push(new URL(url).pathname);
    const bytes = new URL(url).pathname.endsWith("/manifest-evidence.json.gz") ? body : compressed;
    return new Response(request.method === "HEAD" ? null : bytes, { headers: { "content-length": String(bytes.length) } });
  } };
  return { index, body, compressed, descriptor, options, calls };
}
const read = row => verifiedEvidence("https://example.test/data/manifest-evidence.json.gz", row.descriptor, row.options);

test("the bounded snapshot reference restores all failures and unknown bootstrap fields without restamping", async () => {
  const row = fixture(), before = JSON.stringify(row.index);
  const payload = await read(row);
  const bootstrap = Object.fromEntries(Object.entries(value).filter(([name]) => !deferredManifestFields.includes(name)));
  bootstrap.deferred_evidence = row.descriptor;
  bootstrap.strict_backlog_count = 1;
  assert.deepEqual(restoreManifest(bootstrap, payload), value);
  assert.equal(JSON.stringify(row.index), before);
  assert.ok(row.calls.every(url => ["/data/manifest-evidence.json.gz", "/data/manifest.json.gz"].includes(url)));
});
test("legacy evidence remains readable without an additional source request", async () => {
  const fields = Object.fromEntries(deferredManifestFields.map(name => [name, value[name]]));
  const payload = { schema: 1, encoding: "deferred-manifest-v1", generated_at: value.generated_at,
    source_fingerprint: value.source.fingerprint, fields };
  const bytes = gzipSync(JSON.stringify(payload));
  assert.deepEqual(await verifiedEvidence("https://example.test/legacy.gz", { bytes: bytes.length, sha256: sha(bytes) },
    { fetcher: async (_, options) => new Response(options.method === "HEAD" ? null : bytes, { headers: { "content-length": String(bytes.length) } }) }), payload);
});
test("migration tables can be deferred without changing complete snapshot identity",async()=>{
  const complete={...value,verification_migration_pool:{schema:1,encoding:"approved-test-migrations-pool-v1",contexts:{}}};
  const fields=[...deferredManifestFields,"verification_migration_pool"];
  const row=fixture(index=>{index.fields=fields;},Buffer.from(JSON.stringify(complete)));
  const payload=await read(row);
  const bootstrap=Object.fromEntries(Object.entries(complete).filter(([name])=>!fields.includes(name)));
  bootstrap.deferred_evidence=row.descriptor;
  bootstrap.strict_backlog_count=1;
  assert.deepEqual(restoreManifest(bootstrap,payload),complete);
  bootstrap.verification_migration_pool={};
  assert.throws(()=>restoreManifest(bootstrap,payload),/does not match/);
});
for (const [label, change] of [
  ["path traversal", x => { x.snapshot.file = "../manifest.json.gz"; }],
  ["absolute URL", x => { x.snapshot.file = "https://evil.test/manifest.json.gz"; }],
  ["reordered fields", x => { x.fields.reverse(); }],
  ["missing field", x => { x.fields.pop(); }],
  ["duplicate field", x => { x.fields[0] = x.fields[1]; }],
  ["unknown format", x => { x.encoding = "future"; }],
  ["Boolean size", x => { x.snapshot.original_bytes = true; }],
  ["oversized original", x => { x.snapshot.original_bytes = 4 * 1024 ** 3 + 1; }],
  ["oversized gzip", x => { x.snapshot.bytes = 100 * 1024 ** 2; }],
]) test(`${label} is rejected before any snapshot request`, async () => {
  const row = fixture(change);
  await assert.rejects(read(row), /Invalid deferred snapshot/);
  assert.ok(row.calls.every(url => url.endsWith("/manifest-evidence.json.gz")));
});
for (const [label, change, error] of [
  ["compressed hash", x => { x.snapshot.sha256 = "b".repeat(64); }, /integrity mismatch/],
  ["original hash", x => { x.snapshot.original_sha256 = "b".repeat(64); }, /original bytes\/hash/],
  ["compressed size", x => { x.snapshot.bytes++; }, /size mismatch/],
  ["truncated bound", x => { x.snapshot.original_bytes--; }, /expansion/],
  ["long original size", x => { x.snapshot.original_bytes++; }, /original bytes\/hash/],
  ["forged date", x => { x.generated_at = "new date"; }, /identity differs/],
  ["forged source", x => { x.source_fingerprint = "b".repeat(64); }, /identity differs/],
]) test(`${label} cannot upgrade the original evidence identity`, async () => {
  await assert.rejects(read(fixture(change)), error);
});
test("a projection or archive index cannot stand in for a complete snapshot", async () => {
  for (const altered of [{ ...value, deferred_evidence: {} }, { ...value, public_snapshot_format: "v1" },
    { ...value, byte_view_format: "v2" }, { ...value, verification: undefined }]) {
    await assert.rejects(read(fixture(() => {}, Buffer.from(JSON.stringify(altered)))), /identity differs/);
  }
});
test("reordered JSON bytes cannot bypass the original-byte hash", async () => {
  const row = fixture(x => { x.snapshot.original_sha256 = sha(Buffer.from(JSON.stringify(value))); });
  await assert.rejects(read(row), /original bytes\/hash/);
});
