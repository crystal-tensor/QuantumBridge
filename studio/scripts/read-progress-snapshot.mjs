// Read a legacy JSON snapshot or its verified, lossless gzip transport.
import { readFile, lstat, realpath } from "node:fs/promises";
import path from "node:path";
import { fileURLToPath } from "node:url";
import { createHash } from "node:crypto";
import { gunzipSync } from "node:zlib";
import { readJSONByteViews, byteViewIndexLimit } from "./read-json-byte-views.mjs";
import { restoreMigrationPool } from "../src/progress/migration-pool.js";

const format = "quantumbridge.public-snapshot-gzip.v1";
const indexFormat = "quantumbridge.public-snapshot-index-gzip.v3";
const originalLimit = 4 * 1024 ** 3;
const compressedLimit = 100 * 1024 ** 2 - 1;
const sha = value => createHash("sha256").update(value).digest("hex");
const size = (value, limit) => Number.isSafeInteger(value) && value > 0 && value <= limit;

export async function readProgressSnapshotBytes(source) {
  const filename = source instanceof URL ? fileURLToPath(source) : path.resolve(source);
  const sourceStat = await lstat(filename);
  if (sourceStat.isSymbolicLink() || (await lstat(path.dirname(filename))).isSymbolicLink()) throw new Error("Snapshot archive escaped its directory");
  if (sourceStat.size > originalLimit) throw new Error("Snapshot exceeds the read limit");
  let body = await readFile(filename);
  let index = JSON.parse(body);
  if (index?.public_snapshot_format === indexFormat) {
    if (body.length > 4096 || index.encoding !== "gzip-index" ||
        index.file !== path.basename(filename, path.extname(filename))+"-index-"+index.index_compressed_sha256+".json.gz" ||
        !size(index.index_bytes, byteViewIndexLimit) || !size(index.index_compressed_bytes, byteViewIndexLimit) ||
        !/^[0-9a-f]{64}$/.test(index.index_sha256 || "") || !/^[0-9a-f]{64}$/.test(index.index_compressed_sha256 || "")) {
      throw new Error("Invalid compressed snapshot index");
    }
    const sibling = path.join(path.dirname(filename), index.file);
    const stat = await lstat(sibling);
    if (stat.isSymbolicLink() || await realpath(path.dirname(sibling)) !== path.dirname(await realpath(filename)) ||
        stat.size !== index.index_compressed_bytes) throw new Error("Compressed snapshot index escaped or differs in size");
    const compressed = await readFile(sibling);
    if (sha(compressed) !== index.index_compressed_sha256) throw new Error("Compressed snapshot index hash differs");
    body = gunzipSync(compressed, {maxOutputLength:index.index_bytes+1});
    if (body.length !== index.index_bytes || sha(body) !== index.index_sha256) throw new Error("Snapshot index original bytes differ");
    const inner = JSON.parse(body);
    if (inner.public_snapshot_format !== "quantumbridge.public-snapshot-byte-views.v2" || inner.kind !== "full_snapshot" ||
        inner.bytes !== index.bytes || inner.sha256 !== index.sha256 ||
        inner.snapshot_identity?.generated_at !== index.snapshot_identity?.generated_at ||
        inner.snapshot_identity?.source_fingerprint !== index.snapshot_identity?.source_fingerprint ||
        ["file","bytes","sha256"].some(name=>inner.download?.[name] !== index.download?.[name])) {
      throw new Error("Compressed snapshot index identity differs");
    }
    index = inner;
  }
  if (index?.public_snapshot_format === "quantumbridge.public-snapshot-byte-views.v2") {
    if (body.length > byteViewIndexLimit || index.kind !== "full_snapshot") throw new Error("Invalid snapshot byte views");
    return readJSONByteViews(index, async source => {
      const sibling = path.join(path.dirname(filename), source.file);
      const stat = await lstat(sibling);
      if (stat.isSymbolicLink() || await realpath(path.dirname(sibling)) !== path.dirname(await realpath(filename))) {
        throw new Error("Snapshot archive escaped its directory");
      }
      if (stat.size !== source.compressed_bytes) throw new Error("Source compressed size differs");
      return readFile(sibling);
    });
  }
  if (index && Object.hasOwn(index, "byte_view_format")) throw new Error("Expected an explicit full public snapshot descriptor");
  if (!index || !Object.hasOwn(index, "public_snapshot_format")) return body;
  if (index.public_snapshot_format !== format || index.encoding !== "gzip" || index.file !== path.basename(filename, path.extname(filename)) + "-" + index.compressed_sha256 + ".json.gz" ||
      !size(index.bytes, originalLimit) || !size(index.compressed_bytes, compressedLimit) ||
      !/^[0-9a-f]{64}$/.test(index.sha256 || "") || !/^[0-9a-f]{64}$/.test(index.compressed_sha256 || "")) {
    throw new Error("Invalid snapshot archive descriptor");
  }
  const sibling = path.join(path.dirname(filename), index.file);
  const stat = await lstat(sibling);
  if (stat.isSymbolicLink() || await realpath(path.dirname(sibling)) !== path.dirname(await realpath(filename))) throw new Error("Snapshot archive escaped its directory");
  if (stat.size !== index.compressed_bytes) throw new Error("Snapshot compressed size differs");
  const compressed = await readFile(sibling);
  if (sha(compressed) !== index.compressed_sha256) throw new Error("Snapshot compressed hash differs");
  const raw = gunzipSync(compressed, { maxOutputLength: index.bytes + 1 });
  if (raw.length !== index.bytes || sha(raw) !== index.sha256) throw new Error("Snapshot original bytes differ");
  const value = JSON.parse(raw);
  if (Object.hasOwn(value, "public_snapshot_format") || Object.hasOwn(value, "deferred_evidence") || value.generated_at !== index.snapshot_identity?.generated_at ||
      value.source?.fingerprint !== index.snapshot_identity?.source_fingerprint) throw new Error("Snapshot identity differs");
  return raw;
}

export async function readProgressSnapshot(source) {
  return restoreMigrationPool(JSON.parse(await readProgressSnapshotBytes(source)));
}
