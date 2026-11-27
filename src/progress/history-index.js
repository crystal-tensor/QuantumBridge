import { inflateBounded, verifiedBytes } from "./transport.js?http=history-index-20261126";

export const historyIndexFormat = "quantumbridge.engineering-history-index-gzip.v1";
export const historyIndexSpanFormat = "quantumbridge.engineering-history-index-spans.v2";
export const historyIndexLimit = 16 * 1024 ** 2;
const hash = value => typeof value === "string" && /^[0-9a-f]{64}$/.test(value);
const size = value => Number.isSafeInteger(value) && value > 0 && value <= historyIndexLimit;
const digest = async bytes => [...new Uint8Array(await crypto.subtle.digest("SHA-256", bytes))]
  .map(value => value.toString(16).padStart(2, "0")).join("");

export function historyIndexReference(value) {
  if (!value || Array.isArray(value) ||
      value.original_file !== "history.json" || !size(value.bytes) || !hash(value.sha256) ||
      value.replayIsNotNewVerification !== true || value.newFunctionAcceptances !== 0) return null;
  if (value.format === historyIndexFormat && value.encoding === "gzip-bytes" &&
      size(value.compressed_bytes) && hash(value.compressed_sha256) &&
      value.file === `history-index-${value.compressed_sha256}.json.gz`) return value;
  if (value.format !== historyIndexSpanFormat || value.encoding !== "gzip-byte-spans" ||
      !Array.isArray(value.sources) || value.sources.length < 1 || value.sources.length > 512 ||
      !Array.isArray(value.pieces) || value.pieces.length < 1 || value.pieces.length > 1024) return null;
  const names = new Set(), used = new Set();
  let sourceBytes = 0, total = 0;
  for (const source of value.sources) {
    if (!source || typeof source !== "object" || Array.isArray(source) ||
        !size(source.bytes) || !hash(source.sha256) || !size(source.compressed_bytes) ||
        !hash(source.compressed_sha256) || names.has(source.file) ||
        ![`history-index-${source.compressed_sha256}.json.gz`,
          `history-span-${source.compressed_sha256}.bin.gz`].includes(source.file)) return null;
    names.add(source.file); sourceBytes += source.bytes;
    if (sourceBytes > historyIndexLimit) return null;
  }
  for (const piece of value.pieces) {
    if (!Array.isArray(piece) || piece.length !== 3 ||
        !Number.isSafeInteger(piece[0]) || piece[0] < 0 || piece[0] >= value.sources.length ||
        !Number.isSafeInteger(piece[1]) || piece[1] < 0 || !size(piece[2]) ||
        piece[1] + piece[2] > value.sources[piece[0]].bytes) return null;
    used.add(piece[0]); total += piece[2];
    if (total > value.bytes) return null;
  }
  return total === value.bytes && used.size === value.sources.length ? value : null;
}

export async function decodeHistoryIndexBytes(value, loadCompressed) {
  const item = historyIndexReference(value);
  if (!item || item.format !== historyIndexSpanFormat) throw new Error("Invalid historical span transport");
  const sources = [];
  for (const source of item.sources) {
    const compressed = await loadCompressed(source);
    if (!(compressed instanceof Uint8Array) || compressed.length !== source.compressed_bytes ||
        await digest(compressed) !== source.compressed_sha256) throw new Error("Historical source compressed bytes/hash differ");
    const raw = await inflateBounded(compressed, source.bytes);
    if (raw.length !== source.bytes || await digest(raw) !== source.sha256)
      throw new Error("Historical source original bytes/hash differ");
    sources.push(raw);
  }
  const raw = new Uint8Array(item.bytes);
  let offset = 0;
  for (const [number, start, length] of item.pieces) {
    raw.set(sources[number].subarray(start, start + length), offset);
    offset += length;
  }
  if (await digest(raw) !== item.sha256) throw new Error("Original historical index bytes/hash differ");
  return raw;
}

function legacyReference(value) {
  if (!value || value.format !== historyIndexFormat || value.encoding !== "gzip-bytes" ||
      !size(value.compressed_bytes) || !hash(value.compressed_sha256) ||
      value.file !== `history-index-${value.compressed_sha256}.json.gz`) return null;
  return value;
}

export async function historyIndexBytes(url, value, options) {
  const item = historyIndexReference(value);
  if (!item) throw new Error("Invalid historical index transport");
  if (item.format === historyIndexSpanFormat)
    return decodeHistoryIndexBytes(item, source => verifiedBytes(new URL(source.file, url),
      {bytes: source.compressed_bytes, sha256: source.compressed_sha256}, options));
  if (!legacyReference(item)) throw new Error("Invalid historical index transport");
  const compressed = await verifiedBytes(new URL(item.file, url),
    { bytes: item.compressed_bytes, sha256: item.compressed_sha256 }, options);
  const raw = await inflateBounded(compressed, item.bytes);
  if (raw.length !== item.bytes || await digest(raw) !== item.sha256) {
    throw new Error("Original historical index bytes/hash differ");
  }
  return raw;
}

export async function restoreHistoryIndex(value, url, options) {
  if (Array.isArray(value)) return value;
  const raw = await historyIndexBytes(url, value, options);
  const result = JSON.parse(new TextDecoder("utf-8", { fatal: true }).decode(raw));
  if (!Array.isArray(result)) throw new Error("Historical index must retain its original array");
  return result;
}
