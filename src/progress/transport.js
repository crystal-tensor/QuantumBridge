import { validDeferredManifestFields } from "./model.js?manifest=delivery-20261123";
import { parseStructuredJSON } from "./structured-json.js?observer=relative-20261127";

const CHUNK_BYTES = 1024 * 1024;
const CONCURRENCY = 8;
const DEFAULT_CONCURRENCY = 2;
const REQUEST_TIMEOUT_MS = 60000;
const MAX_ORIGINAL = 4 * 1024 ** 3;
const digest = async bytes => [...new Uint8Array(await crypto.subtle.digest("SHA-256", bytes))].map(value => value.toString(16).padStart(2, "0")).join("");
const positiveSize = (value, limit) => Number.isSafeInteger(value) && value > 0 && value <= limit;

export async function inflateBounded(bytes, limit) {
  const reader = new Blob([bytes]).stream().pipeThrough(new DecompressionStream("gzip")).getReader();
  const chunks = [];
  let length = 0;
  try {
    for (;;) {
      const { value, done } = await reader.read();
      if (done) break;
      length += value.length;
      if (length > limit) throw new Error("Evidence expansion exceeds its bound");
      chunks.push(value);
    }
  } catch (error) {
    await reader.cancel().catch(() => {});
    throw error;
  } finally { reader.releaseLock(); }
  const raw = new Uint8Array(length);
  let offset = 0;
  for (const chunk of chunks) { raw.set(chunk, offset); offset += chunk.length; }
  return raw;
}

function evidenceReference(value) {
  if (value?.schema !== 2 || value.encoding !== "deferred-manifest-snapshot-v2" ||
      typeof value.generated_at !== "string" || !value.generated_at || !/^[0-9a-f]{64}$/.test(value.source_fingerprint || "") ||
      !validDeferredManifestFields(value.fields) || value.snapshot?.file !== "manifest.json.gz" ||
      !positiveSize(value.snapshot.bytes, 100 * 1024 ** 2 - 1) || !positiveSize(value.snapshot.original_bytes, MAX_ORIGINAL) ||
      !/^[0-9a-f]{64}$/.test(value.snapshot.sha256 || "") || !/^[0-9a-f]{64}$/.test(value.snapshot.original_sha256 || "")) {
    throw new Error("Invalid deferred snapshot reference");
  }
  return value.snapshot;
}

export async function verifiedEvidence(url, descriptor, options) {
  const payload = await verifiedJSON(url, descriptor, options);
  if (payload?.schema === 1 && payload.encoding === "deferred-manifest-v1") return payload;
  const snapshot = evidenceReference(payload);
  const compressed = await verifiedBytes(new URL(snapshot.file, url), snapshot, options);
  const raw = await inflateBounded(compressed, snapshot.original_bytes);
  if (raw.length !== snapshot.original_bytes || await digest(raw) !== snapshot.original_sha256) {
    throw new Error("Deferred snapshot original bytes/hash differ");
  }
  const value = await parseStructuredJSON(raw, snapshot.json_structure);
  if (!value || Array.isArray(value) || Object.hasOwn(value, "public_snapshot_format") ||
      Object.hasOwn(value, "byte_view_format") || Object.hasOwn(value, "deferred_evidence") ||
      value.generated_at !== payload.generated_at || value.source?.fingerprint !== payload.source_fingerprint ||
      payload.fields.some(name => !Object.hasOwn(value, name))) throw new Error("Deferred snapshot identity differs");
  return { schema: 1, encoding: "deferred-manifest-v1", generated_at: value.generated_at,
    source_fingerprint: value.source.fingerprint, fields: Object.fromEntries(payload.fields.map(name => [name, value[name]])) };
}

function byteLength(value) {
  return /^\d+$/.test(value || "") && Number.isSafeInteger(Number(value)) && Number(value) > 0 ? Number(value) : null;
}

