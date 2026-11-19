// Reconstruct original JSON bytes, never project or refresh their identity.
import { createHash } from "node:crypto";
import { gunzipSync } from "node:zlib";

export const byteViewFormat = "quantumbridge.json-byte-views.v2";
export const byteViewIndexLimit = 16 * 1024 ** 2;
const originalLimit = 4 * 1024 ** 3;
const compressedLimit = 100 * 1024 ** 2 - 1;
const sha = value => createHash("sha256").update(value).digest("hex");
const hash = value => typeof value === "string" && /^[0-9a-f]{64}$/.test(value);
const size = (value, limit, zero = false) => Number.isSafeInteger(value) && value >= (zero ? 0 : 1) && value <= limit;
const object = value => value !== null && typeof value === "object" && !Array.isArray(value);
const filename = value => typeof value === "string" && /^(?:manifest-[0-9a-f]{64}\.json\.gz|json-piece-[0-9a-f]{64}\.bin\.gz|(?:native|target|runtime|runtime-browser|manifest-evidence|runtime-details-[0-9a-f]{2}|identity-groups-(?:main|alternate)|namespaces-(?:main|alternate))\.json\.gz)$/.test(value);

export async function readJSONByteViews(index, loadCompressed) {
  if (!object(index) || index.byte_view_format !== byteViewFormat || index.encoding !== "gzip-byte-spans" ||
      !size(index.bytes, originalLimit) || !hash(index.sha256) || !Array.isArray(index.sources) ||
      index.sources.length < 1 || index.sources.length > 4096 || !Array.isArray(index.pieces) ||
      index.pieces.length < 1 || index.pieces.length > 500000) throw new Error("Invalid byte-view index");
  const names = new Set();
  let sourceBytes = 0;
  for (const source of index.sources) {
    if (!object(source) || !filename(source.file) || !size(source.bytes, originalLimit) ||
        !size(source.compressed_bytes, compressedLimit) || !hash(source.sha256) || !hash(source.compressed_sha256) ||
        names.has(source.file)) throw new Error("Invalid byte-view source identity or bounds");
    if (/^(manifest-|json-piece-)/.test(source.file) && !source.file.includes(source.compressed_sha256)) {
      throw new Error("Content-addressed source filename differs");
    }
    names.add(source.file);
    sourceBytes += source.bytes;
    if (sourceBytes > originalLimit) throw new Error("Cumulative source bytes exceed their bound");
  }
  const used = new Set();
  let total = 0;
  for (const piece of index.pieces) {
    if (!Array.isArray(piece) || piece.length !== 3 || !size(piece[0], index.sources.length - 1, true) ||
        !size(piece[1], index.sources[piece[0]].bytes, true) || !size(piece[2], index.sources[piece[0]].bytes) ||
        piece[1] + piece[2] > index.sources[piece[0]].bytes) throw new Error("Invalid byte-view piece bounds");
    total += piece[2];
    used.add(piece[0]);
    if (total > index.bytes) throw new Error("Byte-view coverage exceeds original size");
  }
  if (total !== index.bytes || used.size !== index.sources.length) throw new Error("Byte-view coverage differs");
  const buffers = [];
  for (const source of index.sources) {
    const compressed = await loadCompressed(source);
    if (compressed.length !== source.compressed_bytes || sha(compressed) !== source.compressed_sha256) {
      throw new Error("Source compressed bytes/hash differ");
    }
    const raw = gunzipSync(compressed, { maxOutputLength: source.bytes + 1 });
    if (raw.length !== source.bytes || sha(raw) !== source.sha256) throw new Error("Source original bytes/hash differ");
    buffers.push(raw);
  }
  const raw = Buffer.allocUnsafe(index.bytes);
  let offset = 0;
  for (const [number, start, length] of index.pieces) {
    buffers[number].copy(raw, offset, start, start + length);
    offset += length;
  }
  if (sha(raw) !== index.sha256) throw new Error("Reconstructed original byte hash differs");
  const value = JSON.parse(raw);
  if (object(value) && Object.hasOwn(value, "byte_view_format")) throw new Error("Nested byte-view indexes are not original JSON");
  if (index.kind === "full_snapshot") {
    if (!object(value) || Object.hasOwn(value, "public_snapshot_format") || Object.hasOwn(value, "deferred_evidence") ||
        typeof value.generated_at !== "string" || !value.generated_at || !hash(value.source?.fingerprint) ||
        value.generated_at !== index.snapshot_identity?.generated_at ||
        value.source.fingerprint !== index.snapshot_identity?.source_fingerprint) throw new Error("Reconstructed snapshot identity differs");
  } else if (index.kind !== "json_document" || index.snapshot_identity !== null) {
    throw new Error("Unknown byte-view document kind or identity");
  }
  return raw;
}
