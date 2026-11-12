import assert from "node:assert/strict";
import test from "node:test";
import { createHash } from "node:crypto";
import { gzipSync } from "node:zlib";
import { verifiedBytes, verifiedJSON } from "../src/progress/transport.js";

const sha = bytes => createHash("sha256").update(bytes).digest("hex");
const source = Buffer.from("0123456789abcdefghijklmnopqrstuvwxyz");
const descriptor = { sha256: sha(source), bytes: source.length };
function fixture({ bytes = source, headStatus = 200, range = true, headSize = bytes.length, headThrows = false, corrupt = false, status = 200, delay = false, badHeader = false, short = false, rangeStatus = 206 } = {}) {
  const calls = [], state = { active: 0, maximum: 0, aborted: 0 };
  const fetcher = async (url, options) => {
    calls.push({ url: String(url), ...options });
    if (options.method === "HEAD") {
      if (headThrows) throw new Error("HEAD unavailable");
      return new Response(null, { status: headStatus, headers: { ...(headSize == null ? {} : { "content-length": String(headSize) }), ...(range ? { "accept-ranges": "bytes" } : {}) } });
    }
    if (!options.headers?.Range) return new Response(bytes, { status });
    const [, begin, finish] = options.headers.Range.match(/^bytes=(\d+)-(\d+)$/);
    const start = Number(begin), end = Number(finish);
    state.active++; state.maximum = Math.max(state.maximum, state.active);
    try {
      if (delay && start !== 0) await new Promise((resolve, reject) => {
        const timer = setTimeout(() => { options.signal.removeEventListener("abort", abort); resolve(); }, 10);
        function abort() { clearTimeout(timer); state.aborted++; reject(new Error("Aborted")); }
        options.signal.addEventListener("abort", abort, { once: true });
      });
      const chunk = Buffer.from(bytes.subarray(start, end + 1));
      if (corrupt && start === 0) chunk[0] ^= 1;
      return new Response(short ? chunk.subarray(1) : chunk, { status: rangeStatus, headers: { "content-range": badHeader ? "bytes 0-1/2" : `bytes ${start}-${end}/${bytes.length}` } });
    } finally { state.active--; }
  };
  return { fetcher, calls, state };
}

test("bounded parallel ranges reconstruct every byte and bind all requests to the expected hash", async () => {
  const env = fixture({ delay: true });
  const result = await verifiedBytes("https://example.test/data.json.gz", descriptor, { ...env, chunkBytes: 3, concurrency: 3 });
  assert.deepEqual(Buffer.from(result), source);
  assert.ok(env.state.maximum > 1 && env.state.maximum <= 3);
  assert.equal(env.state.active, 0);
  const ranges = env.calls.filter(row => row.headers?.Range);
  assert.equal(ranges.length, 12);
  assert.equal(new Set(ranges.map(row => row.headers.Range)).size, 12);
  assert.ok(env.calls.every(row => new URL(row.url).searchParams.get("sha256") === descriptor.sha256));
});

for (const options of [{ range: false }, { headStatus: 405 }, { headThrows: true }, { headSize: null, range: false }]) {
  test(`a server without usable range metadata still requires complete verified bytes ${JSON.stringify(options)}`, async () => {
    const env = fixture(options);
    assert.deepEqual(Buffer.from(await verifiedBytes("https://example.test/data", { sha256: descriptor.sha256 }, { ...env, chunkBytes: 3 })), source);
    assert.equal(env.calls.filter(row => row.headers?.Range).length, 0);
    assert.equal(env.calls.length, 2);
  });
}
test("small artifacts use one body request even when ranges are supported", async () => {
  const env = fixture();
  await verifiedBytes("https://example.test/data", descriptor, { ...env, chunkBytes: source.length });
  assert.equal(env.calls.length, 2);
  assert.equal(env.calls.filter(row => row.headers?.Range).length, 0);
});
for (const [options, message] of [
  [{ headSize: 1 }, /size mismatch/], [{ corrupt: true }, /integrity mismatch/],
  [{ badHeader: true }, /range response/], [{ short: true }, /Incomplete artifact range/],
  [{ rangeStatus: 200 }, /range response/], [{ range: false, status: 503 }, /HTTP 503/],
]) {
  test(`corrupt or incomplete transport cannot become evidence ${JSON.stringify(options)}`, async () => {
    const env = fixture(options);
    await assert.rejects(verifiedBytes("https://example.test/data", descriptor, { ...env, chunkBytes: 3 }), message);
  });
}
test("a failed range aborts and joins every outstanding worker", async () => {
  const env = fixture({ badHeader: true, delay: true });
  await assert.rejects(verifiedBytes("https://example.test/data", descriptor, { ...env, chunkBytes: 3 }), /range response/);
  assert.ok(env.state.aborted > 0);
  assert.equal(env.state.active, 0);
});
test("plain transfers cannot bypass declared byte count or checksum", async () => {
  await assert.rejects(verifiedBytes("https://example.test/data", { ...descriptor, bytes: source.length + 1 }, fixture({ range: false, headSize: null })), /size mismatch/);
  await assert.rejects(verifiedBytes("https://example.test/data", { ...descriptor, sha256: "0".repeat(64) }, fixture({ range: false })), /integrity mismatch/);
});
test("invalid transfer bounds and missing identities fail before a request", async () => {
  const env = fixture();
  for (const options of [{ chunkBytes: 0 }, { concurrency: 0 }, { concurrency: 9 }, { chunkBytes: 1.5 }]) {
    await assert.rejects(verifiedBytes("https://example.test/data", descriptor, { ...env, ...options }), /transfer bounds/);
  }
  await assert.rejects(verifiedBytes("https://example.test/data", {}, env), /SHA-256/);
  await assert.rejects(verifiedBytes("https://example.test/data", { ...descriptor, bytes: 0 }, env), /artifact size/);
  assert.equal(env.calls.length, 0);
});
test("gzip JSON is decoded only after the complete artifact hash passes", async () => {
  const value = { failed: ["case"], accepted: false }, bytes = gzipSync(JSON.stringify(value));
  const env = fixture({ bytes });
  assert.deepEqual(await verifiedJSON("https://example.test/data.gz", { sha256: sha(bytes), bytes: bytes.length }, env), value);
  await assert.rejects(verifiedJSON("https://example.test/bad.gz", descriptor, fixture()));
});