async function transferBytes(fetcher, target, options, validate) {
  for (let attempt = 0; attempt < 3; attempt++) {
    const signal = options.signal ? AbortSignal.any([options.signal, AbortSignal.timeout(REQUEST_TIMEOUT_MS)]) : AbortSignal.timeout(REQUEST_TIMEOUT_MS);
    try {
      const response = await fetcher(target, { ...options, signal });
      validate(response);
      return new Uint8Array(await response.arrayBuffer());
    } catch (error) {
      const networkFailure = error instanceof TypeError || ["TimeoutError", "AbortError"].includes(error.name);
      if (options.signal?.aborted || !networkFailure || attempt === 2) throw error;
      await new Promise(resolve => setTimeout(resolve, 250 * (attempt + 1)));
    }
  }
}

export async function verifiedBytes(url, descriptor, { fetcher = globalThis.fetch, chunkBytes = CHUNK_BYTES, concurrency = DEFAULT_CONCURRENCY } = {}) {
  if (!/^[0-9a-f]{64}$/.test(descriptor.sha256 || "")) throw new Error("Missing artifact SHA-256");
  if (!Number.isSafeInteger(chunkBytes) || chunkBytes < 1 || !Number.isSafeInteger(concurrency) || concurrency < 1 || concurrency > CONCURRENCY) throw new Error("Invalid transfer bounds");
  const target = new URL(url);
  target.searchParams.set("sha256", descriptor.sha256);
  const options = { cache: "no-cache" };
  let size = descriptor.bytes ?? null;
  if (size !== null && (!Number.isSafeInteger(size) || size < 1)) throw new Error("Invalid artifact size");
  let ranged = false;
  try {
    const head = await fetcher(target, { ...options, method: "HEAD", signal: AbortSignal.timeout(REQUEST_TIMEOUT_MS) });
    if (head.ok && (!head.headers.get("content-encoding") || head.headers.get("content-encoding").toLowerCase() === "identity")) {
      const observed = byteLength(head.headers.get("content-length"));
      if (size !== null && observed !== null && size !== observed) throw new Error("Artifact size mismatch");
      size ??= observed;
      ranged = head.headers.get("accept-ranges") === "bytes";
    }
  } catch (error) {
    if (error.message === "Artifact size mismatch") throw error;
  }
  let bytes;
  if (ranged && size > chunkBytes) {
    const controller = new AbortController();
    const chunks = new Array(Math.ceil(size / chunkBytes));
    let cursor = 0;
    async function worker() {
      while (cursor < chunks.length) {
        const index = cursor++, start = index * chunkBytes, end = Math.min(size - 1, start + chunkBytes - 1);
        const chunk = await transferBytes(fetcher, target, { ...options, signal: controller.signal, headers: { Range: `bytes=${start}-${end}` } }, response => {
          if (response.status !== 206 || response.headers.get("content-range") !== `bytes ${start}-${end}/${size}`) throw new Error("Invalid artifact range response");
        });
        if (chunk.byteLength !== end - start + 1) throw new Error("Incomplete artifact range");
        chunks[index] = chunk;
      }
    }
    const workers = Array.from({ length: Math.min(concurrency, chunks.length) }, () => worker());
    try { await Promise.all(workers); }
    catch (error) { controller.abort(); await Promise.allSettled(workers); throw error; }
    bytes = new Uint8Array(size);
    chunks.forEach((chunk, index) => bytes.set(chunk, index * chunkBytes));
  } else {
    bytes = await transferBytes(fetcher, target, options, response => {
      if (!response.ok) throw new Error(`Artifact HTTP ${response.status}`);
    });
    if (size !== null && bytes.byteLength !== size) throw new Error("Artifact size mismatch");
  }
  const hash = await digest(bytes);
  if (hash !== descriptor.sha256) throw new Error("Artifact integrity mismatch");
  return bytes;
}

export async function verifiedJSON(url, descriptor, options) {
  const bytes = await verifiedBytes(url, descriptor, options);
  const stream = new Blob([bytes]).stream().pipeThrough(new DecompressionStream("gzip"));
  return new Response(stream).json();
}
